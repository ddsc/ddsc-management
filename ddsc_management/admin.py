# (c) Nelen & Schuurmans. MIT licensed, see LICENSE.rst.

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from piston.models import Consumer, Nonce, Resource, Token

from lizard_auth_client.client import sso_get_users_django


class DdscUserAdmin(UserAdmin):
    actions = ['synchronize_with_sso_server']

    def synchronize_with_sso_server(self, request, queryset):
        sso_get_users_django()
        # TODO: process the response

    synchronize_with_sso_server.short_description = _(
        "Synchronize with SSO server"
    )


# Override Django auth's UserAdmin:

admin.site.unregister(User)
admin.site.register(User, DdscUserAdmin)

# Hide Piston:

admin.site.unregister(Consumer)
admin.site.unregister(Nonce)
admin.site.unregister(Resource)
admin.site.unregister(Token)
