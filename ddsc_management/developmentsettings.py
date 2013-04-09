import os

from lizard_ui.settingshelper import setup_logging

from ddsc_management.settings import *  # NOQA

DEBUG = True

# By default, var/log/django.log gets WARN level logging, the console gets
# DEBUG level logging.
LOGGING = setup_logging(BUILDOUT_DIR)

# ENGINE: 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
# In case of geodatabase, prepend with:
# django.contrib.gis.db.backends.(postgis)
DATABASES = {
    # If you want to use another database, consider putting the database
    # settings in localsettings.py. Otherwise, if you change the settings in
    # the current file and commit them to the repository, other developers will
    # also use these settings whether they have that database or not.
    # One of those other developers is Jenkins, our continuous integration
    # solution. Jenkins can only run the tests of the current application when
    # the specified database exists. When the tests cannot run, Jenkins sees
    # that as an error.
    'default': {
        'NAME': 'ddsc_management',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': 'buildout',
        'PASSWORD': 'buildout',
        'HOST': '',  # empty string for localhost.
        'PORT': '',  # empty string for default.
        },
    }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BUILDOUT_DIR, 'var', 'cache'),
    }
}

# SSO
SSO_STANDALONE = False
SSO_ENABLED = True
# A key identifying this client. Can be published.
SSO_KEY = 'WSX'
# A *secret* shared between client and server.
# Used to sign the messages exchanged between them.
SSO_SECRET = 'QAZ'
# URL used to redirect the user to the SSO server
# Note: needs a trailing slash
SSO_SERVER_PUBLIC_URL = 'http://localhost:8001/'
# URL used for server-to-server communication
# Note: needs a trailing slash
SSO_SERVER_PRIVATE_URL = 'http://localhost:8001/'

WEBCLIENT = 'http://localhost:8000'
