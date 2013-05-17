# (c) Nelen & Schuurmans. BSD licensed, see LICENSE.rst.

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='ddsc_management_user')
    sso_user_pk = models.IntegerField(
        help_text="Primary key of this user at the SSO server",
        unique=True,
        verbose_name="SSO pk",
    )

    class Meta:
        ordering = ("user__username", )

    def __unicode__(self):
        return unicode(self.user)
