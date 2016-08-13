#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Dariusz Dwornikowski'
SITENAME = u'Blog'
SITEURL = '//tdi.github.io'
TAGLINE = 'Computer Scientist, Admin, Debian Developer, CTO at Tenesys, AWS certified'

PATH = 'content'
DISQUS_SITENAME = 'tdiblog'
TIMEZONE = 'Europe/Warsaw'
LOCALE = ('en_US.utf8')
GOOGLE_ANALYTICS_ID = 'UA-1656033-10'
GOOGLE_ANALYTICS_PROP = 'auto'

MENUITEMS = [('all', '/blog/archives.html')]
TAG_CLOUD_STEPS = 4
TAG_CLOUD_MAX_ITEMS = 100
TAGS_URL='tags.html'

CATEGORIES_URL='categories.html'
ARCHIVES_URL='archives.html'
DEFAULT_LANG = u'en'
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'

PLUGIN_PATHS = ['/home/tdi/dev/pelican-plugins']
PLUGINS = ['sitemap']
ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}



# Feed generation is usually not desired when developing
#FEED_ALL_ATOM = None
#CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
SUMMARY_MAX_LENGTH = 40

THEME = 'svbhack'
# Blogroll
LINKS = (('Debian DDPO', 'https://qa.debian.org/developer.php?login=dariusz.dwornikowski%40cs.put.poznan.pl'),
        ('Github', 'https://github.com/tdi'), 
        ('Debian Poznań', 'https://wiki.debian.org/LocalGroups/DebianPoz'), 
        ('My company', 'http://tenesys.pl'), 
        ('About me', 'http://www.cs.put.poznan.pl/ddwornikowski/'), 
        )

# Social widget
# SOCIAL = (('twitter', '7d1'),
          # ('KOZA', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True