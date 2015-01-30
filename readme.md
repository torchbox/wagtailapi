Wagtail API module
==================

The ``wagtailapi`` module can be used to create a simple, read-only, JSON-based API for viewing your Wagtail content.

There are three endpoints to the API:

* **Pages:** ``/api/v1/pages/``
* **Images:** ``/api/v1/images/``
* **Documents:** ``/api/v1/documents/``

See [the API documentation](http://docs.wagtailapi.apiary.io/) for more information on how to use the API.


Installation
------------

The ``wagtailapi`` module can be installed with ``pip``:

```
    pip install wagtailapi
```

Once installed, you then need to add ``wagtailapi`` to ``INSTALLED_APPS`` in your Django settings and configure a URL for it in ``urls.py``

```
    # settings.py

    INSTALLED_APPS = [
        ...
        
        'wagtailapi',
    ]


    # urls.py

    from wagtailapi import urls as wagtailapi_urls


    urlpatterns = [
        ...

        url(r'^api/', include(wagtailapi_urls)),
    ]
```


Configuration
-------------

### Settings

``WAGTAILAPI_BASE_URL`` (required when using frontend cache invalidation)

This is used in two places, when generating absolute URLs to document files and invalidating the cache.

Generating URLs to documents will fall back the the current request's hostname if this is not set. Cache invalidation cannot do this however so this setting must be set when using this module alongside the ``wagtailfrontendcache`` module.


``WAGTAILAPI_SEARCH_ENABLED`` (default: True)

Setting this to false will disable full text search. This applies to all endpoints.


``WAGTAILAPI_MAX_RESULTS`` (default: 20)

This allows you to change the maximum number of results a user can get at any time. This applies to all endpoints.


### Adding more fields to pages

By Default, the pages endpoint only includes the ``id``, ``title`` and ``type`` fields in both the listing and detail views.

You can add more fields to the pages endpoint by setting an attribute called ``api_fields`` to a list/tuple of field names:

```python
    class BlogPage(Page):  
        posted_by = models.CharField()
        posted_at = models.DateTimeField()
        content = RichTextField()

        api_fields = ('posted_by', 'posted_at', 'content')
```


This list also supports child relations (which will be nested inside returned JSON document):

```python
    class BlogPageRelatedLink(Orderable):
        page = ParentalKey('BlogPage', related_name='related_links')
        link = models.URLField()

        api_fields = ('link', )

    class BlogPage(Page):  
        posted_by = models.CharField()
        posted_at = models.DateTimeField()
        content = RichTextField()

        api_fields = ('posted_by', 'posted_at', 'content', 'related_links')
```
