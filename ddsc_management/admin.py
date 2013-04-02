# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from __future__ import unicode_literals

from django.contrib import admin

from piston.models import Consumer, Nonce, Resource, Token

from ddsc_management import models

# Hide Piston:
admin.site.unregister(Consumer)
admin.site.unregister(Nonce)
admin.site.unregister(Resource)
admin.site.unregister(Token)
