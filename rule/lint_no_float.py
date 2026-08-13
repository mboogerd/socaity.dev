"""The no-float lint: an AST gate on the mechanism path.

socaity-x8o §5 / platform-engineer PARAMOUNT: "no floats in the mechanism
path", "floats banned and AST-lint-enforced".  Review cannot enforce this --
``a / b`` on two ints is a float, ``sum()`` over a float is a float, and both
read as ordinary arithmetic.  So the check is mechanical and runs in CI.

Two tiers:

* CORE (:data:`CORE_MODULES`) -- the pure rule.  No floats AND no I/O, no
  clock, no environment, no randomness: the import allowlist is
  :data:`CORE_IMPORTS`.
* SUPPORT -- everything else under ``rule/``, including the publisher, the
  replay adapter, the CI driver and the tests.  Floats are still banned (a
  float in a test fixture would silently teach the golden vectors to lie); the
  import allowlist is relaxed.

Findings
--------
float_literal        a float or complex constant
float_op             the `/` operator (true division; use rule.distribute._div
                     or fractions.Fraction(a, b))
float_name           float / complex / round / a float-producing builtin
banned_import        a module outside the tier's allowlist
negative_pow         `x ** -n`, which produces a float for int x

Usage:  python3 -m rule.lint_no_float [paths...]   (exit 1 on any finding)
"""

import ast
import os
import sys

__all__ = ["Finding", "lint_source", "lint_file", "lint_paths", "CORE_MODULES",
           "CORE_IMPORTS", "SUPPORT_IMPORTS", "BANNED_NAMES", "SELF_EXEMPT"]

CORE_MODULES = ("params.py", "valuation.py", "distribute.py", "metarule.py")

#: The linter itself must name the types and operators it bans, so linting its
#: own source would report its own ban list.  It is the only exemption, it is
#: named here rather than inferred, and test_lint.py asserts that the exemption
#: list contains nothing else.
SELF_EXEMPT = ("lint_no_float.py",)

#: The pure rule may import exactly these.  `ledger.canonical` is the repo's
#: own RFC 8785 implementation (stdlib-only, a published artifact itself);
#: re-implementing it here would be a second canonicaliser to keep in sync.
CORE_IMPORTS = ("fractions", "hashlib", "ledger.canonical")

SUPPORT_IMPORTS = CORE_IMPORTS + ("rule", "ast", "json", "os", "sys", "unittest",
                                  "datetime", "hmac", "argparse", "ledger",
                                  "ledger.canonical", "ledger.catalog",
                                  "ledger.crypto", "ledger.validator",
                                  "ledger.log", "difflib", "copy", "itertools",
                                  "random", "collections")

#: Names that produce a float no matter what they are handed.
BANNED_NAMES = ("float", "complex", "round", "fsum", "sqrt", "log", "exp",
                "mean", "median", "truediv")


class Finding:
    def __init__(self, path, node, kind, message):
        self.path = path
        self.line = getattr(node, "lineno", 0)
        self.col = getattr(node, "col_offset", 0)
        self.kind = kind
        self.message = message

    def __str__(self):
        return "%s:%d:%d: %s: %s" % (self.path, self.line, self.col + 1,
                                     self.kind, self.message)


def _module_name(node):
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if node.level:                       # relative import inside the package
        return []
    # For `from X import a, b` only X is a module; a and b are its members.
    return [node.module or ""]


def lint_source(source, path, allowed_imports):
    """Return a list of Findings for one module's source text."""
    findings = []
    tree = ast.parse(source, filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, float):
                findings.append(Finding(path, node, "float_literal",
                                        "float literal %r" % (node.value,)))
            elif isinstance(node.value, complex):
                findings.append(Finding(path, node, "float_literal",
                                        "complex literal %r" % (node.value,)))
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            findings.append(Finding(
                path, node, "float_op",
                "`/` is banned: on integers it silently produces a float. "
                "Use Fraction(a, b) or the exact _div helper."))
        elif isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Div):
            findings.append(Finding(path, node, "float_op", "`/=` is banned"))
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            right = node.right
            if isinstance(right, ast.UnaryOp) and isinstance(right.op, ast.USub):
                findings.append(Finding(path, node, "negative_pow",
                                        "a negative exponent produces a float"))
        elif isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            findings.append(Finding(path, node, "float_name",
                                    "%s() produces a float" % node.id))
        elif isinstance(node, ast.Attribute) and node.attr in BANNED_NAMES:
            findings.append(Finding(path, node, "float_name",
                                    ".%s produces a float" % node.attr))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for name in _module_name(node):
                root = name.split(".")[0]
                if name not in allowed_imports and root not in allowed_imports:
                    findings.append(Finding(path, node, "banned_import",
                                            "import %s is outside the allowlist"
                                            % name))
    return findings


def lint_file(path):
    core = os.path.basename(path) in CORE_MODULES
    allowed = CORE_IMPORTS if core else SUPPORT_IMPORTS
    with open(path, "r", encoding="utf-8") as handle:
        return lint_source(handle.read(), path, allowed)


def lint_paths(paths):
    targets = []
    for path in paths:
        if os.path.isdir(path):
            for root, _dirs, files in sorted(os.walk(path)):
                for name in sorted(files):
                    if name.endswith(".py"):
                        targets.append(os.path.join(root, name))
        elif path.endswith(".py"):
            targets.append(path)
    out = []
    for path in sorted(targets):
        if os.path.basename(path) in SELF_EXEMPT:
            continue
        out.extend(lint_file(path))
    return out


def main(argv):
    paths = argv[1:] or [os.path.dirname(os.path.abspath(__file__))]
    findings = lint_paths(paths)
    for finding in findings:
        sys.stderr.write("%s\n" % finding)
    if findings:
        sys.stderr.write("no-float lint: %d finding(s)\n" % len(findings))
        return 1
    sys.stdout.write("no-float lint: clean (%s)\n" % ", ".join(paths))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
