# (c) Nelen & Schuurmans. MIT licensed, see LICENSE.rst.

from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns

from ddsc_management import views

admin.autodiscover()

urlpatterns = patterns('',
    # overviews
    url(r'^$', views.OverviewsView.as_view(), name='ddsc_management.home'),
    url(r'^overviews/$', views.OverviewsView.as_view(), name='ddsc_management.overviews'),
    url(r'^overviews/users/$', views.UsersView.as_view(), name='ddsc_management.users'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^ui/', include('lizard_ui.urls')),
    url(r'^ddsc_core/', include('ddsc_core.urls')),
)

urlpatterns += debugmode_urlpatterns()
