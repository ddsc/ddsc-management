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

#
#def validate_password(cleaned_password):
#    if settings.DEBUG:
#        return
#
#    # At least MIN_LENGTH long
#    if len(cleaned_password) < MIN_LENGTH:
#        raise ValidationError(_("The new password must be at least %d characters long.") % MIN_LENGTH)
#
#    # At least one letter and one non-letter, unless it is a huge password
#    is_huge = len(cleaned_password) > HUGE_LENGTH
#    first_isalpha = cleaned_password[0].isalpha()
#    if not is_huge and all(c.isalpha() == first_isalpha for c in cleaned_password):
#        raise ValidationError(_("The new password must contain at least one letter and at least one digit or punctuation character."))
#
#class PasswordChangeForm(auth.forms.PasswordChangeForm):
#    '''Used to verify whether the new password is secure.'''
#
#    def clean_new_password1(self):
#        password1 = self.cleaned_data.get('new_password1')
#        validate_password(password1)
#        return password1
#
#class InviteUserForm(forms.Form):
#    '''
#    Form used by an administrator to invite a user.
#    '''
#    name = forms.CharField(max_length=64, label=_('Name'), required=True)
#    email = forms.EmailField(max_length=255, label=_('Email'), required=True)
#    organisation = forms.CharField(max_length=255, label=_('Organisation'), required=True)
#    language = forms.ChoiceField(
#        label=_('Language'),
#        required=True,
#        choices=[(lang_code, _(lang_name)) for lang_code, lang_name in settings.LANGUAGES],
#        widget=forms.RadioSelect(),
#        initial='nl'
#    )
#
#    portals = forms.ModelMultipleChoiceField(
#        label=_('Portals'),
#        required=False,
#        queryset=Portal.objects.all(),
#        widget=forms.CheckboxSelectMultiple()
#    )
#
#    def clean_email(self):
#        email = self.cleaned_data.get('email')
#        users = User.objects.filter(email=email)
#        if users.exists():
#            raise ValidationError(_('{} is already taken.').format(email))
#        return email
#
#class ActivateUserForm1(forms.Form):
#    '''
#    Form used by a user to activate his/her account.
#    '''
#    username = forms.CharField(max_length=30, label=_('Username'), required=True)
#    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
#    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput)
#
#    error_messages = {
#        'password_mismatch': _("The two password fields didn't match."),
#    }
#
#    def clean_username(self):
#        username = self.cleaned_data.get('username')
#        users = User.objects.filter(username=username)
#        if users.exists():
#            raise ValidationError(_('{} is already taken.').format(username))
#        return username
#
#    def clean_new_password1(self):
#        password1 = self.cleaned_data.get('new_password1')
#        validate_password(password1)
#        return password1
#
#    def clean_new_password2(self):
#        password1 = self.cleaned_data.get('new_password1')
#        password2 = self.cleaned_data.get('new_password2')
#        if password1 and password2:
#            if password1 != password2:
#                raise ValidationError(self.error_messages['password_mismatch'])
#        return password2
#
#class EditProfileForm(forms.Form):
#    '''
#    Form used by a user to activate his/her account.
#    '''
#    email = forms.EmailField(max_length=255, label=_('Email'), required=True)
#    first_name = forms.CharField(max_length=30, label=_('First name'), required=True)
#    last_name = forms.CharField(max_length=30, label=_('Last name'), required=True)
#    title = forms.CharField(max_length=255, label=_('Title'), required=False)
#    street = forms.CharField(max_length=255, label=_('Street'), required=False)
#    postal_code = forms.CharField(max_length=255, label=_('Postal code'), required=False)
#    town = forms.CharField(max_length=255, label=_('Town'), required=False)
#    phone_number = forms.CharField(max_length=255, label=_('Phone number'), required=False)
#    mobile_phone_number = forms.CharField(max_length=255, label=_('Mobile phone number'), required=False)
#
#    def __init__(self, user=None, *args, **kwargs):
#        super(EditProfileForm, self).__init__(*args, **kwargs)
#        self.user = user
#        self.fields.keyOrder = [
#            'email',
#            'first_name',
#            'last_name',
#            'title',
#            'street',
#            'postal_code',
#            'town',
#            'phone_number',
#            'mobile_phone_number',
#        ]
#
#    def clean_email(self):
#        email = self.cleaned_data.get('email')
#        users = User.objects.filter(email=email)
#        if self.user:
#            users = users.exclude(pk=self.user.pk)
#        if users.exists():
#            raise ValidationError(_('{} is already taken.').format(email))
#        return email

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

from ddsc_core import models

class SourceForm(forms.ModelForm):
    class Meta:
        model = models.Source
        widgets = {
#            'manufacturer': widgets.Select(
#                attrs={
#                    'data-inline-add-for': models.Source._meta.verbose_name
#                }
#            ),
            'manufacturer': SelectWithInlineFormPopup(attrs={
                'field': 'manufacturer',
                'model': models.Source,
                'related_model': models.Manufacturer
            }),
        }
#    manufacturer = forms.ModelChoiceField(
#        queryset=models.Manufacturer.objects.all(),
#        widget=SelectWithInlineFormPopup
#    )
#    name = forms.CharField(max_length=30, label=_('Name'), required=True)
#    type = forms.ChoiceField(
#        label=_('Type'),
#        required=True,
#        choices=[
#            ('sensor', _('Sensor')),
#            ('der', _('Der.')),
#            ('cal', _('Cal.')),
#            ('sim', _('Sim.'))
#        ],
#        widget=forms.RadioSelect(),
#        initial='sensor'
#    )
#    supplier = forms.CharField(max_length=30, label=_('Supplier'), required=True)
#    details = forms.CharField(max_length=255, label=_('Details'), required=True)

class TimeseriesForm(forms.ModelForm):
    class Meta:
        model = models.Timeseries
        fields = [
            'code',
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

    #code = forms.CharField(max_length=30, label=_('Code'), required=True)
    #name = forms.CharField(max_length=30, label=_('Name'), required=True)

class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = models.Manufacturer
