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
from django.template import loader, Context, RequestContext

from lizard_ui.views import ViewContextMixin

from ddsc_management.utils import get_datatables_records
from ddsc_management import forms
from ddsc_core import models

logger = logging.getLogger(__name__)

class JsonView(View):
    request = None

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        self.request = request
        self.as_html = not request.is_ajax()
        data = self.get_json(request, *args, **kwargs)
        if isinstance(data, HttpResponse):
            return data
        else:
            serialized_data = simplejson.dumps(data)
            return HttpResponse(serialized_data, content_type='application/json')

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        self.request = request
        self.as_html = not request.is_ajax()
        data = self.post_json(request, *args, **kwargs)
        if isinstance(data, HttpResponse):
            return data
        else:
            serialized_data = simplejson.dumps(data)
            return HttpResponse(serialized_data, content_type='application/json')

class DataSourceView(JsonView):
    action = 'list'

    def get_json(self, request, *args, **kwargs):
        if self.action == 'list':
            data = self.list()
        else:
            return HttpResponseBadRequest('Unknown action')
        return data

    def post_json(self, request, *args, **kwargs):
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

    def query_set(self):
        return self.model.objects.all()

    def list(self):
        query_set = self.query_set()
        return get_datatables_records(self.request, query_set, self.allowed_columns)

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

    def init(self, request, *args, **kwargs):
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
        if form.instance.pk is None:
            updating = False
        else:
            updating = True
        form.save()
        if updating:
            return HttpResponse(content="item updated", status=200)
        else:
            return HttpResponse(content="item created", status=201)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form), status=400)

class MySingleObjectMixin(object):
    """
    A mixin that allows an object with a single PK to be passed directly
    in a form. Load before MyFormMixin when needed.
    """
    pk = None
    instance = None

    def get_instance(self):
        return self.query_set().get(pk=self.pk)

    def query_set(self):
        return self.model.objects.all()

    def init(self, request, *args, **kwargs):
        self.pk = request.GET.get('pk', None)
        if self.pk is not None:
            self.instance = self.get_instance()

    def get_context_data(self, **kwargs):
        context = super(MySingleObjectMixin, self).get_context_data(**kwargs)
        context['pk'] = self.pk
        context['instance'] = self.instance
        return context

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = super(MySingleObjectMixin, self).get_form_kwargs()
        kwargs.update({'instance': self.instance})
        return kwargs

class MyTemplateMixin(object):
    def render_to_html(self):
        context = self.get_context_data()
        request_context = RequestContext(self.request, context)
        template = loader.get_template(self.template_name)
        html = template.render(request_context)
        return html

    def get_context_data(self, **kwargs):
        c = {
            'params': kwargs,
            'view': self,
        }
        return c

class MyModelClassMixin(object):
    model_name_to_class = {}
    model_name = None
    model = None

    def init(self, request, *args, **kwargs):
        self.model_name = kwargs['model_name']
        self.model = self.get_model()

    def find_model(self):
        app_label = 'ddsc_core'
        # find the Model class
        model_class = get_model(app_label, self.model_name)
        return model_class

    def get_model(self):
        return self.model_name_to_class[self.model_name]
