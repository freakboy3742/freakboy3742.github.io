"""One-off converter from Lektor (reStructuredText) flat files to Markdown.

Reads a Lektor content tree and writes Markdown source for Pelican.
Run manually by a human; never run in CI.
"""

import os
import re
from pathlib import Path


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


QUOTE_DATES = {
    "arne-naess-mountains": "2017-04-29 15:00",
    "plato-republic-child-dark": "2017-04-29 14:00",
    "eleanor-roosevelt-courage": "2017-04-29 13:00",
    "rfk-lawrence": "2017-04-29 12:00",
    "politics-as-a-vocation": "2017-04-29 11:00",
    "dead-poets-society": "2017-04-29 10:00",
    "a-river-runs-through-it": "2017-04-29 09:00",
    "theodore-roosevelt-critics": "2017-04-29 08:00",
    "nick-cave-truths": "2017-04-29 07:00",
    "stanley-kubrick-playboy": "2017-04-29 06:00",
    "nick-cave-days": "2017-04-29 05:00",
    "eugene-oneill": "2017-04-29 04:00",
    "john-maynard-keynes-words": "2017-04-29 03:00",
    "antoine-de-saint-exupery-ships": "2017-04-29 02:00",
    "west-wing-words": "2017-04-29 01:00",
}

_PAGE_ASSET_RE = re.compile(r"\((mugshot\.png|beeware\.png|django\.png|CurriculumVitae-RussellKeith-Magee\.pdf)\)")
_PAGE_ASSETS = {
    "mugshot.png": "/about/mugshot.png",
    "beeware.png": "/projects/beeware.png",
    "django.png": "/projects/django.png",
    "CurriculumVitae-RussellKeith-Magee.pdf": "/about/CurriculumVitae-RussellKeith-Magee.pdf",
}


def write_entry(slug: str, fields: dict[str, str], dest_dir: str):
    lines = [f"Title: {fields['title']}", f"Date: {fields['pub_date']}"]
    if fields.get("excerpt"):
        flat = " ".join(rst_to_markdown(fields["excerpt"]).split())
        lines.append("Summary: " + flat)
    if fields.get("author"):
        lines.append(f"Author: {fields['author']}")
    body = rst_to_markdown(fields["body"])
    out = "\n".join(lines) + "\n\n" + body
    dest = os.path.join(dest_dir, "entries", f"{slug}.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    return Path(os.path.abspath(dest))


def write_quote(slug: str, fields: dict[str, str], dest_dir: str):
    author = fields["author"]
    lines = [f"Title: {author}", f"Author: {author}"]
    if fields.get("location"):
        lines.append(f"Location: {fields['location']}")
    if fields.get("context"):
        lines.append(f"Context: {fields['context']}")
    lines.append(f"Date: {QUOTE_DATES[slug]}")
    lines.append("Template: quotation")
    body = rst_to_markdown(fields["text"])
    out = "\n".join(lines) + "\n\n" + body
    dest = os.path.join(dest_dir, "inspiration", f"{slug}.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    return Path(os.path.abspath(dest))


def write_page(slug: str, fields: dict[str, str], dest_dir: str):
    body = rst_to_markdown(fields["body"])
    body = _PAGE_ASSET_RE.sub(lambda m: f"({_PAGE_ASSETS[m.group(1)]})", body)
    out = f"Title: {fields['title']}\nDisplayTitle: yes\n\n{body}"
    dest = os.path.join(dest_dir, "pages", f"{slug}.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    return Path(os.path.abspath(dest))


def _copy_assets(src_dir: str, dest_dir: str) -> None:
    copies = [
        (("about", "mugshot.png"), ("about", "mugshot.png")),
        (("about", "CurriculumVitae-RussellKeith-Magee.pdf"), ("about", "CurriculumVitae-RussellKeith-Magee.pdf")),
        (("projects", "beeware.png"), ("projects", "beeware.png")),
        (("projects", "django.png"), ("projects", "django.png")),
    ]
    for (src_sub, src_name), (dst_sub, dst_name) in copies:
        src = os.path.join(src_dir, src_sub, src_name)
        dst = os.path.join(dest_dir, dst_sub, dst_name)
        if not os.path.exists(src):
            raise FileNotFoundError(f"Missing asset: {src}")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            f_out.write(f_in.read())


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Convert Lektor content to Markdown")
    parser.add_argument("--src", required=True, help="path to exported lektor content dir")
    parser.add_argument("--dest", required=True, help="destination content dir (repo content/)")
    args = parser.parse_args(argv)

    src = args.src
    dest = args.dest

    for slug in sorted(os.listdir(os.path.join(src, "entries"))):
        lr = os.path.join(src, "entries", slug, "contents.lr")
        if os.path.isfile(lr):
            with open(lr, encoding="utf-8") as f:
                write_entry(slug, parse_lr(f.read()), dest)

    for slug in sorted(os.listdir(os.path.join(src, "inspiration"))):
        lr = os.path.join(src, "inspiration", slug, "contents.lr")
        if os.path.isfile(lr):
            with open(lr, encoding="utf-8") as f:
                write_quote(slug, parse_lr(f.read()), dest)

    for slug in ("about", "projects", "contact", "colophon"):
        lr = os.path.join(src, slug, "contents.lr")
        if os.path.isfile(lr):
            with open(lr, encoding="utf-8") as f:
                write_page(slug, parse_lr(f.read()), dest)

    _copy_assets(src, dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
