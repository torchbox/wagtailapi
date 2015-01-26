from django.conf.urls import patterns, include, url

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailsearch import urls as wagtailsearch_urls
from wagtail.wagtailimages import urls as wagtailimages_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from wagtailapi import urls as wagtailapi_urls


urlpatterns = patterns('',
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^search/', include(wagtailsearch_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^api/', include(wagtailapi_urls)),

    url(r'', include(wagtail_urls)),
)
