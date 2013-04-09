# (c) Nelen & Schuurmans. BSD licensed, see LICENSE.rst.

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    sso_user_pk = models.IntegerField(
        help_text="Primary key at SSO server",
        unique=True,
    )
