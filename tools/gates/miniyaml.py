#!/usr/bin/env python3
"""A YAML subset parser, stdlib only, for the gate scripts.

The gates run before `pip install`, so they cannot use PyYAML; they only ever
read graph node/ticket files, whose shape is fixed by graph/SCHEMA (schema: 1):
block mappings, block sequences, plain and quoted scalars, `|` block scalars,
and empty flow collections (`[]`, `{}`).  Anything outside that subset raises,
loudly, rather than being silently mis-parsed — the real validator
(tools/validate) is the authority on schema, this is only enough YAML to ask
questions about edges.

The gates and the renderer must agree about the graph, so every divergence
from PyYAML found by tools/gates/test_gates.py is closed in one of two ways:
matched, or turned into a loud `YAMLSubsetError`.  Silently parsing something
differently is the one outcome that is not allowed — a gate that reads a
different tree than the renderer is worse than no gate.  In particular:

  * TAB indentation is rejected.  Tabs are illegal YAML indentation; PyYAML
    raises, and this parser used to read `\t- id: e1` as a *sibling* of its
    key, which silently emptied `edges:` and disarmed the dispute gate.
  * `---` opens the document; a second one (multi-document) is rejected.
  * Non-empty flow collections (`[a, b]`, `{a: 1}`) are rejected rather than
    returned as a string that happens to look like YAML.
  * Anchors, aliases and multi-line plain scalars are rejected by name.
  * Blank lines and `#`-leading lines inside a `|` block are content, not
    structure, and survive.
  * YAML 1.1 booleans (`yes`/`no`/`on`/`off`) resolve as PyYAML resolves them.
  * A leading-zero integer is ambiguous (PyYAML reads `0012` as octal 10), so
    it is rejected rather than guessed.
"""

import re


class YAMLSubsetError(ValueError):
    pass


# A mapping key is `word:` followed by end-of-line or a space — so that a
# sequence item like `- sha256:abcd…` stays the scalar it is.
_KEY = re.compile(r"""(?P<key>'[^']*'|"[^"]*"|[^\s:#][^:#]*?):(?:\s|$)""")
_INT = re.compile(r"[-+]?[0-9]+")
# `0012` is octal 10 to PyYAML's 1.1 resolver and twelve to everyone else.
_AMBIGUOUS_INT = re.compile(r"[-+]?0[0-9]+")
_FLOW = re.compile(r"[\[{]")
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "0": "\0",
            "\\": "\\", '"': '"', "/": "/", "a": "\a", "b": "\b", "f": "\f",
            "v": "\v", "e": "\x1b", " ": " "}
# PyYAML's safe resolver is YAML 1.1 minus the bare `y`/`n` forms — verified
# against PyYAML in tools/gates/test_gates.py, because `- y` under `tags:` must
# stay the string "y".
_TRUE = {"true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"}
_FALSE = {"false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF"}
_FLOAT = re.compile(r"[-+]?(?:[0-9]*\.[0-9]+|[0-9]+\.[0-9]*)(?:[eE][-+]?[0-9]+)?")


def _unescape(text):
    """Double-quoted escape processing, the subset YAML shares with JSON."""
    out, index = [], 0
    while index < len(text):
        ch = text[index]
        if ch != "\\":
            out.append(ch)
            index += 1
            continue
        index += 1
        if index >= len(text):
            raise YAMLSubsetError("trailing backslash in %r" % text)
        nxt = text[index]
        if nxt in ("x", "u", "U"):
            width = {"x": 2, "u": 4, "U": 8}[nxt]
            digits = text[index + 1:index + 1 + width]
            if len(digits) != width or any(d not in "0123456789abcdefABCDEF"
                                           for d in digits):
                raise YAMLSubsetError("bad \\%s escape in %r" % (nxt, text))
            out.append(chr(int(digits, 16)))
            index += 1 + width
            continue
        if nxt not in _ESCAPES:
            raise YAMLSubsetError("unsupported escape \\%s in %r" % (nxt, text))
        out.append(_ESCAPES[nxt])
        index += 1
    return "".join(out)


def _scalar(text, number=0):
    text = text.strip()
    if text in ("[]",):
        return []
    if text in ("{}",):
        return {}
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        body = text[1:-1]
        # A quote that closes early is a flow collection or a broken scalar,
        # never the plain string it would silently become.
        if text[0] in body.replace("''", "").replace('\\"', ""):
            raise YAMLSubsetError(
                "line %d: quoted scalar with an embedded quote is outside the "
                "subset: %r" % (number, text))
        return body.replace("''", "'") if text[0] == "'" else _unescape(body)
    if _FLOW.match(text):
        raise YAMLSubsetError(
            "line %d: non-empty flow collection is outside the subset (use a "
            "block sequence or mapping): %r" % (number, text))
    if text[:1] in ("*", "&"):
        raise YAMLSubsetError(
            "line %d: YAML anchors and aliases are outside the subset: %r"
            % (number, text))
    if text in ("null", "Null", "NULL", "~", ""):
        return None
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    if _AMBIGUOUS_INT.fullmatch(text):
        raise YAMLSubsetError(
            "line %d: leading-zero number %r is ambiguous (PyYAML reads it as "
            "octal) — quote it if it is a string" % (number, text))
    if _INT.fullmatch(text):
        return int(text)
    if _FLOAT.fullmatch(text):
        return float(text)
    return text


def _strip_comment(text):
    quote = None
    for i, ch in enumerate(text):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "#" and (i == 0 or text[i - 1] in " \t"):
            return text[:i]
    return text


def _lines(raw):
    """Structural rows: (source_line_no, indent, text, source_index).

    Blank and comment lines carry no structure, so they are dropped here — but
    `source_index` keeps the way back to the raw document, which is how a `|`
    block keeps the blank lines and `#`-leading lines that are its content.
    """
    out = []
    for offset, line in enumerate(raw.split("\n")):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.lstrip(" ")
        if stripped[:1] == "\t" or "\t" in line[:len(line) - len(stripped)]:
            raise YAMLSubsetError(
                "line %d: TAB indentation is not legal YAML and is rejected — "
                "PyYAML raises on it, and reading it as indentation would make "
                "this parser disagree with the renderer: %r" % (offset + 1, line))
        out.append((offset + 1, len(line) - len(stripped), line, offset))
    return out


def loads(raw):
    """Parse one YAML document into dicts/lists/scalars."""
    src = raw.split("\n")
    rows = _lines(raw)
    # A leading `---` opens the document and is not content; a later one would
    # open a second document, which this subset does not represent.
    if rows and rows[0][2].strip() == "---":
        rows = rows[1:]
    for number, _indent, line, _offset in rows:
        if line.strip() in ("---", "..."):
            raise YAMLSubsetError(
                "line %d: multi-document YAML is outside the subset" % number)
    if not rows:
        return None
    value, index = _parse_block(src, rows, 0, rows[0][1])
    if index != len(rows):
        raise YAMLSubsetError(
            "line %d: unparsed trailing content — a multi-line plain scalar, a "
            "nested flow structure or a bad indent step: %r"
            % (rows[index][0], rows[index][2].strip()))
    return value


def _block_scalar(src, rows, index, parent_indent, style, chomp):
    """Consume a `|` / `>` block, returning (text, next_index).

    The body is taken from the *raw* document between the first and last
    structural row of the block, so blank lines and lines that begin with `#`
    survive as the content they are.
    """
    start = index
    while index < len(rows) and rows[index][1] > parent_indent:
        index += 1
    if index == start:
        return ("" if chomp == "-" else ""), index
    body = src[rows[start][3]:rows[index - 1][3] + 1]
    strip = min(len(c) - len(c.lstrip(" ")) for c in body if c.strip())
    body = [c[strip:] if c.strip() else "" for c in body]
    text = "\n".join(body) if style == "|" else " ".join(body)
    return (text if chomp == "-" else text + "\n"), index


def _parse_block(src, rows, index, indent):
    if index >= len(rows):
        return None, index
    if rows[index][2].lstrip().startswith("- "):
        return _parse_sequence(src, rows, index, indent)
    return _parse_mapping(src, rows, index, indent)


def _parse_sequence(src, rows, index, indent):
    items = []
    while index < len(rows) and rows[index][1] == indent:
        number, _, line, offset = rows[index]
        body = line.lstrip()
        if not body.startswith("- ") and body.rstrip() != "-":
            break
        inline = _strip_comment(body[2:]).rstrip()
        child_indent = indent + 2
        if _KEY.match(inline):
            # `- key: value` opens a mapping whose first key sits inline.
            synthetic = [(number, child_indent, " " * child_indent + inline, offset)]
            rest, index = _take(rows, index + 1, child_indent)
            item, consumed = _parse_mapping(src, synthetic + rest, 0, child_indent)
            if consumed != len(synthetic) + len(rest):
                raise YAMLSubsetError(
                    "line %d: unparsed content inside sequence item"
                    % (synthetic + rest)[consumed][0])
            items.append(item)
        else:
            items.append(_scalar(inline, number))
            index += 1
    return items, index


def _take(rows, index, indent):
    """Rows that belong to a block at `indent` or deeper."""
    out = []
    while index < len(rows) and rows[index][1] >= indent:
        out.append(rows[index])
        index += 1
    return out, index


def _parse_mapping(src, rows, index, indent):
    result = {}
    while index < len(rows) and rows[index][1] == indent:
        number, _, line, _offset = rows[index]
        body = line.strip()
        if body.startswith("- "):
            break
        found = _KEY.match(body)
        if not found:
            raise YAMLSubsetError("line %d: not a mapping entry: %r" % (number, body))
        key = found.group("key").strip().strip("'\"")
        rest = _strip_comment(body[found.end():]).strip()
        index += 1
        if rest in ("|", ">", "|-", ">-", "|+", ">+"):
            text, index = _block_scalar(src, rows, index, indent, rest[0],
                                        rest[1:] or "")
            result[key] = text
        elif rest == "":
            if index < len(rows) and rows[index][1] > indent:
                child, index = _parse_block(src, rows, index, rows[index][1])
                result[key] = child
            elif (index < len(rows) and rows[index][1] == indent
                    and rows[index][2].lstrip().startswith("- ")):
                child, index = _parse_sequence(src, rows, index, indent)
                result[key] = child
            else:
                result[key] = None
        else:
            result[key] = _scalar(rest, number)
    return result, index


def load_file(path):
    with open(path, encoding="utf-8") as handle:
        return loads(handle.read())
