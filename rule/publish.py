"""Rule-version artifacts: in-band version binding, and the publication gate.

socaity-x8o §6: ``rule_version = hash(source + canonical params)``.  This
module builds that artifact and refuses -- loudly, and at three independent
points -- to build a PUBLISHABLE one out of the placeholder parameters
(:mod:`rule.params`), because socaity-x8o §7 makes a placeholder-free V a hard
precondition of ``epoch.opened(1)`` and therefore of the first external ledger
entry.

Development artifacts are still buildable: :func:`build_artifact` works with
placeholders so the tests, the golden vectors and the forkability job have
something to run against.  Only :func:`publish` -- the function whose output is
meant to become a ``rule.version_published`` payload -- applies the gate.

This module reads source files, so it is NOT part of the pure rule: the rule
function itself (``rule.distribute.distribute``) never touches the filesystem.
"""

import hashlib
import os

from ledger.canonical import canonicalize

from . import metarule, params as P
from .distribute import STRUCTURE_VERSION

__all__ = ["PublicationRefused", "STRUCTURE_MODULES", "source_hashes",
           "structure_hash", "params_hash", "build_artifact", "publish",
           "meta_rule_artifact", "meta_rule_hash", "artifact_bytes"]

#: The files whose bytes ARE the structure.  Changing any of them changes
#: rule_version, and the meta-rule refuses the result as an amendment.
STRUCTURE_MODULES = ("params.py", "valuation.py", "distribute.py",
                     "metarule.py")

_HERE = os.path.dirname(os.path.abspath(__file__))


class PublicationRefused(Exception):
    """Refusing to publish: the parameters are placeholders."""


def source_hashes(directory=None):
    """filename -> sha256 of its exact bytes, for every structure module."""
    root = _HERE if directory is None else directory
    out = {}
    for name in STRUCTURE_MODULES:
        with open(os.path.join(root, name), "rb") as handle:
            out[name] = hashlib.sha256(handle.read()).hexdigest()
    return out


def structure_hash(sources):
    return hashlib.sha256(canonicalize(
        {"structure_version": STRUCTURE_VERSION, "sources": sources})).hexdigest()


def params_hash(params):
    return hashlib.sha256(canonicalize(params)).hexdigest()


def build_artifact(params=None, prev_rule_version=None, directory=None):
    """The rule-version artifact.  Works with placeholders (development)."""
    params = P.PLACEHOLDER_PARAMS if params is None else params
    P.validate_params(params)
    sources = source_hashes(directory)
    s_hash = structure_hash(sources)
    p_hash = params_hash(params)
    artifact = {
        "structure_version": STRUCTURE_VERSION,
        "structure_hash": s_hash,
        "sources": sources,
        "params": params,
        "params_hash": p_hash,
        "rule_version": hashlib.sha256(canonicalize(
            {"structure_hash": s_hash, "params_hash": p_hash})).hexdigest(),
        "prev_rule_version": prev_rule_version,
        "notice": P.DISCLOSURE,
    }
    return artifact


def artifact_bytes(artifact):
    return canonicalize(artifact)


def publish(params, prev_artifact=None, state=None, directory=None):
    """Build a PUBLISHABLE artifact plus its ``rule.version_published`` payload.

    Refuses placeholder parameters.  If *prev_artifact* is given, the meta-rule
    must also accept the change (amendments are gated by the meta-rule, never
    by the publisher's judgement).
    """
    try:
        P.assert_publishable(params)
    except P.ParamsError as exc:
        raise PublicationRefused(str(exc))

    artifact = build_artifact(
        params,
        prev_rule_version=None if prev_artifact is None else prev_artifact["rule_version"],
        directory=directory)

    if prev_artifact is not None:
        metarule.assert_valid_amendment(prev_artifact, artifact,
                                        {} if state is None else state)

    payload = {"rule_version": artifact["rule_version"],
               "source_hash": artifact["structure_hash"],
               "params_hash": artifact["params_hash"]}
    return artifact, payload


def meta_rule_artifact(directory=None):
    """The published meta-rule: its clause list and the bytes that implement it."""
    root = _HERE if directory is None else directory
    with open(os.path.join(root, "metarule.py"), "rb") as handle:
        source = hashlib.sha256(handle.read()).hexdigest()
    return {"checks": list(metarule.CHECKS), "source_hash": source,
            "structure_version": STRUCTURE_VERSION}


def meta_rule_hash(directory=None):
    return hashlib.sha256(canonicalize(meta_rule_artifact(directory))).hexdigest()
