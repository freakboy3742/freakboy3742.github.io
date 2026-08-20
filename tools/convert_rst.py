"""One-off converter from Lektor (reStructuredText) flat files to Markdown.

Reads a Lektor content tree and writes Markdown source for Pelican.
Run manually by a human; never run in CI.
"""

import os
import re


def parse_lr(text: str) -> dict[str, str]:
    """Parse a Lektor flat-file document into {field_name: value}."""
    fields: dict[str, str] = {}
    for block in text.split("\n---\n"):
        block = block.strip("\n")
        if not block.strip():
            continue
        lines = block.split("\n")
        header = lines[0]
        if ":" not in header:
            continue
        key, _, inline = header.partition(":")
        key = key.strip().lower()
        inline = inline.strip()
        rest = "\n".join(lines[1:]).strip()
        if inline and rest:
            value = inline + "\n\n" + rest
        else:
            value = inline + rest
        fields[key] = value
    return fields


_ADORNMENTS = "~-=^+*#"

_UNDERLINE_RE = re.compile(r"^([~\-=^+*#])\1{2,}$")
_HR_RE = re.compile(r"^([\-=])\1{2,}$")

_INLINE_LINK_RE = re.compile(r"`([^`\n]+?) <([^<>\n]+)>`_+")
_INLINE_LITERAL_RE = re.compile(r"``([^`]+)``")


def _convert_inline(text: str) -> str:
    text = _INLINE_LINK_RE.sub(lambda m: f"[{m.group(1)}]({m.group(2)})", text)
    text = _INLINE_LITERAL_RE.sub(lambda m: f"`{m.group(1)}`", text)
    return text


def _is_underline(line: str) -> bool:
    return bool(_UNDERLINE_RE.match(line))


def _is_hr(line: str, prev_line: str) -> bool:
    if not _HR_RE.match(line):
        return False
    return not prev_line.strip()  # blank line before => horizontal rule


def rst_to_markdown(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    adornment_level: dict[str, int] = {}
    next_level = 2
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            out.append("")
            i += 1
            continue

# --- literal block: paragraph ending with '::' + indented block ---
        if stripped.endswith("::") and not stripped.startswith(".."):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                block: list[str] = []
                indent = None
                while j < len(lines) and lines[j].strip():
                    l = lines[j]
                    lead = len(l) - len(l.lstrip())
                    if indent is None:
                        indent = lead
                    block.append(l[indent:] if lead >= indent else l.lstrip())
                    j += 1
                prefix = stripped[:-2].rstrip()
                if prefix:
                    out.append(_convert_inline(prefix))
                out.append("```text")
                out.extend(block)
                out.append("```")
                i = j
                continue

        # --- image directive ---
        if stripped.startswith(".. image::"):
            target = stripped[len(".. image::"):].strip()
            opts: dict[str, str] = {}
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith(":"):
                m = re.match(r":(\w+):\s*(.*)", lines[j].strip())
                if m:
                    opts[m.group(1)] = m.group(2)
                j += 1
            alt = opts.get("alt", "")
            width = opts.get("width", "")
            classes = []
            if opts.get("align") == "left":
                classes.append("align-left")
            if width:
                classes.append("img-" + width.replace("%", ""))
            attrs = ("{: .%s}" % " .".join(classes)) if classes else ""
            out.append(f"![{alt}]({target}){attrs}")
            i = j
            continue

        # --- raw html directive ---
        if stripped.startswith(".. raw:: html"):
            j = i + 1
            block = []
            while j < len(lines) and lines[j].strip():
                block.append(lines[j].lstrip())
                j += 1
            out.extend(block)
            i = j
            continue

        # --- other directives: skip (none expected in the source) ---
        if stripped.startswith(".. "):
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith(":"):
                j += 1
            i = j
            continue

        # --- section heading: underline directly below text ---
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        prev = lines[i - 1] if i > 0 else ""
        if _is_underline(nxt) and stripped:
            char = nxt[0]
            if char not in adornment_level:
                adornment_level[char] = next_level
                next_level += 1
            out.append("#" * adornment_level[char] + " " + _convert_inline(stripped))
            i += 2
            continue

        # --- horizontal rule: standalone dashes with blank line before ---
        if _is_hr(stripped, prev):
            out.append("---")
            i += 1
            continue

        out.append(_convert_inline(stripped))
        i += 1

    return "\n".join(out).strip() + "\n"
