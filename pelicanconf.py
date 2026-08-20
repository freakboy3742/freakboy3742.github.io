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
FEED_ALL_ATOM = None
FEED_ALL_ATOM_URL = None
FEED_ALL_RSS = None
CATEGORY_FEED_ATOM = None
CATEGORY_FEED_RSS = None
TRANSLATION_FEED_ATOM = None
TRANSLATION_FEED_RSS = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Content locations
ARTICLE_PATHS = ["entries", "inspiration"]
PAGE_PATHS = ["pages"]
STATIC_PATHS = ["about", "projects", "extra", "entries/images"]
EXTRA_PATH_METADATA = {"extra/CNAME": {"path": "CNAME"}}
IGNORE_FILES = [".DS_Store"]

# URL pinning (preserves every existing URL).
# Slug = filename so URLs match the Lektor folder names (live site paths).
SLUGIFY_SOURCE = "basename"
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
        "markdown.extensions.smarty": {},
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