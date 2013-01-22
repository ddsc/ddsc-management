# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from __future__ import unicode_literals

import logging

from django.forms import models as model_forms
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormMixin, FormView, ProcessFormView, BaseFormView, ModelFormMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.decorators.cache import never_cache
from django.utils.encoding import smart_str
from django.db.models.loading import get_model

from lizard_ui.views import ViewContextMixin

from ddsc_management.utils import get_datatables_records
from ddsc_management import forms
from ddsc_core import models

logger = logging.getLogger(__name__)

class JsonView(View):
    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            logger.warn('Request sent to JsonView does not seem to be Ajax')
        data = self.get_json(request, *args, **kwargs)
        if isinstance(data, HttpResponse):
            return data
        else:
            serialized_data = simplejson.dumps(data)
            return HttpResponse(serialized_data, content_type='application/json')

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            logger.warn('Request sent to JsonView does not seem to be Ajax')
        data = self.post_json(request, *args, **kwargs)
        if isinstance(data, HttpResponse):
            return data
        else:
            serialized_data = simplejson.dumps(data)
            return HttpResponse(serialized_data, content_type='application/json')

class DataSourceView(JsonView):
    action = 'list'
    request = None

    def get_json(self, request, *args, **kwargs):
        self.request = request
        if self.action == 'list':
            data = self.list()
        else:
            return HttpResponseBadRequest('Unknown action')
        return data

    def post_json(self, request, *args, **kwargs):
        self.request = request
        if self.action == 'delete':
            pks = self.request.POST.getlist('pks[]')
            data = self.delete(pks)
        else:
            return HttpResponseBadRequest('Unknown action')
        return data

    def list(self):
        # might want to raise NotImplementedError instead
        return HttpResponseBadRequest('Action not implemented')

    def delete(self, pks):
        # might want to raise NotImplementedError instead
        return HttpResponseBadRequest('Action not implemented')

class ModelDataSourceView(DataSourceView):
    model = None
    allowed_columns = []
    details_view_name = None

    def query_set(self):
        return self.model.objects.all()

    def list(self):
        query_set = self.query_set()
        return get_datatables_records(self.request, query_set, self.allowed_columns, self.details_view_name)

    def delete(self, pks):
        deleted = []
        skipped = []
        for pk in pks:
            try:
                c = self.query_set().filter(pk=pk).get()
                # first grab some information
                deleted.append({
                    'pk': c.pk,
                    'message': unicode(c)
                })
                # then delete it
                c.delete()
            except self.model.DoesNotExist:
                logger.warn('Skipped deleting non-existing object with pk={}'.format(pk))
                skipped.append(pk)
        return {
            'deleted': deleted,
            'skipped': skipped,
        }

class MyFormMixin(object):
    """
    Clone of FormMixin: A mixin that provides a way to show a form in a request.
    """
    initial = {}
    form_class = None

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

    def _init_form(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

    def get_context_data(self, **kwargs):
        context = super(MyFormMixin, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

class MyProcessFormMixin(object):
    """
    Handle the form when set on a View.
    Load before MyFormMixin.
    """
    success_url = None

    def get(self, request, *args, **kwargs):
        self._init_form(request, *args, **kwargs)
        return super(MyProcessFormMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._init_form(request, *args, **kwargs)
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def form_valid(self, form):
        raise NotImplementedError()

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

class MySingleObjectMixin(object):
    """
    A mixin that allows an object with a single PK to be passed directly
    in a form. Load before MyFormMixin when needed.
    """
    pk = None
    model = None
    object = None

    def get_object(self):
        if self.pk is None:
            return
        return self.query_set().get(pk=self.pk)

    def query_set(self):
        return self.model.objects.all()

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(MySingleObjectMixin, self).get_initial()
        if self.object:
            initial.update({'name': self.object.name})
        return initial

    def _init_object(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk', None)
        if self.pk is not None:
            self.object = self.get_object()

    def get(self, request, *args, **kwargs):
        self._init_object(request, *args, **kwargs)
        return super(MySingleObjectMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._init_object(request, *args, **kwargs)
        return super(MySingleObjectMixin, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MySingleObjectMixin, self).get_context_data(**kwargs)
        context['pk'] = self.pk
        context['object'] = self.object
        return context

class MySingleObjectFormMixin(object):
    """
    Combines an object set on the view with the form.
    """

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        if self.form_class:
            return self.form_class
        else:
            return model_forms.modelform_factory(self.model)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = super(MySingleObjectFormMixin, self).get_form_kwargs()
        kwargs.update({'instance': self.object})
        return kwargs

class InlineFormView(MyFormMixin, MyProcessFormMixin, TemplateView):
    app_label = None
    model_name = None
    field = None
    related_model = None
    template_name = 'ddsc_management/inline_form.html'
    model_to_form = {
        models.Manufacturer: forms.ManufacturerForm
    }

    def _init_related_model(self, request, app_label, model_name, field, *args, **kwargs):
        self.app_label = app_label
        self.model_name = model_name
        self.field = field
        self.related_model = self.get_related_model()

    def get(self, request, *args, **kwargs):
        self._init_related_model(request, *args, **kwargs)
        return super(InlineFormView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._init_related_model(request, *args, **kwargs)
        return super(InlineFormView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InlineFormView, self).get_context_data(**kwargs)
        context['app_label'] = self.app_label
        context['model_name'] = self.model_name
        context['field'] = self.field
        context['related_model'] = self.related_model
        return context

    def get_related_model(self):
        # validate parameters here because they
        # might be passed on to the template again
        if self.app_label != 'ddsc_core':
            raise Exception('Inline form not allowed for app_label {}.'.format(self.app_label))
        if self.model_name not in ['source']:
            raise Exception('Inline form not allowed for model {}.'.format(self.model_name))

        # get the Model class and the field meta info
        model_class = get_model(self.app_label, self.model_name)
        model_field = model_class._meta.get_field_by_name(self.field)

        if not model_field:
            raise Exception('Unknown field {} for model {}.'.format(self.field, self.model_name))

        # find out what the foreign key is pointing to
        return model_field[0].related.parent_model

    def get_form_class(self):
        return self.model_to_form[self.related_model]

    def form_valid(self, form):
        form.save()
        return HttpResponse(status=201)
