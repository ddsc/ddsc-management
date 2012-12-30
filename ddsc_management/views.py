# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormMixin, FormView, ProcessFormView, BaseFormView, ModelFormMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from django.views.decorators.cache import never_cache
from lizard_ui.views import UiView
from lizard_ui.layout import Action

from ddsc_management import forms
from ddsc_management.utils import get_datatables_records

logger = logging.getLogger(__name__)

class JsonView(View):
    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        data = self.get_json(request, *args, **kwargs)
        serialized_data = simplejson.dumps(data)
        return HttpResponse(serialized_data, content_type='application/json')

class BaseView(UiView):
    @property
    def home_breadcrumb_element(self):
        home = super(BaseView, self).home_breadcrumb_element
        home.url = reverse('ddsc_management.summary')
        return home

    def content_actions(self):
        return [
            Action(
                name=_('Summary'),
                description=_('View summarized infomation.'),
                url=reverse('ddsc_management.summary'),
                icon='icon-edit'
            ),
            Action(
                name=_('Alarms'),
                description=_('Manage alarms.'),
                url=reverse('ddsc_management.alarms'),
                icon='icon-edit'
            ),
            Action(
                name=_('Import data'),
                description=_('Manually import data from csv files.'),
                url=reverse('ddsc_management.import'),
                icon='icon-edit'
            ),
            Action(
                name=_('Timeseries'),
                description=_('Manage timeseries.'),
                url=reverse('ddsc_management.timeseries'),
                icon='icon-edit'
            ),
            Action(
                name=_('Manage sources'),
                description=_('Manage sources.'),
                url=reverse('ddsc_management.sources'),
                icon='icon-edit'
            ),
            Action(
                name=_('Manage locations'),
                description=_('Manage locations.'),
                url=reverse('ddsc_management.locations'),
                icon='icon-edit'
            ),
            Action(
                name=_('Manage access groups'),
                description=_('Manage who has access to your data.'),
                url=reverse('ddsc_management.access_groups'),
                icon='icon-edit'
            ),
        ]

class ViewContextFormMixin(object):
    """
    (FormMixin)
    A mixin that provides a way to show and handle a form in a request.

    Combined with:

    (ProcessFormView)
    A mixin that processes a form on POST.

    And tuned to allow a custom GET method with its own
    RequestContext handling.
    """

    initial = {}
    form_class = None
    success_url = None

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initial.copy()

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        return self.form_class

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        return super(ViewContextFormMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class ViewContextModelFormMixin(ViewContextFormMixin):
    """
    A mixin that provides a way to show and handle a modelform in a request.
    """

    model = None
    object = None

    def get_object(self):
        pk = self.request.GET.get('pk', None)
        if pk is None:
            return
        return self.model.objects.get(pk=pk)

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(ViewContextModelFormMixin, self).get_initial()
        if self.object:
            initial.update({'name': self.object.name})
        return initial

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ViewContextModelFormMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ViewContextModelFormMixin, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        #self.object.save()
        return HttpResponseRedirect(self.get_success_url())

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

class SourcesView(ViewContextFormMixin, BaseView):
    template_name = 'ddsc_management/sources.html'
    page_title = _('Manage sources')
    form_class = forms.SourceForm

from ddsc_management.models import Country

class EditSourcesView(ViewContextModelFormMixin, BaseView):
    template_name = 'ddsc_management/sources.html'
    page_title = _('Manage sources2')
    form_class = forms.SourceForm
    model = Country

class ListSourcesView(JsonView):
    def get_json(self, request, *args, **kwargs):
        # DEBUG since we don't have Sources yet, use a debug Model
        from ddsc_management.models import Country
        query_set = Country.objects.all()
        if query_set.count() == 0:
            for i in range(200):
                c = Country()
                c.name = 'name {}'.format(i)
                c.formal_name = 'formal name {}'.format(i)
                c.capital = 'capital {}'.format(i)
                c.save()
            query_set = Country.objects.all()
        allowed_columns = ['pk', 'name', 'formal_name']
        # /DEBUG
        return get_datatables_records(request, query_set, allowed_columns)

class LocationsView(BaseView):
    template_name = 'ddsc_management/locations.html'
    page_title = _('Manage locations')

class AccessGroupsView(BaseView):
    template_name = 'ddsc_management/access_groups.html'
    page_title = _('Manage access groups')
