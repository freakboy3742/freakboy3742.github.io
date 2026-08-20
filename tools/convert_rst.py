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
