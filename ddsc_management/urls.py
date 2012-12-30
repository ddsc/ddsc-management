# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from lizard_map.views import HomepageView
from lizard_ui.urls import debugmode_urlpatterns

from ddsc_management import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.SummaryView.as_view(), name='ddsc_management.summary'),

    url(r'^alarms/$', views.AlarmsView.as_view(), name='ddsc_management.alarms'),
    url(r'^import/$', views.ImportView.as_view(), name='ddsc_management.import'),
    url(r'^timeseries/$', views.TimeseriesView.as_view(), name='ddsc_management.timeseries'),

    url(r'^sources/$', views.SourcesView.as_view(), name='ddsc_management.sources'),
    url(r'^sources/(?P<pk>\d+)/edit/$', views.EditSourcesView.as_view(), name='ddsc_management.edit_source'),
    url(r'^api/sources/$',        views.ListSourcesView.as_view(),                name='ddsc_management.api.list_sources'),
    url(r'^api/sources/delete/$', views.ListSourcesView.as_view(action='delete'), name='ddsc_management.api.delete_sources'),

    url(r'^locations/$', views.LocationsView.as_view(), name='ddsc_management.locations'),
    url(r'^access_groups/$', views.AccessGroupsView.as_view(), name='ddsc_management.access_groups'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^map/', include('lizard_map.urls')),
    url(r'^ui/', include('lizard_ui.urls')),
    )
urlpatterns += debugmode_urlpatterns()
