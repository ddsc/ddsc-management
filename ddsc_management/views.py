# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormMixin, FormView, ProcessFormView, BaseFormView, ModelFormMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from django.views.decorators.cache import never_cache

from lizard_ui.views import UiView
from lizard_ui.layout import Action

from ddsc_core.models import Timeseries

from ddsc_management import forms
from ddsc_management.utils import get_datatables_records
from ddsc_management.generic_views import MySingleObjectMixin, ViewContextFormMixin, ProcessFormMixin, ModelDataSourceView

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
                name=_('Summary'),
                description=_('View summarized infomation.'),
                url=reverse('ddsc_management.summary'),
                icon=''
            ),
            Action(
                name=_('Alarms'),
                description=_('Manage alarms.'),
                url=reverse('ddsc_management.alarms'),
                icon=''
            ),
            Action(
                name=_('Import data'),
                description=_('Manually import data from csv files.'),
                url=reverse('ddsc_management.import'),
                icon=''
            ),
            Action(
                name=_('Timeseries'),
                description=_('Manage timeseries.'),
                url=reverse('ddsc_management.timeseries.list'),
                icon=''
            ),
            Action(
                name=_('Manage sources'),
                description=_('Manage sources.'),
                url=reverse('ddsc_management.sources.list'),
                icon=''
            ),
            Action(
                name=_('Manage locations'),
                description=_('Manage locations.'),
                url=reverse('ddsc_management.locations'),
                icon=''
            ),
            Action(
                name=_('Manage access groups'),
                description=_('Manage who has access to your data.'),
                url=reverse('ddsc_management.access_groups'),
                icon=''
            ),
        ]

class SummaryView(BaseView):
    template_name = 'ddsc_management/summary.html'
    page_title = _('Summary')

class AlarmsView(BaseView):
    template_name = 'ddsc_management/alarms.html'
    page_title = _('Alarms')

class ImportView(BaseView):
    template_name = 'ddsc_management/import.html'
    page_title = _('Import data')

class TimeseriesView(MySingleObjectMixin, ViewContextFormMixin, ProcessFormMixin, BaseView):
    template_name = 'ddsc_management/timeseries.html'
    page_title = _('Manage timeseries')
    form_class = forms.TimeseriesForm
    model = Timeseries
    using = 'timeseries_staging_db'

    def query_set(self):
        return self.model.objects_nosecurity.using('timeseries_staging_db').all()

    def post(self, request, *args, **kwargs):
        return super(TimeseriesView, self).post(request, *args, **kwargs)

class TimeseriesApiView(ModelDataSourceView):
    model = Timeseries
    allowed_columns = ['code', 'name']
    details_view_name = 'ddsc_management.timeseries.detail'

    def query_set(self):
        return self.model.objects_nosecurity.using('timeseries_staging_db').all()

    def list(self):
        return super(TimeseriesApiView, self).list()

from ddsc_management.models import Country

class SourcesView(MySingleObjectMixin, ViewContextFormMixin, ProcessFormMixin, BaseView):
    template_name = 'ddsc_management/sources.html'
    page_title = _('Manage sources')
    form_class = forms.SourceForm
    model = Country

    def form_valid(self, form):
        if self.object is not None:
            object = self.object
        else:
            object = Country()
        object.name = form.data['name']
        object.save()
        self.success_url = reverse('ddsc_management.sources.detail', kwargs={'pk': object.pk})
        return super(SourcesView, self).form_valid(form)


class SourcesApiView(ModelDataSourceView):
    model = Country
    allowed_columns = ['name', 'formal_name']
    details_view_name = 'ddsc_management.sources.detail'

    def list(self):
        # DEBUG create a few objects if none exist
        if self.query_set().count() == 0:
            for i in range(200):
                c = Country()
                c.name = 'name {:03d}'.format(i)
                c.formal_name = 'formal name {:03d}'.format(i)
                c.capital = 'capital {:03d}'.format(i)
                c.save()
        # /DEBUG
        return super(SourcesApiView, self).list()

class LocationsView(BaseView):
    template_name = 'ddsc_management/locations.html'
    page_title = _('Manage locations')

class AccessGroupsView(BaseView):
    template_name = 'ddsc_management/access_groups.html'
    page_title = _('Manage access groups')
