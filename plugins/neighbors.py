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