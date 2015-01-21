from __future__ import absolute_import

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^v1/pages/$', views.page_listing),
    url(r'^v1/pages/(\d+)/$', views.page_detail),
]
