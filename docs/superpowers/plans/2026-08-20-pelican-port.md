# Pelican Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port cecinestpasun.com from Lektor + reStructuredText to Pelican + Markdown, preserving every existing URL, on a clean `main` branch.

**Architecture:** A bespoke Pelican theme (`themes/cecinestpasun/`) reproduces the current layout/palette with HTML5 semantics. Content is converted from `content/**/contents.lr` (reST) to `content/**/*.md` (Markdown) by a one-off converter script (`tools/convert_rst.py`) that is tested with pytest but not run in CI. URL pinning is done entirely in `pelicanconf.py`; CI builds with `publishconf.py` and deploys via GitHub Actions + Pages.

**Tech Stack:** Pelican 4.10.x, Python-Markdown 3.7 (codehilite, fenced_code, attr_list, smart_quotes), Pygments, pytz, typogrify, pytest, GitHub Actions (`actions/deploy-pages`).

## Global Constraints

- **Preserve every existing URL byte-for-byte.** All 22 entries (`/entries/<slug>/`), 15 quotes (`/inspiration/<slug>/`), 4 pages (`/about/`, `/projects/`, `/contact/`, `/colophon/`), `/` (home), `/entries/` + `/entries/page/2/` + `/entries/page/3/` (pagination), and the Atom feed at `/rss/all/`.
- **Assets stay in place** (user decision): images keep their existing URLs — `content/about/mugshot.png` → `/about/mugshot.png`, `content/projects/beeware.png` → `/projects/beeware.png`, `content/projects/django.png` → `/projects/django.png`, `content/about/CurriculumVitae-RussellKeith-Magee.pdf` → `/about/CurriculumVitae-RussellKeith-Magee.pdf`.
- `TIMEZONE = 'Australia/Perth'` (source dates are local naive times; display must show the same local wall-clock time as today).
- `SITEURL = 'https://cecinestpasun.com/'` in `publishconf.py` only; `pelicanconf.py` keeps `SITEURL = ''` so dev builds emit root-relative links.
- Keep the palette exactly: `#FFD06B`, `#ffffea`, `#330e00`, `#B85D00`; Georgia serif. Same DOM structure/class names so the CSS carries over. Modernize to HTML5 (`<header>`, `<nav>`, `<main>`, `<footer>`), modern doctype, viewport meta, drop `min-width:50em`.
- Drop Google Analytics entirely (no replacement).
- Feed is Atom only, at `/rss/all/`, and contains **entries only** (never the quotes) — matching the old Lektor feed config (`site.query('/entries')`).
- Quotes carry `Author`, `Location`, `Context` (when present) metadata; they get synthetic `Date:` values only to pin their display order (no date is ever shown on a quote page). No prev/next navigation on quote pages (matches today).
- Home (`index.html`) lists all 22 entries, unpaginated (matches Lektor's `home.html` which queries all of `/entries`).
- Only the `entries` category is paginated (10/page). The `inspiration` category page lists all 15 quotes on one page (matches today); the harmless extra `/inspiration/page/2/` output may exist but must not be linked.
- Blog-post pages keep today's quirky titles: page `<title>` and masthead read "Ceci n'est pas un blog" on entry/article pages, "Ceci n'est pas un inspiration" on quote pages, "Ceci n'est pas un homepage" on `/`, and "Ceci n'est pas <page title>" on pages.
- Prev/next nav semantics: "Previous entry" links to the OLDER post, "Next entry" links to the NEWER post.
- `main` has clean history; the `lektor` branch is untouched as the source of truth. `master` untouched.
- Python 3.12 in CI; dependencies pinned in `requirements.txt`.
- No comments in generated code unless required for readability.

---

## File Structure

New repo layout on `main` (all paths relative to repo root):

```
pelicanconf.py                    # dev config (SITEURL='')
publishconf.py                    # prod config (SITEURL set)
requirements.txt                  # pinned deps
.gitignore
tools/
  convert_rst.py                  # one-off reST -> Markdown converter
  test_convert_rst.py             # pytest tests for the converter
plugins/
  __init__.py                     # empty marker (pelican plugin path)
  neighbors.py                    # per-category prev/next plugin
  entries_feed.py                 # feed = entries only
content/
  entries/<slug>.md               # 22 posts -> /entries/<slug>/
  inspiration/<slug>.md           # 15 quotes -> /inspiration/<slug>/
  pages/{about,projects,contact,colophon}.md   # -> /<slug>/
  about/                          # mugshot.png, CurriculumVitae-RussellKeith-Magee.pdf
  projects/                       # beeware.png, django.png
  extra/CNAME                     # "cecinestpasun.com"
themes/cecinestpasun/
  templates/
    base.html
    index.html
    article.html
    category.html
    quotation.html
    page.html
    404.html
    macros/entry.html
    macros/quotation.html
    macros/pagination.html
  static/css/cecinestpasun.css    # modernized, same palette
.github/workflows/publish.yml     # build + deploy on main
docs/superpowers/                 # plan + spec (kept from lektor branch)
```

Design units and responsibilities:

- `tools/convert_rst.py` — one module, three pure functions (`parse_lr`, `rst_to_markdown`, `write_markdown`) plus a CLI. It reads a Lektor content tree and writes Markdown files + copies assets. Tested via pytest. Not run in CI.
- `plugins/neighbors.py` — tiny plugin setting `article.older_entry` / `article.newer_entry` per category (core Pelican does **not** provide prev/next; the community neighbors plugin operates across all categories, which is wrong here).
- `plugins/entries_feed.py` — patches `ArticlesGenerator.generate_feeds` so the Atom feed contains only the `entries` category.
- `themes/cecinestpasun/` — all templates + CSS. Templates replicate the current DOM and class names (`#header`, `#nav`, `#main`, `#content`, `#footer`, `.wrap`, `.date`, `.link`, `.archive`, `.pagination`, `.mastodon`, `.anchor`, `.author`, `.location`, `.context`) so the existing CSS carries over with only modernization edits.
- `pelicanconf.py` / `publishconf.py` — all URL pinning lives here (see Global Constraints). `publishconf.py` imports `pelicanconf` and overrides `SITEURL` + `DELETE_OUTPUT_DIRECTORY`.

---

### Task 1: Scaffold the clean `main` branch

**Files:**
- Create: `.gitignore`
- Create: `docs/superpowers/` (copy spec + plan from the lektor branch)
- Create: empty `tools/`, `plugins/` (with `__init__.py`), `content/` dirs with `.gitkeep`-style placeholders, `themes/cecinestpasun/` skeleton dirs

**Interfaces:**
- Consumes: the approved spec at `docs/superpowers/specs/2026-08-20-pelican-port-design.md` on the `lektor` branch.
- Produces: an orphan `main` branch with a clean tree that later tasks fill in. All subsequent tasks run on `main`.

- [ ] **Step 1: Create the orphan `main` branch**

Run from a fresh clone/worktree of this repo (do NOT disturb the `lektor` checkout):

```bash
# From a scratch copy of the repo (e.g. git worktree add -b main ../cecinestpasun-main):
git checkout --orphan main
git rm -rf . >/dev/null
git clean -fdx
git commit --allow-empty -m "chore: start main branch with clean history"
git push -u origin main
```

- [ ] **Step 2: Export the lektor source-of-truth content for the converter**

```bash
git archive lektor -o /tmp/lektor-content.tar
mkdir -p /tmp/lektor-content
tar -xf /tmp/lektor-content.tar -C /tmp/lektor-content
```

This gives `/tmp/lektor-content/content/**` — the input for Task 6. (Converts from a snapshot; the `lektor` branch itself is never modified.)

- [ ] **Step 3: Create the `.gitignore`**

Write `.gitignore`:

```
output/
__pycache__/
*.pyc
.DS_Store
.venv/
venv/
```

- [ ] **Step 4: Copy the spec + plan into `docs/superpowers/`**

```bash
mkdir -p docs/superpowers/specs docs/superpowers/plans
cp /tmp/lektor-content/docs/superpowers/specs/2026-08-20-pelican-port-design.md docs/superpowers/specs/
cp /tmp/lektor-content/docs/superpowers/plans/2026-08-20-pelican-port.md docs/superpowers/plans/
```

- [ ] **Step 5: Create empty package/asset dirs**

```bash
mkdir -p tools plugins content/entries content/inspiration content/pages \
         content/about content/projects content/extra \
         themes/cecinestpasun/templates/macros themes/cecinestpasun/static/css
touch plugins/__init__.py
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: scaffold pelican project structure on main"
```

Expected: `git status` clean, `git log --oneline` shows 2 commits, tree contains `.gitignore`, `docs/`, `plugins/__init__.py`, empty content/theme/tools dirs.

---

### Task 2: Converter — Lektor flat-file parser

**Files:**
- Create: `tools/convert_rst.py`
- Create: `tools/test_convert_rst.py`

**Interfaces:**
- Consumes: nothing yet (pure function).
- Produces: `parse_lr(text: str) -> dict[str, str]` — maps field name (lowercase) to raw string value. Used by Task 6's CLI and indirectly by every content task.

The Lektor flat format: fields are separated by lines that are exactly `---`. A field block starts with `key:` (optionally with an inline value after the first colon). The remainder of the block (after the first line) is part of the value. Leading/trailing blank lines are stripped; a common leading indentation is stripped; blank lines *between* paragraphs are preserved. Field order is not significant; some files put `pub_date` after `body` (e.g. `where-do-you-see-python-in-10-years`).

- [ ] **Step 1: Write the failing tests**

```python
import pytest

from convert_rst import parse_lr


def test_parse_single_line_fields():
    text = (
        "title: Moving to Lektor\n"
        "---\n"
        "pub_date: 2017-04-29 16:00:00\n"
    )
    assert parse_lr(text) == {
        "title": "Moving to Lektor",
        "pub_date": "2017-04-29 16:00:00",
    }


def test_parse_multiline_body_field():
    text = (
        "title: X\n"
        "---\n"
        "body:\n"
        "\n"
        "First paragraph.\n"
        "\n"
        "Second paragraph.\n"
    )
    result = parse_lr(text)
    assert result["body"] == "First paragraph.\n\nSecond paragraph."


def test_parse_field_with_inline_value_and_continuation():
    text = (
        "excerpt: Everyone knows the story.\n"
        "\n"
        "But it isn't always like that.\n"
        "---\n"
        "pub_date: 2017-08-27 12:06:12\n"
    )
    result = parse_lr(text)
    assert result["excerpt"] == "Everyone knows the story.\n\nBut it isn't always like that."


def test_parse_colon_inside_inline_value():
    text = "pub_date: 2017-02-13 7:47:54\n"
    assert parse_lr(text)["pub_date"] == "2017-02-13 7:47:54"


def test_parse_preserves_internal_blank_lines():
    text = (
        "text:\n"
        "\n"
        "Line one.\n"
        "\n"
        "\n"
        "Line four.\n"
    )
    assert parse_lr(text)["text"] == "Line one.\n\n\nLine four."
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/test_convert_rst.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'convert_rst'` (collection error; no `__init__.py` needed, run pytest from `tools/` or use `PYTHONPATH=tools`).

- [ ] **Step 3: Implement `parse_lr`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/test_convert_rst.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/convert_rst.py tools/test_convert_rst.py
git commit -m "feat: add Lektor flat-file parser for converter"
```

---

### Task 3: Converter — block structure (headings, rules, literal blocks, raw html, images)

**Files:**
- Modify: `tools/convert_rst.py`
- Modify: `tools/test_convert_rst.py`

**Interfaces:**
- Consumes: `parse_lr` from Task 2.
- Produces: `rst_to_markdown(text: str) -> str` — full reST→Markdown conversion for a body/excerpt. Handles the block-level constructs present in the source:
  - Section headings: an underline of repeated `~`/`-`/`=`/`^`/`+`/`*`/`#` directly beneath a non-blank line. The **first distinct adornment character** in a document maps to `##`, the second distinct character to `###`, etc. (reST semantics: level = order of first appearance; page title is already h1 from metadata, so the first body heading is h2). Underline length may be shorter than the title (present in the PyCon talk) — still a heading.
  - Horizontal rules: a line of 3+ dashes (`-`/`=`) with a **blank line before it** (i.e. not directly under text) → `---`.
  - Literal blocks: a paragraph line ending in `::`, followed by an indented block → fenced code block with `text` language hint; the `::` is dropped from the leading sentence.
  - `.. raw:: html` directive followed by an indented block → emitted verbatim (dedented) as raw HTML.
  - `.. image:: path` with `:width:`, `:alt:`, `:align: left` options → `![alt](path){: .align-left .img-NN}` where `NN` is the numeric width percent (33 or 50).
  - Any other `.. directive::` (none expected) → skipped with its option block.
  - Plain paragraphs and bullet lists pass through verbatim (Markdown-compatible).

- [ ] **Step 1: Write the failing tests**

```python
from convert_rst import rst_to_markdown


def test_heading_levels_by_first_adornment_order():
    text = (
        "About Russell\n"
        "~~~~~~~~~~~~~\n"
        "\n"
        "Text.\n"
        "\n"
        "Academia\n"
        "--------\n"
        "\n"
        "More text.\n"
    )
    result = rst_to_markdown(text)
    assert "## About Russell" in result
    assert "### Academia" in result


def test_heading_with_short_underline():
    text = "Call to action 4: Get out your wallets\n~~~~~~~~~~~~~~~~~~~~~~\n\nBody.\n"
    assert "## Call to action 4: Get out your wallets" in rst_to_markdown(text)


def test_horizontal_rule_requires_blank_line_before():
    text = "Intro.\n\n-----\n\nNext section.\n"
    result = rst_to_markdown(text)
    assert "---" in result
    assert "Intro." in result


def test_dashes_directly_under_text_are_headings_not_rules():
    text = "Transcript\n----------\n\nBody.\n"
    result = rst_to_markdown(text)
    assert "## Transcript" in result
    assert result.count("---") == 0


def test_literal_block_becomes_fenced_code():
    text = (
        "Run the following::\n"
        "\n"
        "    $ export PATH=/opt/subversion/bin:$PATH\n"
        "    $ python -c \"import svn.core\"\n"
    )
    result = rst_to_markdown(text)
    assert "```text" in result
    assert "$ export PATH=/opt/subversion/bin:$PATH" in result
    assert "Run the following" in result
    assert result.index("```text") > result.index("Run the following")


def test_raw_html_directive_emitted_verbatim():
    text = (
        "Intro paragraph.\n"
        "\n"
        ".. raw:: html\n"
        "\n"
        "    <iframe width=\"500\" src=\"https://example.com/v\"></iframe>\n"
    )
    result = rst_to_markdown(text)
    assert '<iframe width="500" src="https://example.com/v"></iframe>' in result


def test_image_directive_becomes_markdown_with_attr_classes():
    text = (
        ".. image:: mugshot.png\n"
        "   :width: 33%\n"
        "   :alt: Russell Keith-Magee's mugshot\n"
        "   :align: left\n"
    )
    result = rst_to_markdown(text)
    assert "![Russell Keith-Magee's mugshot](mugshot.png){: .align-left .img-33}" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/test_convert_rst.py -v`
Expected: FAIL — `ImportError: cannot import name 'rst_to_markdown'` (collection error) or `NameError`.

- [ ] **Step 3: Implement `rst_to_markdown`**

Add to `tools/convert_rst.py`:

```python
_ADORNMENTS = "~-=^+*#"

_UNDERLINE_RE = re.compile(r"^([~\-=^+*#])\1{2,}$")
_HR_RE = re.compile(r"^([\-=])\1{2,}$")


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
            if i + 1 < len(lines) and lines[i + 1].strip():
                block: list[str] = []
                j = i + 1
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
            attrs = ("{: .%s}" % " ".join(classes)) if classes else ""
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
            out.append("#" * adornment_level[char] + " " + stripped)
            i += 2
            continue

        # --- horizontal rule: standalone dashes with blank line before ---
        if _is_hr(stripped, prev):
            out.append("---")
            i += 1
            continue

        out.append(stripped)
        i += 1

    return "\n".join(out).strip() + "\n"
```

Note: the `::` literal-block rule must run before heading/hr checks. Disambiguation: a line with an underline directly below it is a heading (no blank-line requirement — headings can open a body); a standalone dash/equals line with a blank line before it is a horizontal rule.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/test_convert_rst.py -v`
Expected: all tests pass (5 from Task 2 + 7 new = 12 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/convert_rst.py tools/test_convert_rst.py
git commit -m "feat: convert reST block structure to Markdown"
```

---

### Task 4: Converter — inline markup (links, literals, emphasis)

**Files:**
- Modify: `tools/convert_rst.py`
- Modify: `tools/test_convert_rst.py`

**Interfaces:**
- Consumes: `rst_to_markdown` from Task 3.
- Produces: `_convert_inline(text: str) -> str` (private helper) applied to every emitted paragraph/heading line inside `rst_to_markdown`, plus a public `rst_to_markdown` that now handles inline syntax.

Rules:
- `` `text <url>`_ `` and `` `text <url>`__ `` (single or double trailing underscore) → `[text](url)`.
- ````code```` (double backticks, inline literal) → `` `code` ``.
- `*emphasis*` / `**strong**` are already valid Markdown and pass through unchanged.
- Everything else (quotes, dashes, ampersands) preserved verbatim — `smart_quotes` in the Markdown build reproduces the old docutils typography.

- [ ] **Step 1: Write the failing tests**

```python
from convert_rst import rst_to_markdown


def test_inline_link_single_underscore():
    text = "Use `Lektor <https://getlektor.com>`_ for this.\n"
    assert "[Lektor](https://getlektor.com)" in rst_to_markdown(text)


def test_inline_link_double_underscore():
    text = "See `BeeWare <https://beeware.org>`__ here.\n"
    assert "[BeeWare](https://beeware.org)" in rst_to_markdown(text)


def test_multiple_links_in_one_paragraph():
    text = "A `X <http://a.example>`_ and B `Y <http://b.example>`__ end.\n"
    result = rst_to_markdown(text)
    assert "[X](http://a.example)" in result
    assert "[Y](http://b.example)" in result


def test_inline_literal_becomes_backtick():
    text = "Run ``svn+https`` to clone.\n"
    assert "`svn+https`" in rst_to_markdown(text)


def test_link_inside_heading():
    text = "About `BeeWare <https://beeware.org>`__\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nBody.\n"
    result = rst_to_markdown(text)
    assert "## About [BeeWare](https://beeware.org)" in result


def test_emphasis_passes_through():
    text = "It *usually* isn't and **never** was.\n"
    assert "It *usually* isn't and **never** was." in rst_to_markdown(text)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/test_convert_rst.py -v`
Expected: the new tests fail (raw backtick link syntax still present).

- [ ] **Step 3: Implement inline conversion**

Add to `tools/convert_rst.py`:

```python
_INLINE_LINK_RE = re.compile(r"`([^`\n]+?) <([^<>\n]+)>`_+")
_INLINE_LITERAL_RE = re.compile(r"``([^`]+)``")


def _convert_inline(text: str) -> str:
    text = _INLINE_LINK_RE.sub(lambda m: f"[{m.group(1)}]({m.group(2)})", text)
    text = _INLINE_LITERAL_RE.sub(lambda m: f"`{m.group(1)}`", text)
    return text
```

Apply it in `rst_to_markdown` at every `out.append(...)` that writes a paragraph, heading, or literal-block prefix:

```python
        if stripped.endswith("::") and not stripped.startswith(".."):
            ...
            if prefix:
                out.append(_convert_inline(prefix))
            ...
        ...
            out.append("#" * adornment_level[char] + " " + _convert_inline(stripped))
            ...
        out.append(_convert_inline(stripped))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/test_convert_rst.py -v`
Expected: all tests pass (12 + 6 new = 18 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/convert_rst.py tools/test_convert_rst.py
git commit -m "feat: convert reST inline links and literals to Markdown"
```

---

### Task 5: Converter — page writers + CLI + asset copy

**Files:**
- Modify: `tools/convert_rst.py`
- Modify: `tools/test_convert_rst.py`

**Interfaces:**
- Consumes: `parse_lr` (Task 2), `rst_to_markdown` (Tasks 3–4).
- Produces:
  - `QUOTE_DATES: dict[str, str]` — synthetic dates per quote slug, chosen to sort newest-first in the exact live order.
  - `write_entry(slug, fields, dest_dir)` — writes `content/entries/<slug>.md`.
  - `write_quote(slug, fields, dest_dir)` — writes `content/inspiration/<slug>.md`.
  - `write_page(slug, fields, dest_dir)` — writes `content/pages/<slug>.md`.
  - `main(argv) -> int` — CLI entry point.

The **exact live quote order** (newest first) that the synthetic dates must reproduce:

```
arne-naess-mountains, plato-republic-child-dark, eleanor-roosevelt-courage,
rfk-lawrence, politics-as-a-vocation, dead-poets-society, a-river-runs-through-it,
theodore-roosevelt-critics, nick-cave-truths, stanley-kubrick-playboy,
nick-cave-days, eugene-oneill, john-maynard-keynes-words,
antoine-de-saint-exupery-ships, west-wing-words
```

Metadata output formats:

- Entry: `Title:`, `Date:`, optional `Summary:` (only when the source had an excerpt), optional `Author:` (only `moving-to-lektor`), blank line, body. Excerpts are reST too, so they go through `rst_to_markdown`.
- Quote: `Title: <author>`, `Author:`, `Location:`, optional `Context:`, `Date: <synthetic>`, `Template: quotation`, blank line, text (through `rst_to_markdown`).
- Page: `Title:`, `DisplayTitle: yes`, blank line, body. Page images keep their current URL (`/about/mugshot.png`, `/projects/beeware.png`, `/projects/django.png`, `/about/CurriculumVitae-RussellKeith-Magee.pdf`) — rewrite relative image/pdf links in the page body to these root-relative URLs.

- [ ] **Step 1: Write the failing tests**

```python
from convert_rst import QUOTE_DATES, write_quote, write_entry, write_page


def test_quote_dates_reproduce_live_order():
    order = [
        "arne-naess-mountains", "plato-republic-child-dark",
        "eleanor-roosevelt-courage", "rfk-lawrence", "politics-as-a-vocation",
        "dead-poets-society", "a-river-runs-through-it",
        "theodore-roosevelt-critics", "nick-cave-truths",
        "stanley-kubrick-playboy", "nick-cave-days", "eugene-oneill",
        "john-maynard-keynes-words", "antoine-de-saint-exupery-ships",
        "west-wing-words",
    ]
    dates = [QUOTE_DATES[s] for s in order]
    assert dates == sorted(dates, reverse=True)
    assert len(set(dates)) == len(dates)


def test_write_entry_without_summary(tmp_path):
    fields = {
        "title": "Moving to Lektor",
        "pub_date": "2017-04-29 16:00:00",
        "body": "Hello `world <https://example.com>`_.\n",
    }
    path = write_entry("moving-to-lektor", fields, str(tmp_path))
    content = path.read_text()
    assert content.startswith("Title: Moving to Lektor\nDate: 2017-04-29 16:00:00\n")
    assert "Summary:" not in content
    assert "[world](https://example.com)" in content


def test_write_entry_with_excerpt(tmp_path):
    fields = {
        "title": "T",
        "pub_date": "2019-05-03 10:00:00",
        "excerpt": "It *usually* isn't.\n",
        "body": "Body here.\n",
    }
    content = write_entry("t", fields, str(tmp_path)).read_text()
    assert "Summary: It *usually* isn't." in content


def test_write_entry_flattens_multiline_excerpt(tmp_path):
    fields = {
        "title": "T",
        "pub_date": "2019-05-03 10:00:00",
        "excerpt": "Everyone knows the story.\n\nBut it isn't always like that.\n",
        "body": "Body here.\n",
    }
    content = write_entry("t", fields, str(tmp_path)).read_text()
    summary = [l for l in content.split("\n") if l.startswith("Summary:")][0]
    assert summary == "Summary: Everyone knows the story. But it isn't always like that."


def test_write_quote_with_context(tmp_path):
    fields = {
        "author": "Arne Næss",
        "text": "The smaller one comes to feel compared to the mountain.\n",
        "location": "Modesty and the Conquest of Mountains",
    }
    content = write_quote("arne-naess-mountains", fields, str(tmp_path)).read_text()
    assert content.startswith("Title: Arne Næss\n")
    assert "Author: Arne Næss\n" in content
    assert "Location: Modesty and the Conquest of Mountains\n" in content
    assert "Date: 2017-04-29 15:00" in content
    assert "Template: quotation\n" in content
    assert "Context:" not in content


def test_write_page_with_image_link(tmp_path):
    fields = {
        "title": "un about page",
        "modify_title": "yes",
        "body": ".. image:: mugshot.png\n   :width: 33%\n   :alt: mugshot\n   :align: left\n",
    }
    content = write_page("about", fields, str(tmp_path)).read_text()
    assert content.startswith("Title: un about page\nDisplayTitle: yes\n")
    assert "![mugshot](/about/mugshot.png){: .align-left .img-33}" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/test_convert_rst.py -v`
Expected: FAIL — `ImportError: cannot import name 'QUOTE_DATES'` (collection error).

- [ ] **Step 3: Implement writers + CLI**

Add to `tools/convert_rst.py`:

```python
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
    return os.path.abspath(dest)


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
    return os.path.abspath(dest)


def write_page(slug: str, fields: dict[str, str], dest_dir: str):
    body = rst_to_markdown(fields["body"])
    body = _PAGE_ASSET_RE.sub(lambda m: f"({_PAGE_ASSETS[m.group(1)]})", body)
    out = f"Title: {fields['title']}\nDisplayTitle: yes\n\n{body}"
    dest = os.path.join(dest_dir, "pages", f"{slug}.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    return os.path.abspath(dest)


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/test_convert_rst.py -v`
Expected: all tests pass (18 + 6 new = 24 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/convert_rst.py tools/test_convert_rst.py
git commit -m "feat: add converter writers and CLI for entries, quotes, pages"
```

---

### Task 6: Run the converter to generate all content

**Files:**
- Create: `content/entries/<slug>.md` (22 files)
- Create: `content/inspiration/<slug>.md` (15 files)
- Create: `content/pages/{about,projects,contact,colophon}.md` (4 files)
- Create: `content/about/{mugshot.png,CurriculumVitae-RussellKeith-Magee.pdf}`
- Create: `content/projects/{beeware.png,django.png}`

**Interfaces:**
- Consumes: `/tmp/lektor-content/content` (exported in Task 1) and `tools/convert_rst.py` (Tasks 2–5).
- Produces: the complete converted Markdown content tree that Tasks 9–11 build.

- [ ] **Step 1: Run the converter**

```bash
mkdir -p content
python tools/convert_rst.py --src /tmp/lektor-content/content --dest content
```

- [ ] **Step 2: Verify counts and spot-check files**

```bash
ls content/entries | wc -l    # 22
ls content/inspiration | wc -l # 15
ls content/pages                # about.md colophon.md contact.md projects.md
ls content/about content/projects   # png + pdf present
```

Spot-check (read each fully):
- `content/entries/where-do-you-see-python-in-10-years.md` — excerpt present as `Summary:`, `## Acknowledgement of Country`, the YouTube `<iframe>` line, and every `[text](url)` link.
- `content/entries/getting-hgsubversion-work-under-osx.md` — fenced code blocks contain the `$ export ...` lines and the `hg branches`/`hg tags` output; the final `**Updated ...**` line intact.
- `content/entries/autopsy-of-a-slow-train-wreck.md` — multiline `Summary:`, both `<iframe>` and `<blockquote class="twitter-tweet">` raw HTML blocks, `## Transcript`, `### Humans aren't rational`, `----` between the letter opener and the letter body.
- `content/entries/moving-to-lektor.md` — has `Author:` and **no** `Summary:`.
- `content/pages/about.md` — `![Russell Keith-Magee's mugshot](/about/mugshot.png){: .align-left .img-33}`, `[Curriculum Vitae is available](/about/CurriculumVitae-RussellKeith-Magee.pdf)`, `## About Russell`, `### Academia`.
- `content/pages/projects.md` — two images with `/projects/...` URLs and `.img-50`.
- `content/inspiration/*.md` — `Title:`/`Author:` set, `Date:` from `QUOTE_DATES`, `Template: quotation`, no `Summary:`.

- [ ] **Step 3: Manually fix known edge cases**

1. `content/entries/where-do-you-see-python-in-10-years.md`: the line `![Image goes here](images/xkcd-1987.png)` is already Markdown image syntax but the file does not exist on the live site (the reST source renders it as literal text). Escape the brackets so it renders as literal text exactly like today:
   `![Image goes here](images/xkcd-1987.png)` → `\![Image goes here\](images/xkcd-1987.png)`
2. `content/pages/colophon.md`: replace the sentence "This blog is built using `Lektor`..." with "This blog is built using [Pelican](https://blog.getpelican.com)." (the engine has changed; keep the GitHub source link).

- [ ] **Step 4: Run the full test suite once more**

Run: `python -m pytest tools/test_convert_rst.py -q`
Expected: 24 passed.

- [ ] **Step 5: Commit**

```bash
git add content tools
git commit -m "feat: generate Markdown content from Lektor sources"
```

---

### Task 7: Theme — templates, macros, and CSS

**Files:**
- Create: `themes/cecinestpasun/templates/base.html`
- Create: `themes/cecinestpasun/templates/index.html`
- Create: `themes/cecinestpasun/templates/article.html`
- Create: `themes/cecinestpasun/templates/category.html`
- Create: `themes/cecinestpasun/templates/quotation.html`
- Create: `themes/cecinestpasun/templates/page.html`
- Create: `themes/cecinestpasun/templates/404.html`
- Create: `themes/cecinestpasun/templates/macros/entry.html`
- Create: `themes/cecinestpasun/templates/macros/quotation.html`
- Create: `themes/cecinestpasun/templates/macros/pagination.html`
- Create: `themes/cecinestpasun/static/css/cecinestpasun.css`

**Interfaces:**
- Consumes: Pelican template context (articles, pages, categories, article, page, category, `articles_page`, `articles_paginator`, `articles_previous_page`, `articles_next_page`), and the `datefmt` Jinja filter (Task 8).
- Produces: the complete theme. Template class/id names match the CSS; `base.html` is the single layout (masthead + nav + main + footer), nav hand-written exactly as today.

- [ ] **Step 1: Write `base.html`**

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="author" content="Russell Keith-Magee">
        <title>Ceci n'est pas {% block title %}un homepage{% endblock %}</title>
        <link rel="stylesheet" href="/static/css/cecinestpasun.css" media="screen">
        <link rel="alternate" type="application/atom+xml" title="Ceci n'est pas un blog" href="/rss/all/">
        {% block head %}{% endblock %}
    </head>
    <body>
        <header id="header">
            <div class="wrap">
                <p class="title">Ceci n'est pas {% block header %}un homepage{% endblock %}</p>
                <p>The personal blog of Russell Keith-Magee</p>
            </div>
        </header>
        <div class="wrap">
            <main id="main">
                {% block content %}{% endblock %}
            </main>
            <nav id="nav">
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/about/">About Me</a></li>
                    <li><a href="/entries/">Blog</a></li>
                    <li><a href="/projects/">Projects</a></li>
                    <li><a href="/inspiration/">Inspiration</a></li>
                    <li><a href="/contact/">Contact</a></li>
                    <li><a href="/colophon/">Colophon</a></li>
                </ul>
            </nav>
            <footer id="footer">
                <p>Copyright &copy; {{ CURRENT_YEAR }} Russell Keith-Magee</p>
                <a class="mastodon" rel="me" href="https://cloudisland.nz/@freakboy3742">Mastodon</a>
            </footer>
        </div>
    </body>
</html>
```

Note: no Google Analytics script (dropped per spec). `CURRENT_YEAR` comes from `JINJA_GLOBALS` (Task 8). Root-relative links work identically in dev and prod.

- [ ] **Step 2: Write `macros/entry.html`**

```html
{% macro render_blog_entry(entry) %}
<p class="date">{{ entry.date|datefmt }}</p>
<h1><a href="/{{ entry.url }}">{{ entry.title }}</a></h1>
{% if entry.metadata.get('summary') %}{{ entry.summary }}{% endif %}
<p class="link"><a href="/{{ entry.url }}">Read the full entry...</a></p>
<hr/>
{% endmacro %}
```

- [ ] **Step 3: Write `macros/pagination.html`**

```html
{% macro render_pagination(paginator, page) %}
<div class="pagination">
    {% if page.has_previous() %}
        <a href="/{{ paginator.page(page.previous_page_number()).url }}">&laquo; Previous</a>
    {% else %}
        <span class="disabled">&laquo; Previous</span>
    {% endif %}
    | {{ page.number }} |
    {% if page.has_next() %}
        <a href="/{{ paginator.page(page.next_page_number()).url }}">Next &raquo;</a>
    {% else %}
        <span class="disabled">Next &raquo;</span>
    {% endif %}
</div>
{% endmacro %}
```

- [ ] **Step 4: Write `macros/quotation.html`**

```html
{% macro render_quotation(quote, from_list=False) %}
<blockquote>
{{ quote.content }}
{% if from_list %}<a class="anchor" href="/{{ quote.url }}">#</a>{% endif %}
{% if quote.author %}<p class="author">{{ quote.author }}</p>{% endif %}
{% if quote.location %}<p class="location">{{ quote.location }}</p>{% endif %}
{% if quote.context %}<p class="context">{{ quote.context }}</p>{% endif %}
</blockquote>
{% endmacro %}
```

- [ ] **Step 5: Write `index.html`** (home: all 22 entries, unpaginated)

```html
{% extends "base.html" %}
{% from "macros/entry.html" import render_blog_entry %}
{% block content %}
<div id="content">
{% for article in articles if article.category.name == 'entries' %}
{{ render_blog_entry(article) }}
{% endfor %}
</div>
{% endblock %}
```

- [ ] **Step 6: Write `article.html`** (single entry with prev/next sibling nav)

```html
{% extends "base.html" %}
{% block title %}un blog{% endblock %}
{% block header %}un blog{% endblock %}
{% block content %}
<div id="index">
{% if article.older_entry %}
<p class="archive">Previous entry:<br/>
    <a href="/{{ article.older_entry.url }}">{{ article.older_entry.title }}</a>
</p>
{% endif %}
{% if article.newer_entry %}
<p class="archive">Next entry:<br/>
    <a href="/{{ article.newer_entry.url }}">{{ article.newer_entry.title }}</a>
</p>
{% endif %}
</div>
<div id="content">
<p class="date">{{ article.date|datefmt }}</p>
<h1>{{ article.title }}</h1>
{{ article.content }}
<hr/>
</div>
{% endblock %}
```

`older_entry` = older post (rendered under "Previous entry"), `newer_entry` = newer post (rendered under "Next entry") — matches the live site (verified on where-do-you-see-python-in-10-years: Previous → autopsy-of-a-slow-train-wreck, Next → the-passage-of-time).

- [ ] **Step 7: Write `category.html`** (both `/entries/` and `/inspiration/`)

```html
{% extends "base.html" %}
{% from "macros/entry.html" import render_blog_entry %}
{% from "macros/quotation.html" import render_quotation %}
{% from "macros/pagination.html" import render_pagination %}
{% block title %}{% if category.name == 'entries' %}un blog{% else %}un inspiration{% endif %}{% endblock %}
{% block header %}{% if category.name == 'entries' %}un blog{% else %}un inspiration{% endif %}{% endblock %}
{% block content %}
<div id="content">
{% if category.name == 'entries' %}
{% for article in articles_page.object_list %}
{{ render_blog_entry(article) }}
{% endfor %}
{{ render_pagination(articles_paginator, articles_page) }}
{% else %}
<h1>Words</h1>
<p>A word is a powerful instrument. When well chosen and well used, words can move us, inspire us, and force us into action. The following are a few well crafted passages that have captured my attention over the years.</p>
{% for quote in articles %}
<hr />
{{ render_quotation(quote, from_list=True) }}
{% endfor %}
{% endif %}
</div>
{% endblock %}
```

- [ ] **Step 8: Write `quotation.html`** (single quote page — no prev/next, no date)

```html
{% extends "base.html" %}
{% from "macros/quotation.html" import render_quotation %}
{% block title %}un inspiration{% endblock %}
{% block header %}un inspiration{% endblock %}
{% block content %}
<div id="content">
{{ render_quotation(article) }}
</div>
{% endblock %}
```

- [ ] **Step 9: Write `page.html`**

```html
{% extends "base.html" %}
{% block title %}{{ page.title }}{% endblock %}
{% block header %}{{ page.title }}{% endblock %}
{% block content %}
<div id="content">
{{ page.content }}
</div>
{% endblock %}
```

- [ ] **Step 10: Write `404.html`**

```html
{% extends "base.html" %}
{% block title %}404{% endblock %}
{% block header %}404{% endblock %}
{% block content %}
<div id="content">
<h1>Page not found</h1>
<p>The page you requested could not be found.</p>
</div>
{% endblock %}
```

- [ ] **Step 11: Write the modernized CSS**

Write `themes/cecinestpasun/static/css/cecinestpasun.css` — ported from `assets/static/css/cecinestpasun.css` with HTML5/responsive modernization only: modern doctype handled by templates, drop `body { min-width: 50em }`, keep every class/id selector, palette, and the `#content img.align-left` rule, plus new width classes:

```css
li.current {
    background: #FFD06B;
}

body,
html {
    margin: 0;
    padding: 0;
    background: #ffffea;
    color: #330e00;
    font-family: Georgia, "Times New Roman", Times, serif;
}

a {
    color: #B85D00;
}

#content p.link {
    text-align: right;
}

.wrap {
    margin: 0 auto;
    width: 50em;
    max-width: 100%;
}

#header {
    background: #FFD06B;
}

#header .wrap {
    width: 40em;
    max-width: 100%;
}

#header p {
    margin-top: 0.4em;
    font-style: italic;
    font-size: 0.8em;
    text-align: left;
    padding-bottom: 2em;
}

#header p.title {
    margin: 0;
    padding-bottom: 0;
    font-style: italic;
    font-weight: bold;
    font-size: 250%;
    padding-top: 1em;
}

#main hr {
    margin: 0 9em;
    border: 1px solid #330e00;
}

h1 {
    font-size: 1.2em;
    margin-top: 0;
}

h2 {
    font-size: 1.1em;
    margin-top: 0;
}

h3 {
    font-size: 1.0em;
    margin-top: 0;
}

#nav ul,
#index ul {
    padding-left: 0;
    list-style: none;
}

#nav {
    float: left;
    width: 8em;
    line-height: 1.5em;
}

#nav ul li {
    text-align: right;
}

#nav h3,
#nav p {
    padding: 0 10px 0 0;
}

#main {
    float: right;
    width: 45em;
    max-width: 100%;
    line-height: 1.6em;
    font-size: 90%;
    padding-top: 1.4em;
}

#content {
    width: 35em;
    max-width: 100%;
}

#content h1,
#content h2,
#content h3 {
    padding: 0 1em;
}

#content img.align-left {
    float: left;
    padding-right: 1em;
    padding-top: 1em;
    padding-bottom: 1em;
}

#content img.img-33 {
    width: 33%;
}

#content img.img-50 {
    width: 50%;
}

#content p {
    padding: 0 2em;
}

#content pre {
    padding: 0 2.2em;
    margin: 0.2em;
    background: white;
    color: black;
    border: 1px solid #330e00;
    overflow-x: auto;
}

#content p.date,
#content span.pingback {
    font-variant: small-caps;
    font-size: 0.8em;
    padding-top: 0;
    line-height: 1em;
    padding: 0 1.6em;
    margin: 2em 0 0.5em 0;
}

#content p.date:first-child,
#content h1+p.date {
    margin-top: 0;
}

#content blockquote {
    margin: 0 0 0 3em;
    margin-bottom: 1.2em;
    font-style: italic;
}

#content blockquote p.location,
#content blockquote p.context,
#content blockquote p.author {
    line-height: 1em;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
    text-align: left;
    font-size: 80%;
    padding-left: 5em;
}

#content blockquote p.location {
    font-style: italic;
}

#content ul p {
    padding: 0 0.5em;
}

#index {
    float: right;
    padding: 1em;
    line-height: 1.5em;
    max-width: 9em;
}

#index p {
    padding: 0;
}

#index li {
    padding: 0 0.5em;
}

#footer {
    clear: both;
    font-size: 80%;
    text-align: center;
    padding-top: 2em;
}

#footer p {
    padding: 5px;
    margin: auto;
}

a.anchor {
    float: left;
    margin-left: 1.5em;
    font-size: 150%;
    text-decoration: none;
}

a.mastodon {
    display: none;
}
```

The CSS originally had `text-color: black` (invalid) on `#content pre`; corrected to `color: black`. `.wrap`/`#header .wrap`/`#main`/`#content` get `max-width: 100%` for small screens; `#content pre` gets `overflow-x: auto`. Everything else identical to the current stylesheet.

- [ ] **Step 12: Commit**

```bash
git add themes
git commit -m "feat: add bespoke cecinestpasun Pelican theme"
```

---

### Task 8: Pelican configuration, filters, and plugins

**Files:**
- Create: `pelicanconf.py`
- Create: `publishconf.py`
- Create: `plugins/neighbors.py`
- Create: `plugins/entries_feed.py`
- Create: `requirements.txt`

**Interfaces:**
- Consumes: the converted `content/` tree (Task 6) and the theme (Task 7).
- Produces: a buildable Pelican site whose URLs match the live site exactly, plus the `datefmt` Jinja filter used by the theme, and the `older_entry`/`newer_entry` article attributes used by `article.html`.

- [ ] **Step 1: Write `plugins/neighbors.py`**

```python
"""Per-category previous/next article navigation.

Core Pelican does not provide article neighbors. The community `neighbors`
plugin operates across ALL articles, which would incorrectly link blog posts
to quotes. This plugin restricts navigation to within each category.
"""

from pelican import signals


def set_neighbors(articles_generator):
    # categories is a list of (category, [articles]) at this point.
    # Each article list is sorted newest-first (ARTICLE_ORDER_BY is
    # ('date', 'desc')), so index+1 is the older post and index-1 is newer.
    for _category, articles in articles_generator.categories:
        for index, article in enumerate(articles):
            article.older_entry = articles[index + 1] if index + 1 < len(articles) else None
            article.newer_entry = articles[index - 1] if index - 1 >= 0 else None


def register():
    signals.article_generator_finalized.connect(set_neighbors)
```

- [ ] **Step 2: Write `plugins/entries_feed.py`**

```python
"""Restrict the Atom feed to the entries category only, and render summaries.

The old Lektor feed config (`configs/atom.ini`) emitted only the blog entries
(site.query('/entries')). Pelican's FEED_ATOM includes every article, so we
patch generate_feeds to filter. The Summary metadata is already rendered to
HTML by the Markdown reader (FORMATTED_FIELDS), so the feed description is
readable with no extra work.
"""

from pelican import signals
from pelican.generators import ArticlesGenerator


def patch_feeds():
    original = ArticlesGenerator.generate_feeds

    def patched(self, writer):
        saved = self.articles
        entries = [a for a in saved if a.category.name == "entries"]
        self.articles = entries
        try:
            original(self, writer)
        finally:
            self.articles = saved

    ArticlesGenerator.generate_feeds = patched


def register():
    signals.article_generator_init.connect(lambda gen: patch_feeds())
```

- [ ] **Step 3: Write `pelicanconf.py`**

```python
import datetime

AUTHOR = "Russell Keith-Magee"
SITENAME = "Ceci n'est pas un blog"
SITEURL = ""  # root-relative links in dev; publishconf.py overrides for prod

PATH = "content"
OUTPUT_PATH = "output/"
TIMEZONE = "Australia/Perth"
DEFAULT_LANG = "en"

# Only the Atom feed at /rss/all/
FEED_ATOM = "rss/all/index.html"
FEED_ATOM_URL = "rss/all/"
FEED_RSS = None
CATEGORY_FEED_ATOM = None
CATEGORY_FEED_RSS = None
TRANSLATION_FEED_ATOM = None
TRANSLATION_FEED_RSS = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Content locations
ARTICLE_PATHS = ["entries", "inspiration"]
PAGE_PATHS = ["pages"]
STATIC_PATHS = ["about", "projects", "extra"]
EXTRA_PATH_METADATA = {"extra/CNAME": {"path": "CNAME"}}
IGNORE_FILES = [".DS_Store"]

# URL pinning (preserves every existing URL)
ARTICLE_URL = "{category}/{slug}/"
ARTICLE_SAVE_AS = "{category}/{slug}/index.html"
CATEGORY_URL = "{slug}/"
CATEGORY_SAVE_AS = "{slug}/index.html"
PAGE_URL = "{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"

# Only the entries category is paginated, 10 per page.
DEFAULT_PAGINATION = 10
PAGINATED_TEMPLATES = {"category": 10}
PAGINATION_PATTERNS = (
    (1, "{base_name}/", "{base_name}/index.html"),
    (2, "{base_name}/page/{number}/", "{base_name}/page/{number}/index.html"),
)

# Direct templates we actually use
DIRECT_TEMPLATES = ["index", "404"]

# Suppress pages we do not want
AUTHOR_SAVE_AS = ""
AUTHOR_URL = ""
TAG_SAVE_AS = ""
TAG_URL = ""
CATEGORIES_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
ARCHIVES_SAVE_AS = ""
YEAR_ARCHIVE_SAVE_AS = ""
MONTH_ARCHIVE_SAVE_AS = ""
DAY_ARCHIVE_SAVE_AS = ""

MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.codehilite": {"css_class": "highlight", "guess_lang": False},
        "markdown.extensions.fenced_code": {},
        "markdown.extensions.attr_list": {},
        "markdown.extensions.smart_quotes": {},
    },
    "output_format": "html5",
}

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["neighbors", "entries_feed"]

THEME = "themes/cecinestpasun"
THEME_STATIC_DIR = "static"

_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def datefmt(value):
    """Format like Lektor's '%I:%M %p, %-d %B %Y' but cross-platform."""
    hour = value.hour % 12 or 12
    ampm = "AM" if value.hour < 12 else "PM"
    return f"{hour}:{value.minute:02d} {ampm}, {value.day} {_MONTHS[value.month - 1]} {value.year}"


JINJA_FILTERS = {
    "datefmt": datefmt,
}
JINJA_GLOBALS = {"CURRENT_YEAR": datetime.date.today().year}

# Rebuild everything on each build; determinism over speed.
LOAD_CONTENT_CACHE = False
CACHE_CONTENT = False
```

- [ ] **Step 4: Write `publishconf.py`**

```python
import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *  # noqa: F401,F403

SITEURL = "https://cecinestpasun.com/"
DELETE_OUTPUT_DIRECTORY = True
RELATIVE_URLS = False
```

- [ ] **Step 5: Write `requirements.txt`**

```
pelican==4.10.2
markdown==3.7
pygments==2.19.1
typogrify==2.0.7
pytz==2024.2
pytest==8.3.4
```

(`pytest` is needed to run `tools/test_convert_rst.py`; `typogrify` is pinned per the spec even though the theme does not apply its filter, to keep output byte-faithful.)

- [ ] **Step 6: Verify the site builds**

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pelican content -s pelicanconf.py -o output
```

Expected: build succeeds with no errors; `output/index.html`, `output/entries/`, `output/entries/page/2/`, `output/entries/page/3/`, `output/inspiration/`, all 22 entry dirs, all 15 quote dirs, 4 page dirs, `output/rss/all/index.html`, `output/CNAME`, `output/static/css/cecinestpasun.css`, `output/about/mugshot.png`, `output/projects/beeware.png`, `output/projects/django.png`, `output/about/CurriculumVitae-RussellKeith-Magee.pdf`.

- [ ] **Step 7: Commit**

```bash
git add pelicanconf.py publishconf.py plugins requirements.txt
git commit -m "feat: add Pelican config, filters, and plugins"
```

---

### Task 9: GitHub Actions deployment + CNAME

**Files:**
- Create: `.github/workflows/publish.yml`
- Create: `content/extra/CNAME`
- Modify: `.gitignore` (add `output/` if not already present)

**Interfaces:**
- Consumes: `publishconf.py`, `requirements.txt`, and the `content/` tree.
- Produces: automated deploy of `output/` to GitHub Pages on every push to `main`, serving `cecinestpasun.com`.

- [ ] **Step 1: Write `content/extra/CNAME`**

Write the file with exactly one line:

```
cecinestpasun.com
```

- [ ] **Step 2: Write `.github/workflows/publish.yml`**

```yaml
name: Publish
on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Build site
        run: pelican content -o output -s publishconf.py
      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: output
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 3: Run the test suite and build once more from a clean state**

```bash
rm -rf output
python -m pytest tools/test_convert_rst.py -q
pelican content -s publishconf.py -o output
```

Expected: 24 tests pass; build succeeds; `output/CNAME` contains `cecinestpasun.com`.

- [ ] **Step 4: Commit**

```bash
git add .github content/extra/CNAME .gitignore
git commit -m "ci: deploy site to GitHub Pages on push to main"
```

---

### Task 10: URL inventory verification against the live site

**Files:**
- Create: `tools/urls.txt` — a generated inventory of every output URL (kept for the review; delete before the final commit if you prefer).

**Interfaces:**
- Consumes: the `output/` tree from Task 8/9.
- Produces: evidence that every live URL is produced identically.

- [ ] **Step 1: Generate the output URL inventory**

```bash
(cd output && find . -name index.html | sed 's|^\./||; s|index.html$||; s|/$|/|' | sort) > tools/urls.txt
cat tools/urls.txt | wc -l
```

- [ ] **Step 2: Diff against the expected URL set**

Expected inventory (48 URLs — exact match):

```
/
404.html
about/
colophon/
contact/
entries/
entries/moving-to-lektor/
entries/autopsy-of-a-slow-train-wreck/
entries/doing-right-thing/
entries/end-my-evolution/
entries/even-better-i-thought/
entries/expressing-disappointment-my-government/
entries/ezydvd-store-passwords-clear/
entries/freakboy3742/
entries/getting-hgsubversion-work-under-osx/
entries/how-to-succeed-at-sprinting/
entries/i-can-haz-a-question-or-five/
entries/oh-yeah-i-should-probably-mention/
entries/opposing-preference-deals-right/
entries/personal-funding-and-culture-open-source/
entries/quo-vadimus/
entries/replacement-twitter/
entries/searching-for-a-new-place-to-hang-my-hat/
entries/the-passage-of-time/
entries/week-django/
entries/what-no-comments/
entries/where-do-you-see-python-in-10-years/
entries/yet-another-blog-engine/
entries/page/2/
entries/page/3/
inspiration/
inspiration/a-river-runs-through-it/
inspiration/antoine-de-saint-exupery-ships/
inspiration/arne-naess-mountains/
inspiration/dead-poets-society/
inspiration/eleanor-roosevelt-courage/
inspiration/eugene-oneill/
inspiration/john-maynard-keynes-words/
inspiration/nick-cave-days/
inspiration/nick-cave-truths/
inspiration/plato-republic-child-dark/
inspiration/politics-as-a-vocation/
inspiration/rfk-lawrence/
inspiration/stanley-kubrick-playboy/
inspiration/theodore-roosevelt-critics/
inspiration/west-wing-words/
projects/
rss/all/
```

Verify the inventory by diffing against `ls output/entries/` and `ls output/inspiration/`. (Slugs: 22 entries are exactly the directories present in `/tmp/lektor-content/content/entries/`; 15 quotes from `/tmp/lektor-content/content/inspiration/`.)

- [ ] **Step 3: Verify in-page links on key pages**

- `output/entries/where-do-you-see-python-in-10-years/index.html` contains `<iframe ... youtube.com/embed/ftP5BQh1-YM?start=1238` and the `[Acknowledgement of Country](...)` link rendered as `<a href="...">`.
- `output/entries/autopsy-of-a-slow-train-wreck/index.html` contains the twitter `<blockquote class="twitter-tweet">` and `## Transcript` → `<h2>Transcript</h2>`, `### Humans aren't rational` → `<h3>`.
- `output/entries/getting-hgsubversion-work-under-osx/index.html` contains `<pre>` code blocks with the `$ export` lines.
- `output/entries/moving-to-lektor/index.html` has no `.summary` text (no excerpt) but does show the Author metadata nowhere on-page.
- `output/about/index.html` contains `<img ... src="/about/mugshot.png" ... class="align-left img-33">` and the CV link `href="/about/CurriculumVitae-RussellKeith-Magee.pdf"`.
- `output/entries/index.html` shows 10 entries + `| 1 |` pagination with `Next »` → `/entries/page/2/`.
- `output/entries/page/2/index.html` shows 10 entries, `« Previous` → `/entries/`, `| 2 |`, `Next »` → `/entries/page/3/`.
- `output/entries/page/3/index.html` shows 2 entries (the two oldest), `« Previous` → `/entries/page/2/`, `| 3 |` and no Next link.
- `output/inspiration/index.html` lists all 15 quotes in the exact live order (verify against the order in Task 5), each with a `#` anchor link to its `/inspiration/<slug>/` page.
- `output/index.html` lists all 22 entries (not 10) and does NOT list any quotes.
- `output/entries/moving-to-lektor/index.html` and `output/entries/doing-right-thing/index.html` show correct prev/next pairs (newest post has no "Next entry"; oldest post has no "Previous entry").
- `output/rss/all/index.html` is a valid Atom feed whose `<entry>` items are the 22 entries only (no quotes).

- [ ] **Step 4: Commit the inventory (or remove it)**

```bash
git rm --cached tools/urls.txt 2>/dev/null || true
git commit -am "docs: verify URL inventory matches live site"
```

---

### Task 11: Manual content review

**Files:**
- Modify: any of `content/entries/*.md`, `content/inspiration/*.md`, `content/pages/*.md` that need correction.

**Interfaces:**
- Consumes: the built `output/` (Task 8/9) and the live site https://cecinestpasun.com/.
- Produces: content that renders identically to the live site, with edge cases fixed by hand.

- [ ] **Step 1: Render locally and spot-check against the live site**

Run a local server and open each page:

```bash
python -m http.server 8000 --directory output
```

Open these and compare rendered HTML with the live site (date, links, headings, code blocks, emphasis):

- All 22 entries (`/entries/<slug>/`)
- All 15 quotes (`/inspiration/<slug>/`)
- `/`, `/entries/`, `/entries/page/2/`, `/entries/page/3/`, `/inspiration/`
- `/about/`, `/projects/`, `/contact/`, `/colophon/`

- [ ] **Step 2: Verify known edge cases**

- `content/entries/where-do-you-see-python-in-10-years.md`: the xkcd line renders as literal text (brackets escaped), not a broken image.
- `content/entries/autopsy-of-a-slow-train-wreck.md`: the multiline `Summary:` renders with its emphasis (`*usually*` → `<em>`); the letter divider is an `<hr>`.
- `content/entries/how-to-succeed-at-sprinting.md`: `` `doFooBar()` `` renders as `<code>` (not mangled by smart_quotes).
- `content/entries/replacement-twitter.md`: `` `@freakboy3742` `` renders as `<code>@freakboy3742</code>`.
- Code blocks in `getting-hgsubversion-work-under-osx` show exactly, no smart-quote/typographic mangling inside them.
- Every entry's rendered date matches the live date string exactly (e.g. "11:35 AM, 14 November 2008").
- The masthead + `<title>` of a blog post reads "Ceci n'est pas un blog"; of a quote reads "Ceci n'est pas un inspiration"; of `/` reads "Ceci n'est pas un homepage"; of `/about/` reads "Ceci n'est pas un about page".
- Quotes show no date anywhere.

- [ ] **Step 3: Fix any discrepancies found** by editing the affected `.md` files, then re-run the build (Task 8 Step 6 command) and re-verify.

- [ ] **Step 4: Commit**

```bash
git add content
git commit -m "fix: correct content edge cases found in manual review"
```

---

### Task 12: Final verification and merge to main

**Files:**
- All files on `main`.

**Interfaces:**
- Consumes: everything from Tasks 1–11.
- Produces: a merged, clean-history `main` branch with the site passing all checks.

- [ ] **Step 1: Run the full verification suite**

```bash
python -m pytest tools/test_convert_rst.py -q
rm -rf output
pelican content -s publishconf.py -o output
(cd output && find . -name index.html | sed 's|^\./||; s|index.html$||' | sort) > /tmp/built-urls.txt
wc -l /tmp/built-urls.txt
```

Expected: 24 tests pass; build clean; URL count matches the inventory from Task 10.

- [ ] **Step 2: Confirm clean history and working tree**

```bash
git status
git log --oneline
```

Expected: working tree clean; `main` history contains only the commits from Tasks 1–11.

- [ ] **Step 3: Push and confirm the workflow runs**

```bash
git push origin main
```

Expected: GitHub Actions "Publish" workflow triggers on `main`, the build step succeeds, and the deploy step publishes to `https://cecinestpasun.com`.

- [ ] **Step 4: Final live sanity check**

After the workflow completes, fetch these and confirm HTTP 200:
- `https://cecinestpasun.com/`
- `https://cecinestpasun.com/entries/`
- `https://cecinestpasun.com/entries/page/2/`
- `https://cecinestpasun.com/entries/where-do-you-see-python-in-10-years/`
- `https://cecinestpasun.com/inspiration/arne-naess-mountains/`
- `https://cecinestpasun.com/about/`
- `https://cecinestpasun.com/rss/all/`

- [ ] **Step 5: Update the design spec status** to "Implemented" in `docs/superpowers/specs/2026-08-20-pelican-port-design.md` and commit.

```bash
git add docs/superpowers/specs
git commit -m "docs: mark pelican port design spec as implemented"
```

---

## Self-Review

**Spec coverage:**
- Scope (22 entries, 15 quotes, 4 pages, home, feed): Tasks 5–6 ✓
- URL preservation: Task 8 config + Task 10 inventory ✓
- Visual design / same palette: Task 7 ✓
- Deployment / GH Actions on main / CNAME: Task 9 ✓
- Automated conversion + manual review: Tasks 2–6 + Task 11 ✓
- Feed at `/rss/all/`: Task 8 (FEED_ATOM) + entries_feed plugin ✓
- Drop analytics: Task 7 (no GA in base.html) ✓
- Metadata mapping incl. `DisplayTitle`, quote `Author/Location/Context`, `Summary`: Tasks 5 + 8 ✓
- TIMEZONE Australia/Perth: Task 8 ✓
- Pagination only on category, 10/page: Task 8 ✓
- Typography/smart quotes: Task 8 MARKDOWN + Task 11 review ✓

**Placeholder scan:** no TBD/TODO; every step has concrete code or commands.

**Type consistency:** `parse_lr`, `rst_to_markdown`, `write_entry/write_quote/write_page`, `QUOTE_DATES`, `older_entry`/`newer_entry`, `datefmt`, `articles_page/articles_paginator` are defined once and referenced identically throughout. `render_pagination` signature `(paginator, page)` matches its single call site in `category.html`.