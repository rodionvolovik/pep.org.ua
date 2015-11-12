# coding: utf-8
"""
Django settings for pepdb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# For stupid sitemaps
SITE_URL = "http://pep.org.ua"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*37e&4-qi$f+paw#=me8opo$uk7y%d$c@crd++q89$4y!g$p!e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'grappelli',
    'grappelli_modeltranslation',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_markdown',

    'pipeline',
    'django_jinja',
    'django_jinja.contrib._humanize',
    'django_jinja.contrib._easy_thumbnails',

    'compressor',
    'taggit',
    'modelcluster',

    'wagtail.wagtailcore',
    'wagtail.wagtailadmin',
    'wagtail.wagtaildocs',
    'wagtail.wagtailsnippets',
    'wagtail.wagtailusers',
    'wagtail.wagtailimages',
    'wagtail.wagtailembeds',
    'wagtail.wagtailsearch',
    'wagtail.wagtailredirects',
    'wagtail.wagtailforms',

    'cms_pages',
    'qartez',
    'captcha',
    'core',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)

from django_jinja.builtins import DEFAULT_EXTENSIONS

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension": ".jinja",
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.core.context_processors.i18n",
                "django.core.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.feedback_processor",
                "cms_pages.context_processors.menu_processor"
            ),
            "extensions": DEFAULT_EXTENSIONS + [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.with_",
                "jinja2.ext.i18n",
                "jinja2.ext.autoescape",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
                "pipeline.jinja2.ext.PipelineExtension"
            ]
        }
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.core.context_processors.i18n",
                "django.core.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.feedback_processor",
                "cms_pages.context_processors.menu_processor"
            )
        },
        "APP_DIRS": True
    },
]

GRAPPELLI_ADMIN_TITLE = u"(Секретна) база даних PEP"

ROOT_URLCONF = 'pepdb.urls'

WSGI_APPLICATION = 'pepdb.wsgi.application'

DATABASES = {
    'default': {
        # Strictly PostgreSQL
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}

# Internationalization
LANGUAGE_CODE = 'uk'

gettext = lambda s: s
LANGUAGES = (
    ('uk', gettext('Ukrainian')),
    ('en', gettext('English')),
)


TIME_ZONE = 'Europe/Kiev'

USE_I18N = True
USE_L10N = True
USE_TZ = True


LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

DATE_FORMAT = "d.m.Y"
MONTH_YEAR_DATE_FORMAT = "m.Y"
YEAR_DATE_FORMAT = "Y"

DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.jinja'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = '/media/'


JINJA2_EXTENSIONS = ["pipeline.jinja2.ext.PipelineExtension"]

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'pipeline.finders.PipelineFinder',
)

PIPELINE_CSS = {
    'css_all': {
        'source_filenames': (
            'css/bootstrap.min.css',
            'css/ripples.min.css',
            'css/animate.css',
            'css/timeline.css',
            'css/style.css',
            'css/responsive.css',
        ),
        'output_filename': 'css/merged.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },

    'css_print': {
        'source_filenames': (
            'css/print.css',
        ),
        'output_filename': 'css/merged_print.css',
        'extra_context': {
            'media': 'print',
        },
    },
}


PIPELINE_JS = {
    'js_all': {
        'source_filenames': (
            "js/jquery-1.10.2.js",
            "js/bootstrap.min.js",
            "js/bootstrap3-typeahead.min.js",
            "js/ripples.min.js",
            "js/pep.js",
        ),
        'output_filename': 'js/merged.js',
    }
}

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.uglifyjs.UglifyJSCompressor'

# django-compressor settings (for a fucking wagtail)
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

LOGIN_URL = "/admin/login/"
WAGTAIL_SITE_NAME = 'PEP'


# Setup Elasticsearch default connection
ELASTICSEARCH_CONNECTIONS = {
    'default': {
        'hosts': 'localhost',
        'timeout': 20
    }
}

THUMBNAIL_ALIASES = {
    '': {
        'small_avatar': {'size': (100, 100), 'crop': True},
        'avatar': {'size': (128, 128), 'crop': True},
    },
}

CATALOG_PER_PAGE = 6

RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""
NOCAPTCHA = True
RECAPTCHA_USE_SSL = True

try:
    from local_settings import *
except ImportError:
    pass

# Init Elasticsearch connections
from elasticsearch_dsl import connections
connections.connections.configure(**ELASTICSEARCH_CONNECTIONS)
