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


def on_article_generator_init(generator):
    patch_feeds()


def register():
    signals.article_generator_init.connect(on_article_generator_init)