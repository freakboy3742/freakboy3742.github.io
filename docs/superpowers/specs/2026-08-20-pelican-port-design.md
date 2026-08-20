# Design: Port cecinestpasun.com from Lektor to Pelican

Date: 2026-08-20
Status: Implemented

## Goal

Port the personal blog of Russell Keith-Magee (cecinestpasun.com) from Lektor +
reStructuredText to Pelican + Markdown. The new site starts with clean git
history on the `main` branch. Existing Lektor content remains untouched on the
`lektor` branch as the source of truth.

## Decisions (confirmed with user)

- **Scope:** Full port - all 22 blog posts, 15 inspirational quotes, 4 static
  pages (About, Projects, Contact, Colophon), home page, and Atom feed.
- **URLs:** Preserve every existing URL exactly. Existing external links and
  bookmarks must not break.
- **Visual design:** Modernize markup (HTML5, responsive) while keeping the
  current look and feel (same palette, layout, header/footer). Not a redesign.
- **Deployment:** Continue GitHub Pages on the same repo
  (`freakboy3742/freakboy3742.github.io`) with the `cecinestpasun.com` CNAME,
  via a new GitHub Actions workflow on `main`.
- **Content conversion:** Automated reST -> Markdown conversion script plus
  manual review of every converted file.
- **Feed location:** Keep the Atom feed at `/rss/all/`.
- **Analytics:** Drop the old Google Analytics tracker (`ga.js` was shut down
  in 2023). Do not add a replacement.

## Approach

Approach A - "drop-in port": custom Pelican theme reproducing the site's
layout, Markdown content, pinned URLs, GitHub Actions deploy. Chosen over
using an existing community theme (would lose the site's look) and over
keeping reST content (contradicts the Markdown goal).

## Repository structure (`main` branch)

```
pelicanconf.py              # site config
publishconf.py              # production settings
requirements.txt            # pelican, markdown, pygments, typogrify, pytz (pinned)
tools/convert_rst.py        # one-off reST -> Markdown converter (not run in CI)
content/
  entries/<slug>.md         # 22 blog posts -> /entries/<slug>/
  inspiration/<slug>.md     # 15 quotes    -> /inspiration/<slug>/
  pages/{about,projects,contact,colophon}.md   # -> /<slug>/
  images/                   # mugshot.png, beeware.png, django.png
themes/cecinestpasun/
  templates/                # base, index, article, category, page, 404 + macros
  static/css/cecinestpasun.css   # modernized, responsive, same palette
.github/workflows/publish.yml
```

## Routing rules

Preserves every existing URL byte-for-byte:

- Blog posts -> category **entries**:
  `ARTICLE_URL = 'entries/{slug}/'`, `ARTICLE_SAVE_AS = 'entries/{slug}/index.html'`
- Quotes -> category **inspiration**:
  `ARTICLE_URL = 'inspiration/{slug}/'`
- Archive lists -> category archives at `/entries/` (paginated 10/page,
  matching Lektor) and `/inspiration/`
- Pages -> `PAGE_URL = '{slug}/'`, `PAGE_SAVE_AS = '{slug}/index.html'`
  -> `/about/`, `/projects/`, `/contact/`, `/colophon/`
- Home `/` -> full blog roll of all posts (Lektor's home lists all entries,
  no pagination)
- Atom feed -> `FEED_ATOM = 'rss/all/index.html'` -> served at `/rss/all/`
- Quotes carry `author`, `location`, `context` metadata; no visible date
  (Lektor shows none)

## Metadata mapping

| Lektor field | Pelican metadata |
|---|---|
| `title` | `Title:` |
| `pub_date` | `Date:` |
| `excerpt` | `Summary:` |
| `modify_title: yes` | `DisplayTitle: yes` (page renders own title) |
| `body` / `text` | article/page body |
| quote `author`,`location`,`context` | `Author:`,`Location:`,`Context:` |

## Content conversion rules (reST -> Markdown)

| reST (Lektor) | Markdown |
|---|---|
| `Title` / `~~~~` underline headings | ATX `##` headings (1:1 level mapping) |
| `` `text <url>`_ `` and `` `text <url>`__ `` | `[text](url)` |
| `` `phrase` `` (no link) | `*phrase*` |
| `.. image:: x.png` + `:width:`/`:align:` | `![alt](path)`, `{: .align-left}` for alignment |
| `::` literal blocks | fenced code blocks with language hint |
| `----` horizontal rule | `---` |
| `.. raw:: html` (2 YouTube iframes) | inline raw HTML |
| special characters | preserved verbatim |

Source file mapping:

- `content/entries/<slug>/contents.lr` -> `content/entries/<slug>.md`
- `content/inspiration/<slug>/contents.lr` -> `content/inspiration/<slug>.md`
- `content/<page>/contents.lr` -> `content/pages/<page>.md`
- Images moved to `content/images/`, references updated

Manual review of every converted file against the live site (pub date, links,
emphasis, code blocks). Edge cases (e.g. reST roles in the long PyCon talk)
fixed by hand. Lektor content untouched as source of truth.

## Theme

Custom Jinja2 theme in `themes/cecinestpasun/`, preserving identity with
HTML5 modernization:

- Same structure: yellow `#FFD06B` header with italic "Ceci n'est pas..."
  masthead, fixed-width body, right-floated nav, footer with copyright +
  Mastodon link.
- HTML5 semantics (`<header>`, `<nav>`, `<main>`, `<footer>`), modern
  doctype, viewport meta, UTF-8, responsive CSS (drop `min-width:50em`).
- Palette kept: `#ffffea`, `#330e00`, `#B85D00`, `#FFD06B`; Georgia serif.
- Templates:
  - `index.html` - home: all posts (title + excerpt + "Read the full
    entry..." link, `.date` small-caps)
  - `category.html` - `/entries/` paginated (10, "« Previous | N | Next »")
    and `/inspiration/` list
  - `article.html` - post: date, title h1, body, prev/next sibling nav
  - `quotation` - `<blockquote>` with author/location/context styling
  - `page.html`, `404.html`, macros for entry + pagination

## Build / config

- `SITENAME = "Ceci n'est pas un blog"`,
  `SITEURL = "https://cecinestpasun.com/"`,
  `AUTHOR = "Russell Keith-Magee"`, `DEFAULT_LANG = "en"`
- `TIMEZONE = "Australia/Perth"` (source dates local)
- `DEFAULT_PAGINATION = 10`; pagination applies to category only
- `STATIC_PATHS`: theme CSS + `content/images`; ignore `.DS_Store`
- `MARKDOWN`: `codehilite` (fenced code), `attr_list` (image alignment),
  `smart_quotes`
- Atom feed only at `/rss/all/`
- Nav hand-written in `base.html` exactly as today (Home, About Me, Blog,
  Projects, Inspiration, Contact, Colophon)

## CI / deployment

`.github/workflows/publish.yml` on branch `main`:

1. `actions/checkout`
2. Set up Python 3.x, `pip install -r requirements.txt`
3. `pelican content -o output -s publishconf.py`
4. `actions/upload-pages-artifact` with `output/` -> `actions/deploy-pages`
5. Repo Pages configured for GH Actions source, serving `cecinestpasun.com`
   (CNAME preserved)

Old Lektor deploy flow (lektor deploy ghpages) replaced entirely.

## Git / branch plan

- Clean history on `main`; `lektor` branch untouched (content source of
  truth / rollback).
- `master` branch is stale (syncs to lektor); not touched.

## Local dev

`pelican --listen` (or `pelican -r` watch) to preview before pushing.