from __future__ import absolute_import

from django.conf.urls import url, include

from . import api


urlpatterns = [
    url(r'^v1/pages/', include(api.PagesAPIEndpoint().get_urlpatterns(), namespace='wagtailapi_v1_pages')),
    url(r'^v1/images/', include(api.ImagesAPIEndpoint().get_urlpatterns(), namespace='wagtailapi_v1_images')),
    url(r'^v1/documents/', include(api.DocumentsAPIEndpoint().get_urlpatterns(), namespace='wagtailapi_v1_documents')),
]
