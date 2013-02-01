# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from __future__ import unicode_literals

import logging
from urllib import urlencode

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormMixin, FormView, ProcessFormView, BaseFormView, ModelFormMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.decorators.cache import never_cache
from django.db.models.loading import get_model
from django.template import loader, Context, RequestContext
from django.core import serializers

from lizard_ui.views import UiView
from lizard_ui.layout import Action

from ddsc_core import models

from ddsc_management import forms
from ddsc_management.utils import get_datatables_records, treebeard_nodes_to_jstree
from ddsc_management.generic_views import (
    JsonView,
    MySingleObjectMixin,
    MyFormMixin,
    MyProcessFormMixin,
    ModelDataSourceView,
    MyTemplateMixin,
    MyModelClassMixin
)

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
                url=reverse('ddsc_management.timeseries'),
                icon=''
            ),
            Action(
                name=_('Sources'),
                description=_('Manage sources.'),
                url=reverse('ddsc_management.sources'),
                icon=''
            ),
            Action(
                name=_('Locations'),
                description=_('Manage locations.'),
                url=reverse('ddsc_management.locations'),
                icon=''
            ),
            Action(
                name=_('Access groups'),
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

class TimeseriesView(BaseView):
    template_name = 'ddsc_management/timeseries.html'
    page_title = _('Timeseries')

class TimeseriesApiView(ModelDataSourceView):
    model = models.Timeseries
    allowed_columns = ['uuid', 'name']
    detail_view_name = 'ddsc_management.timeseries.detail'

    def query_set(self):
        return self.model.objects_nosecurity.all()

class SourcesView(BaseView):
    template_name = 'ddsc_management/sources.html'
    page_title = _('Sources')

class SourcesApiView(ModelDataSourceView):
    model = models.Source
    allowed_columns = ['name', 'source_type', 'manufacturer__name']

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
    page_title = _('Locations')

class LocationsApiView(ModelDataSourceView):
    model = models.Location
    allowed_columns = ['uuid', 'name']

class LocationTreeView(JsonView):
    def get_json(self, request, *args, **kwargs):
        parent_pk = request.GET.get('parent_pk', None)
        search = request.GET.get('search', None)
        if parent_pk:
            parent = models.Location.objects.get(pk=parent_pk)
            nodes = parent.get_children()
        elif search:
            nodes = models.Location.objects.filter(name__icontains=search)
        else:
            nodes = models.Location.get_root_nodes()
        return treebeard_nodes_to_jstree(nodes)

class AccessGroupsView(BaseView):
    template_name = 'ddsc_management/access_groups.html'
    page_title = _('Access groups')

class DynamicFormView(MyModelClassMixin, MySingleObjectMixin, MyFormMixin, MyTemplateMixin, JsonView):
    action = None
    template_name = 'ddsc_management/dynamic_form.html'
    model_name_to_form = {
        'manufacturer': forms.ManufacturerForm,
        'source': forms.SourceForm,
        'timeseries': forms.TimeseriesForm,
        'location': forms.LocationForm,
    }
    model_name_to_class = {
        'manufacturer': models.Manufacturer,
        'source': models.Source,
        'timeseries': models.Timeseries,
        'location': models.Location,
    }
    for_modal = False

    def init(self, request, *args, **kwargs):
        MyModelClassMixin.init(self, request, *args, **kwargs)
        if self.action == 'edit':
            MySingleObjectMixin.init(self, request, *args, **kwargs)
        MyFormMixin.init(self, request, *args, **kwargs)
        self.for_modal = request.GET.get('for_modal', 'False') == 'True'

    def get_json(self, request, *args, **kwargs):
        self.init(request, *args, **kwargs)

        html = self.render_to_html()
        result = {
            'html': html,
            'success': True
        }

        if self.as_html:
            # just return the html, so it can be viewed in the browser
            return HttpResponse(content=result['html'])
        else:
            return result

    def post_json(self, request, *args, **kwargs):
        self.init(request, *args, **kwargs)

        if self.form.is_valid():
            instance = self.form_valid()
            result = {
                'html': '<p>OK, saved as {} with pk={}</p>'.format(str(instance), instance.pk),
                'success': True,
                'pk': instance.pk,
                'name': str(instance),
            }
        else:
            html = self.render_to_html()
            result = {
                'html': html,
                'success': False,
            }

        if self.as_html:
            # just return the html, so it can be viewed in the browser
            return HttpResponse(content=result['html'])
        else:
            return result

    # DEBUG disable security
    def query_set(self):
        if hasattr(self.model, 'objects_nosecurity'):
            return self.model.objects_nosecurity.all()
        else:
            return self.model.objects.all()
    # /DEBUG

    def form_valid(self):
        instance = self.form.save()
        return instance

    def get_form_kwargs(self):
        kwargs = super(DynamicFormView, self).get_form_kwargs()
        if self.action == 'edit':
            kwargs.update({'instance': self.instance})
        return kwargs

    def get_form_class(self):
        return self.model_name_to_form[self.model_name]

    def form_action_url(self):
        '''
        Determine URL in code, since Django's {% url %} template tag is
        lacking when dealing with query strings.
        '''
        if self.action == 'add':
            qs = urlencode({'for_modal': str(self.for_modal)})
            return reverse('ddsc_management.dynamic_form.add', kwargs={'model_name': self.model_name}) + '?' + qs
        elif self.action == 'edit':
            qs = urlencode({'pk': self.pk, 'for_modal': str(self.for_modal)})
            return reverse('ddsc_management.dynamic_form.edit', kwargs={'model_name': self.model_name}) + '?' + qs

    def form_id(self):
        '''
        Returns a nicely formatted HTML element ID.
        '''
        return 'form-{}-{}'.format(self.action, self.model_name)

    def form_header(self):
        '''
        Returns a suitable, translated header for the form.
        '''
        if self.action == 'add':
            header = _('Add a {model_name}')
        elif self.action == 'edit':
            header = _('Edit a {model_name}')
        return header.format(model_name=self.model._meta.verbose_name)

class GenericDetailView(MyModelClassMixin, MySingleObjectMixin, MyTemplateMixin, JsonView):
    template_name = 'ddsc_management/generic_detail.html'
    model_name_to_class = {
        'manufacturer': models.Manufacturer,
        'source': models.Source,
        'timeseries': models.Timeseries,
        'location': models.Location,
    }

    # DEBUG disable security
    def query_set(self):
        if hasattr(self.model, 'objects_nosecurity'):
            return self.model.objects_nosecurity.all()
        else:
            return self.model.objects.all()
    # /DEBUG

    def get_json(self, request, *args, **kwargs):
        MyModelClassMixin.init(self, request, *args, **kwargs)
        MySingleObjectMixin.init(self, request, *args, **kwargs)

        self.data = serializers.serialize("python", [self.instance])

        html = self.render_to_html()

        result = {
            'html': html
        }

        if self.as_html:
            # just return the html, so it can be viewed in the browser
            return HttpResponse(content=result['html'])
        else:
            return result
