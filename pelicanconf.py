#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Dariusz Dwornikowski'
SITENAME = u'Blog'
SITEURL = '//tdi.github.io'
# USER_LOGO_URL = 'http://www.cs.put.poznan.pl/ddwornikowski/_images/darek.png'
TAGLINE = 'Computer Scientist, Admin, Debian Maintainer'

PATH = 'content'
DISQUS_SITENAME = 'tdiblog'
TIMEZONE = 'Europe/Warsaw'

MENUITEMS = [('all', '/blog/archives.html')]

TAGS_URL='tags.html'

CATEGORIES_URL='categories.html'
ARCHIVES_URL='archives.html'
DEFAULT_LANG = u'en'
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'

# Feed generation is usually not desired when developing
#FEED_ALL_ATOM = None
#CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
SUMMARY_MAX_LENGTH = 40

THEME = 'svbhack'
# Blogroll
LINKS = (('Debian DDPO', 'https://qa.debian.org/developer.php?login=dariusz.dwornikowski%40cs.put.poznan.pl'),
        ('Home Page', 'http://www.cs.put.poznan.pl/ddwornikowski/'), 
        ('About me', 'http://www.cs.put.poznan.pl/ddwornikowski/'), 
        )

# Social widget
# SOCIAL = (('twitter', '7d1'),
          # ('KOZA', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
