# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings

from lizard_ui.views import UiView
from lizard_ui.layout import Action

logger = logging.getLogger(__name__)

class BaseView(UiView):
    page_title = _('DDSC Management')

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

class SummaryView(BaseView):
    template_name = 'ddsc_management/summary.html'

class AlarmsView(BaseView):
    template_name = 'ddsc_management/alarms.html'

class ImportView(BaseView):
    template_name = 'ddsc_management/import.html'

class TimeseriesView(BaseView):
    template_name = 'ddsc_management/timeseries.html'

class SourcesView(BaseView):
    template_name = 'ddsc_management/sources.html'

class LocationsView(BaseView):
    template_name = 'ddsc_management/locations.html'

class AccessGroupsView(BaseView):
    template_name = 'ddsc_management/access_groups.html'
