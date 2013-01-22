# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from lizard_map.views import HomepageView
from lizard_ui.urls import debugmode_urlpatterns

from ddsc_management import views
from ddsc_management import generic_views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.SummaryView.as_view(), name='ddsc_management.summary'),

    url(r'^alarms/$', views.AlarmsView.as_view(), name='ddsc_management.alarms'),
    url(r'^import/$', views.ImportView.as_view(), name='ddsc_management.import'),

    # Timeseries
    url(r'^timeseries/$',
        views.TimeseriesView.as_view(action='list'),   name='ddsc_management.timeseries.list'),
    url(r'^timeseries/add/$',
        views.TimeseriesView.as_view(action='add'),    name='ddsc_management.timeseries.add'),
    url(r'^timeseries/(?P<pk>\d+)/$',
        views.TimeseriesView.as_view(action='detail'), name='ddsc_management.timeseries.detail'),

    url(r'^api/timeseries/$',
        views.TimeseriesApiView.as_view(action='list'),   name='ddsc_management.api.timeseries.list'),
    url(r'^api/timeseries/delete/$',
        views.TimeseriesApiView.as_view(action='delete'), name='ddsc_management.api.timeseries.delete'),

    # Sources
    url(r'^sources/$',
        views.SourcesView.as_view(action='list'),   name='ddsc_management.sources.list'),
    url(r'^sources/add/$',
        views.SourcesView.as_view(action='add'),    name='ddsc_management.sources.add'),
    url(r'^sources/(?P<pk>\d+)/$',
        views.SourcesView.as_view(action='detail'), name='ddsc_management.sources.detail'),
    url(r'^sources/(?P<pk>\d+)/edit/$',
        views.SourcesView.as_view(action='edit'),   name='ddsc_management.sources.edit'),

    url(r'^api/sources/$',
        views.SourcesApiView.as_view(action='list'),   name='ddsc_management.api.sources.list'),
    url(r'^api/sources/delete/$',
        views.SourcesApiView.as_view(action='delete'), name='ddsc_management.api.sources.delete'),

    # Inline forms
    url(r'^inline_form/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<field>\w+)/$',
        generic_views.InlineFormView.as_view(), name='ddsc_management.inline_form'),

    url(r'^locations/$', views.LocationsView.as_view(), name='ddsc_management.locations'),
    url(r'^access_groups/$', views.AccessGroupsView.as_view(), name='ddsc_management.access_groups'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^map/', include('lizard_map.urls')),
    url(r'^ui/', include('lizard_ui.urls')),
    )
urlpatterns += debugmode_urlpatterns()
