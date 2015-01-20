from __future__ import absolute_import

from django.conf.urls import url, include
from .pages import WagtailPagesAPI
from .filters import install_filters_mixin

install_filters_mixin()


urlpatterns = [
    url(r'^v1/pages/', include(WagtailPagesAPI().get_urlpatterns(), namespace='wagtailapi_v1_pages'))
]
