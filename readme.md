Wagtail API module
==================

The ``wagtailapi`` module can be used to create a simple, read-only, JSON-based API for viewing your Wagtail content.

There are three endpoints to the API:

* **Pages:** ``/api/v1/pages/``
* **Images:** ``/api/v1/images/``
* **Documents:** ``/api/v1/documents/``

See [the API documentation](http://docs.wagtailapi.apiary.io/) for more information on how to use the API.


**Warning:** This module is experimental and likely to change in backwards incompatible ways. Once finished, it will be merged into Wagtail as a new contrib app.


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