from __future__ import absolute_import

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^v1/pages/$', views.page_listing, name='wagtailapi_v1_page_listing'),
    url(r'^v1/pages/(\d+)/$', views.page_detail, name='wagtailapi_v1_page_detail'),
    url(r'^v1/images/$', views.image_listing, name='wagtailapi_v1_image_listing'),
    url(r'^v1/images/(\d+)/$', views.image_detail, name='wagtailapi_v1_image_detail'),
    url(r'^v1/documents/$', views.document_listing, name='wagtailapi_v1_document_listing'),
    url(r'^v1/documents/(\d+)/$', views.document_detail, name='wagtailapi_v1_document_detail'),
]
