# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from django.views.generic import TemplateView
from lizard_map.views import HomepageView
from lizard_ui.urls import debugmode_urlpatterns

from ddsc_management import generic_views
from ddsc_management import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.SummaryView.as_view(), name='ddsc_management.summary'),

    url(r'^alarms/$', views.AlarmsView.as_view(), name='ddsc_management.alarms'),
    url(r'^import/$', views.ImportView.as_view(), name='ddsc_management.import'),

    # Timeseries
    url(r'^timeseries/$',
        views.TimeseriesView.as_view(action='list'),   name='ddsc_management.timeseries'),
    # Timeseries API
    url(r'^api/timeseries/$',
        views.TimeseriesApiView.as_view(action='list'),   name='ddsc_management.api.timeseries.list'),
    url(r'^api/timeseries/delete/$',
        views.TimeseriesApiView.as_view(action='delete'), name='ddsc_management.api.timeseries.delete'),

    # Sources
    url(r'^sources/$',
        views.SourcesView.as_view(action='list'),   name='ddsc_management.sources'),
    # Sources API
    url(r'^api/sources/$',
        views.SourcesApiView.as_view(action='list'),   name='ddsc_management.api.sources.list'),
    url(r'^api/sources/delete/$',
        views.SourcesApiView.as_view(action='delete'), name='ddsc_management.api.sources.delete'),

    # Locations
    url(r'^locations/$',
        views.LocationsView.as_view(), name='ddsc_management.locations'),
    # Locations API
    url(r'^api/locations/$',
        views.LocationsApiView.as_view(action='list'),   name='ddsc_management.api.locations.list'),
    url(r'^api/locations/delete/$',
        views.LocationsApiView.as_view(action='delete'), name='ddsc_management.api.locations.delete'),
    url(r'^api/locations/tree$',
        views.LocationTreeView.as_view(),                name='ddsc_management.api.locations.tree'),

    # Inline forms
    url(r'^dynamic_form/(?P<model_name>\w+)/add/$',
        views.DynamicFormView.as_view(action='add'), name='ddsc_management.dynamic_form.add'),
    url(r'^dynamic_form/(?P<model_name>\w+)/edit/$',
        views.DynamicFormView.as_view(action='edit'), name='ddsc_management.dynamic_form.edit'),

    # Simple dump detail view
    url(r'^generic_detail/(?P<model_name>\w+)/$',
        views.GenericDetailView.as_view(), name='ddsc_management.generic_detail'),

    url(r'^access_groups/$', views.AccessGroupsView.as_view(), name='ddsc_management.access_groups'),

    # overviews
    url(r'^overviews/$', views.OverviewsView.as_view(), name='ddsc_management.overviews'),
    url(r'^overviews/users/$', views.UsersView.as_view(), name='ddsc_management.users'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^map/', include('lizard_map.urls')),
    url(r'^ui/', include('lizard_ui.urls')),
    url(r'^ddsc_core/', include('ddsc_core.urls')),
    )
urlpatterns += debugmode_urlpatterns()
