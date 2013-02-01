# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms import ValidationError
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode
from django.forms.util import flatatt
from django.utils.html import conditional_escape

from treebeard.forms import MoveNodeForm
from floppyforms.gis.widgets import PointWidget, GeometryWidget
from floppyforms.gis.fields import PointField

from ddsc_core import models

class SelectWithInlineFormPopup(widgets.Select):
    def render(self, name, value, attrs=None, choices=()):
        select_html = widgets.Select.render(self, name, value, attrs=attrs, choices=choices)
        output = []
        output.append(u'<div class="input-append">')
        output.append(select_html)
        output.append(u'<button class="btn" type="button"')

        model_class = self.attrs['model']
        model_name = model_class._meta.verbose_name
        field = self.attrs['field'] if 'field' in self.attrs else name
        related_model_class = self.attrs['related_model']
        related_model_name = related_model_class._meta.verbose_name

        form_url = reverse('ddsc_management.dynamic_form.add', kwargs={
            'model_name': related_model_name,
        })

        output.append(u' data-inline-add-model-name="' + unicode(model_name) + u'"')
        output.append(u' data-inline-add-field="' + unicode(field) + u'"')
        output.append(u' data-inline-add-related-model-name="' + unicode(related_model_name) + u'"')
        output.append(u' data-inline-add-form-url="' + unicode(form_url) + u'"')

        output.append(u'><i class="icon-plus"></i></button>')
        output.append(u'</div>')
        html = mark_safe(u'\n'.join(output))
        return html

class TreePopup(widgets.TextInput):
    def render(self, name, value, attrs=None):
        output = []

        text_input_html = widgets.TextInput.render(self, name, value, attrs=attrs)
        output.append(text_input_html)

        final_attrs = self.build_attrs(
            attrs,
        )
        final_attrs['type'] = 'button'
        final_attrs['class'] = 'btn'
        final_attrs['data-tree-popup'] = 'true'
        final_attrs['data-field'] = name
        final_attrs['data-tree-url'] = reverse('ddsc_management.api.locations.tree')
        output.append(u'<button%s>%s</button>' % (flatatt(final_attrs), _('Open location tree')))

        return mark_safe(u'\n'.join(output))

class LocationSelector(widgets.Widget):
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(
            attrs,
        )
        final_attrs['data-tree'] = 'tree'
        final_attrs['data-field'] = name
        return mark_safe(u'<div%s/>' % (flatatt(final_attrs)))

class SourceForm(forms.ModelForm):
    class Meta:
        model = models.Source
        widgets = {
            'manufacturer': SelectWithInlineFormPopup(attrs={
                'field': 'manufacturer',
                'model': models.Source,
                'related_model': models.Manufacturer
            }),
        }

class TimeseriesForm(forms.ModelForm):
    class Meta:
        model = models.Timeseries
        fields = [
            'name',
            'description',
            'data_set',
            'supplying_systems',
            'value_type',
            'source',
            'owner',
            'location',
            'parameter',
            'unit',
            'reference_frame',
            'compartment',
            'measuring_device',
            'measuring_method',
            'processing_method',
        ]
        widgets = {
            'source': SelectWithInlineFormPopup(attrs={
                'field': 'source',
                'model': models.Timeseries,
                'related_model': models.Source
            }),
        }

class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = models.Manufacturer

class LocationForm(forms.ModelForm):
    class Meta:
        model = models.Location
        fields = [
            'name',
            'description',
            'relative_location',
            'point_geometry',
            'real_geometry',
            'geometry_precision',
        ]
        widgets = {
            'point_geometry': PointWidget,
            'real_geometry': GeometryWidget,
        }

    parent_pk = forms.CharField(label=_('Parent location'), required=False, widget=TreePopup)

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            # we're in editing / update mode
            if not self.initial.get('parent_pk'):
                parent = self.instance.get_parent()
                parent_pk = None if parent is None else parent.pk
                self.initial['parent_pk'] = parent_pk

    def clean_parent_pk(self):
        parent_pk = self.data.get('parent_pk')
        if parent_pk in ['', 0, None]:
            parent_pk = None
        else:
            parent = models.Location.objects_nosecurity.get(pk=parent_pk)
            if parent is None:
                raise ValidationError('No such parent.')
            if self.instance.pk is not None and self.instance.pk == parent.pk:
                raise ValidationError('Can not assign location as a sublocation of itself.')
        return parent_pk

    def save(self, commit=True):
        if commit:
            parent_pk = self.cleaned_data.get('parent_pk')
            self.instance = self.instance.save_under(parent_pk=parent_pk)
        return super(LocationForm, self).save(commit=commit)
