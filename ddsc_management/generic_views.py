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

from ddsc_management.utils import get_datatables_records

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
    using = None

    def query_set(self):
        if self.using is None:
            return self.model.objects.all()
        else:
            return self.model.objects.using(self.using).all()

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

class ViewContextFormMixin(object):
    """
    Clone of FormMixin: A mixin that provides a way to show and handle a form in a request.
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

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        return super(ViewContextFormMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        return super(ViewContextFormMixin, self).post(request, *args, **kwargs)

class ProcessFormMixin(object):
    """
    Depends on ViewContextFormMixin.
    """

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class MySingleObjectMixin(object):
    """
    A mixin that provides a way to show and handle a modelform in a request.
    """

    pk = None
    model = None
    object = None
    using = None

    def get_object(self):
        if self.pk is None:
            return
        return self.query_set().get(pk=self.pk)

    def query_set(self):
        if self.using is None:
            return self.model.objects.all()
        else:
            return self.model.objects.using(self.using).all()

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(MySingleObjectMixin, self).get_initial()
        if self.object:
            initial.update({'name': self.object.name})
        return initial

    def get(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk', None)
        self.object = self.get_object()
        return super(MySingleObjectMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk', None)
        self.object = self.get_object()
        return super(MySingleObjectMixin, self).post(request, *args, **kwargs)
