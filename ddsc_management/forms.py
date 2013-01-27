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

class TreePopup(widgets.Widget):
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(
            attrs,
        )
        final_attrs['type'] = 'button'
        final_attrs['class'] = 'btn'
        final_attrs['data-tree-popup'] = 'true'
        final_attrs['data-field'] = name
        final_attrs['data-tree-url'] = reverse('ddsc_management.api.locations.tree')
        return mark_safe(u'<button%s>%s</button>' % (flatatt(final_attrs), _('Open location tree')))

class TreePlaceholder(widgets.Widget):
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
            'path',
            'relative_location',
            'point_geometry',
            'real_geometry',
            'geometry_precision',
        ]
        widgets = {
            'point_geometry': PointWidget,
            'real_geometry': GeometryWidget,
            'path': TreePopup
        }

#    point_geometry = PointField()
