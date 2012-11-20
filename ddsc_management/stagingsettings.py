from ddsc_management.settings import *

DATABASES = {
    # Changed server from production to staging
    'default': {
        'NAME': 'ddsc_management',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': 'ddsc_management',
        'PASSWORD': 'bbbbbbbbb',
        'HOST': 's-ddsc-ws-d1.external-nens.local',
        'PORT': '5432',
        },
    }

# TODO: add staging gauges ID here.
UI_GAUGES_SITE_ID = ''  # Staging has a separate one.


try:
    from ddsc_management.localstagingsettings import *
    # For local staging overrides (DB passwords, for instance)
except ImportError:
    pass
