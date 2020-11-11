#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'Tom Augspurger'
SITENAME = 'datasframe'
SITEURL = 'https://tomaugspurger.github.com'

PATH = 'content'

TIMEZONE = 'US/Central'

DEFAULT_LANG = 'en'

# Theme
THEME="pelican-hss"
CSS_FILE = "main.css"
STATIC_PATHS = [
    "images/",
    "extras/",
    "modern_2_method_chaining_files/",
    "Indexes_files/",
    "modern_2_method_chaining_files/",
    "modern_4_performance_files/",
    "modern_5_tidy_files/",
    "modern_6_visualization_files/",
    "modern_7_timeseries_files/",
    "modern-pandas-08_files",
]

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_RSS = "feed"

# Blogroll
# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#           ('Another social link', '#'),)

DEFAULT_PAGINATION = 10
RELATIVE_URLS = True
EXTRA_PATH_METADATA = {
    "extras/custom.css": {"path": "theme/css/custom.css"},
}
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {},
    },
    'output_format': 'html5',
}
