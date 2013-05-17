# Base Django settings, suitable for production.
# Imported (and partly overridden) by developmentsettings.py which also
# imports localsettings.py (which isn't stored in svn).  Buildout takes care
# of using the correct one.
# So: "DEBUG = TRUE" goes into developmentsettings.py and per-developer
# database ports go into localsettings.py.  May your hear turn purple if you
# ever put personal settings into this file or into developmentsettings.py!

import os

from django.conf import global_settings as DEFAULT_SETTINGS
import djcelery

from lizard_ui.layout import Action
from lizard_ui.settingshelper import STATICFILES_FINDERS
from lizard_ui.settingshelper import setup_logging

STATICFILES_FINDERS = STATICFILES_FINDERS

# Set matplotlib defaults.
# Uncomment this when using lizard-map.
# import matplotlib
# # Force matplotlib to not use any Xwindows backend.
# matplotlib.use('Agg')
# import lizard_map.matplotlib_settings

# SETTINGS_DIR allows media paths and so to be relative to this settings file
# instead of hardcoded to c:\only\on\my\computer.
SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))

# BUILDOUT_DIR is for access to the "surrounding" buildout, for instance for
# BUILDOUT_DIR/var/static files to give django-staticfiles a proper place
# to place all collected static files.
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))

# Set up logging. No console logging. By default, var/log/django.log and
# sentry at 'WARN' level.
LOGGING = setup_logging(BUILDOUT_DIR, console_level=None, sentry_level='WARN')

# Production, so DEBUG is False. developmentsettings.py sets it to True.
DEBUG = False
# Show template debug information for faulty templates.  Only used when DEBUG
# is set to True.
TEMPLATE_DEBUG = True

# ADMINS get internal error mails, MANAGERS get 404 mails.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# TODO: Switch this to the real production database.
# ^^^ 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
# In case of geodatabase, prepend with:
# django.contrib.gis.db.backends.(postgis)
DATABASES = {
    # Note: public repo, use localsettings!
    # override me in localsettings
}
POSTGIS_VERSION = (1, 5, 3)

# Almost always set to 1.  Django allows multiple sites in one database.
SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name although not all
# choices may be available on all operating systems.  If running in a Windows
# environment this must be set to the same as your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl-NL'
# For at-runtime language switching.  Note: they're shown in reverse order in
# the interface!
LANGUAGES = (
    ('nl', 'Nederlands'),
    ('en', 'English'),
)
# If you set this to False, Django will make some optimizations so as not to
# load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds user-uploaded media.
MEDIA_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'media')
# Absolute path to the directory where django-staticfiles'
# "bin/django build_static" places all collected static files from all
# applications' /media directory.
STATIC_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
MEDIA_URL = '/media/'
# URL for the per-application /media static files collected by
# django-staticfiles.  Use it in templates like
# "{{ MEDIA_URL }}mypackage/my.css".
STATIC_URL = '/static_media/'

# Make this unique, and don't share it with anybody.
# override me in localsettings
SECRET_KEY = ''

ROOT_URLCONF = 'ddsc_management.urls'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

CACHES = {
    'default': {
        'KEY_PREFIX': BUILDOUT_DIR,
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

MIDDLEWARE_CLASSES = (
    # Gzip needs to be at the top.
    'django.middleware.gzip.GZipMiddleware',
    # Below is the default list, don't modify it.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Lizard security.
    'tls.TLSRequestMiddleware',
    'lizard_security.middleware.SecurityMiddleware',
    )

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',  # django-tables2, treebeard
)

# Customize branding by overriding base_site.html
TEMPLATE_DIRS = (
    os.path.join(SETTINGS_DIR, 'templates')
)

INSTALLED_APPS = (
    'ddsc_management',
    'lizard_auth_client',
    'lizard_security',  # before lizard_ui!
    'ddsc_core',  # after lizard_security!
    'lizard_ui',  # after lizard_security!
    'lizard_map',
    'lizard_maptree',
    'lizard_wms',
    'ddsc_site', # depends on lizard_wms & lizard_security
    'treebeard',
    'floppyforms',
    'south',
    'compressor',
    'staticfiles',
    'raven.contrib.django',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django_tables2',
    'djcelery',
    'gunicorn',
)

# TODO: Put your real url here to configure Sentry.
# override me in localsettings
SENTRY_DSN = None

# override me in localsettings
UI_GAUGES_SITE_ID = ''

LIZARD_SITE = 'http://test.dijkdata.nl/'
MANAGEMENT_SITE = 'http://test.beheer.dijkdata.nl/'

UI_SITE_ACTIONS = [
    Action(
        name="Kaart",
        url=LIZARD_SITE,
        # description="",
        # icon="icon-info-sign",
        # klass="has_popover_south"
    ),
    Action(
        name="Grafieken",
        url=LIZARD_SITE,
    ),
    Action(
        name="Overzichten",
        url="/overviews/",
    ),
    Action(
        name="Beheer",
        # url=MANAGEMENT_SITE,
        # description="",
        # icon="icon-info-sign",
        # klass="has_popover_south"
    ),
    ]

# Celery
djcelery.setup_loader()
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# Tell Django about the user profile
AUTH_PROFILE_MODULE = "ddsc_management.UserProfile"

# Enabling our SSO server as an authentication backend, would grant all DDSC
# users access to this management website. This requires further protection
# of views, etc, and some serious testing. Disable SSO until then.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
#   'lizard_auth_client.backends.SSOBackend',
#   'lizard_security.backends.DDSCPermissionBackend',
)

AUTH_PROFILE_MODULE = 'ddsc_site.UserProfile'

try:
    # For local overrides (DB passwords, for instance)
    from ddsc_management.localsettings import *  # NOQA
    # for ddsc, the following stuff need to be defined in localsettings.py,
    # and shared across the various Django instances.
    #DATABASES
    #SECRET_KEY
    #UI_GAUGES_SITE_ID
    #SESSION_COOKIE_DOMAIN
    #SESSION_COOKIE_NAME
    #DATABASE_ROUTERS
    #BROKER_URL
except ImportError:
    pass
