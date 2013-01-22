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

from ddsc_core import models

from ddsc_management import forms
from ddsc_management.utils import get_datatables_records
from ddsc_management.generic_views import MySingleObjectMixin, MyFormMixin, MyProcessFormMixin, ModelDataSourceView, MySingleObjectFormMixin

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

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        context['action'] = self.action
        return context

class SummaryView(BaseView):
    template_name = 'ddsc_management/summary.html'
    page_title = _('Summary')

class AlarmsView(BaseView):
    template_name = 'ddsc_management/alarms.html'
    page_title = _('Alarms')

class ImportView(BaseView):
    template_name = 'ddsc_management/import.html'
    page_title = _('Import data')

class TimeseriesView(MySingleObjectFormMixin, MySingleObjectMixin, MyFormMixin, MyProcessFormMixin, BaseView):
    template_name = 'ddsc_management/timeseries.html'
    page_title = _('Manage timeseries')
    form_class = forms.TimeseriesForm
    model = models.Timeseries

    def query_set(self):
        return self.model.objects_nosecurity.all()

class TimeseriesApiView(ModelDataSourceView):
    model = models.Timeseries
    allowed_columns = ['code', 'name']
    details_view_name = 'ddsc_management.timeseries.detail'

    def query_set(self):
        return self.model.objects_nosecurity.all()

    def list(self):
        return super(TimeseriesApiView, self).list()

class SourcesView(MySingleObjectFormMixin, MySingleObjectMixin, MyFormMixin, MyProcessFormMixin, BaseView):
    template_name = 'ddsc_management/sources.html'
    page_title = _('Manage sources')
    form_class = forms.SourceForm
    model = models.Source

    def form_valid(self, form):
        form.save()
#        if self.action == 'edit':
#            object = self.object
#        elif self.action == 'add':
#            object = self.model()
#        object.name = form.data['name']
#        object.source_type = form.data['source_type']
#        object.manufacturer = models.Manufacturer.objects.get(pk=form.data['manufacturer'])
#        object.details = form.data['details']
#        object.save()
#        self.success_url = reverse('ddsc_management.sources.detail', kwargs={'pk': object.pk})
        return HttpResponse(status=201)

class SourcesApiView(ModelDataSourceView):
    model = models.Source
    allowed_columns = ['name', 'source_type', 'manufacturer__name']
    details_view_name = 'ddsc_management.sources.detail'

    def list(self):
        # DEBUG create a few objects if none exist
        if self.query_set().count() == 0:
            m = models.Manufacturer()
            m.name = 'generic'
            m.save()
            for i in range(200):
                c = models.Source()
                c.manufacturer = m
                c.name = 'name {:03d}'.format(i)
                c.details = 'details {:03d}'.format(i)
                c.save()
        # /DEBUG
        return super(SourcesApiView, self).list()

class LocationsView(BaseView):
    template_name = 'ddsc_management/locations.html'
    page_title = _('Manage locations')

class AccessGroupsView(BaseView):
    template_name = 'ddsc_management/access_groups.html'
    page_title = _('Manage access groups')
