from __future__ import absolute_import

from django.conf.urls import url, include

from .pages import WagtailPagesAPI


urlpatterns = [
    url(r'^v1/pages/', include(WagtailPagesAPI().get_urlpatterns(), namespace='wagtailapi_v1_pages'))
]
