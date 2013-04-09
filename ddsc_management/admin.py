# (c) Nelen & Schuurmans. MIT licensed, see LICENSE.rst.

from __future__ import unicode_literals

import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import ugettext as _
from piston.models import Consumer, Nonce, Resource, Token

from ddsc_management.models import UserProfile
from lizard_auth_client.client import sso_get_users_django

logger = logging.getLogger(__name__)


class DdscUserAdmin(UserAdmin):
    """Admin action for synchronizing users with our SSO server.

    Users will have no password set (its unusable, not blank),
    because authentication is still done via the SSO server.
    Users are needed locally for authorization purposes.

    See: https://github.com/lizardsystem/lizard-auth-server
    See: https://github.com/lizardsystem/lizard-auth-client

    """
    actions = ['synchronize_with_sso_server']
    list_display = UserAdmin.list_display + ('has_usable_password', )

    def has_usable_password(self, user):
        return user.has_usable_password()

    has_usable_password.boolean = True  # Display as icon
    has_usable_password.short_description = _('has_usable_password')

    @transaction.commit_on_success
    def synchronize_with_sso_server(self, request, queryset):
        logger.debug("Synchronizing users with SSO server")
        for sso_user in sso_get_users_django():
            self.synchronize_sso_user(sso_user)

    synchronize_with_sso_server.short_description = _(
        "Synchronize with SSO server"
    )

    def synchronize_sso_user(self, sso_user):
        """Create or update a local user.

        sso_user -- a dict with user information.
        return True/False if a user was created/updated.

        """
        username = sso_user['username']
        logger.debug("Synchronizing user {}".format(username))

        # In the unlikely event of a username that is renamed, we will have
        # a problem when using this property for synchronizing. The remote
        # primary key is even less likely to change, so let's use that.
        # Note that usernames can be changed via the Django admin.

        try:

            sso_user_pk = sso_user['pk']
            profile = UserProfile.objects.get(sso_user_pk=sso_user_pk)
            local_user = profile.user

        except UserProfile.DoesNotExist:

            try:

                # If there already exists a local user with the same
                # username, e.g. `admin`, let's assume that it was
                # created with a good reason: do not synchronize.

                local_user = User.objects.get(username=username)
                logger.debug("Skipping user {}".format(username))
                return

            except User.DoesNotExist:

                # Create a new user having an unusable password.
                # Store the remote primary key in its profile.

                local_user = User.objects.create_user(username)
                UserProfile(user=local_user, sso_user_pk=sso_user_pk).save()

        local_user.username = username
        local_user.first_name = sso_user.get('first_name')
        local_user.last_name = sso_user.get('last_name')
        local_user.email = sso_user.get('email')
        local_user.is_active = sso_user.get('is_active', False)
        local_user.is_superuser = sso_user.get('is_superuser', False)
        local_user.is_superuser = sso_user.get('is_staff', False)
        local_user.date_joined = sso_user.get('created_at')

        # TODO: synchronize user profile as well?
        # TODO: synchronize permissions as well?

        local_user.save()


# Override Django auth's UserAdmin:

admin.site.unregister(User)
admin.site.register(User, DdscUserAdmin)

# Register others:

admin.site.register(UserProfile)

# Hide Piston:

admin.site.unregister(Consumer)
admin.site.unregister(Nonce)
admin.site.unregister(Resource)
admin.site.unregister(Token)
