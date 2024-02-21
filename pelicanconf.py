#!/usr/bin/env python3

AUTHOR = "anon"
SITENAME = 'openage dev updates'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Berlin'

DEFAULT_LANG = 'en'

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
DISPLAY_PAGES_ON_MENU = False

THEME = "theme/"

LINKS = (
    ('openage', 'https://openage.dev/'),
    ('chat', 'https://matrix.to/#/#sfttech:matrix.org'),
    ('blog source', 'https://github.com/SFTtech/openage-blog/'),
)

EXTLINKS = [
    ('source code', 'https://github.com/SFTtech/openage', 'images/github.svg'),
]

SOCIAL = (
    ('github', 'https://github.com/SFTtech/openage'),
    ('reddit', 'https://reddit.com/r/openage'),
)

DEFAULT_PAGINATION = 5
DEFAULT_CATEGORY = "blog"

RELATIVE_URLS = True

EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
}

STATIC_PATHS = list(EXTRA_PATH_METADATA.keys())
STATIC_PATHS += ['images']


MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'linenums': True
        },
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
    },
    'output_format': 'html5',
}
