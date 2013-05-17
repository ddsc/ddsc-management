# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from __future__ import unicode_literals

from urllib import urlencode
import logging

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.list import MultipleObjectMixin
from django_tables2 import SingleTableMixin

from lizard_ui.layout import Action
from lizard_ui.views import UiView

from ddsc_core import models

from ddsc_management.tables import UserTable

logger = logging.getLogger(__name__)


class BaseView(UiView):
    action = None

    @property
    def home_breadcrumb_element(self):
        home = super(BaseView, self).home_breadcrumb_element
        home.url = reverse('ddsc_management.summary')
        return home

    @property
    def content_actions(self):
        return [
            Action(
                name=_('Overviews'),
                description=_('View overviews (login required).'),
                url=reverse('ddsc_management.overviews'),
                icon=''
            ),
            Action(
                name=_('Admin'),
                description=_('Manage the database (login required).'),
                url=reverse('admin:index'),
                icon=''
            ),
        ]

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        context['action'] = self.action
        return context


class OverviewsView(BaseView):
    """Display a list of links to administrative reports."""
    template_name = 'ddsc_management/overviews.html'
    page_title = 'Overviews'

    # TODO: implement a more fine-grained access control?
    @method_decorator(permission_required('is_superuser'))
    def dispatch(self, *args, **kwargs):
        return super(OverviewsView, self).dispatch(*args, **kwargs)


class UsersView(BaseView, SingleTableMixin, MultipleObjectMixin):
    """Lists all users and their roles."""
    template_name = 'ddsc_management/users.html'
    page_title = 'Users'
    model = User
    table_class = UserTable

    # TODO: implement a more fine-grained access control?
    @method_decorator(permission_required('is_superuser'))
    def dispatch(self, *args, **kwargs):
        return super(UsersView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Note that both BaseView and SingleTableMixin
        # override the `get_context_data` function.
        context = super(UsersView, self).get_context_data(**kwargs)
        table = self.get_table()
        context[self.get_context_table_name(table)] = table
        return context
