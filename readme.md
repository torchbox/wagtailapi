Wagtail API module
==================

The ``wagtailapi`` module can be used to create a simple, read-only, JSON-based API for viewing your Wagtail content.


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



Basic Usage
-----------

### Listing pages

This view should list all live pages in your project that are not in a private section.

Example:

```
    > http http://localhost:8000/api/v1/pages/
    
    HTTP/1.0 200 OK

    {
        "count": 19, 
        "next": "/api/v1/pages/?page=2", 
        "results": [
            {
                "id": 2, 
                "title": "Home page", 
                "type": "demo.HomePage"
            }, 
            {
                "id": 4, 
                "title": "Events index", 
                "type": "demo.EventIndexPage"
            }, 
            {
                "id": 5, 
                "title": "Blog index", 
                "type": "demo.BlogIndexPage"
            }, 
            {
                "id": 16, 
                "title": "Blog post", 
                "type": "demo.BlogPage"
            }, 
            {
                "id": 18, 
                "title": "Blog post again", 
                "type": "demo.BlogPage"
            }, 
            {
                "id": 19, 
                "title": "Another blog post", 
                "type": "demo.BlogPage"
            }
        ]
    }
```


### Viewing details about an individual page


Example

```
    > http http://localhost:8000/api/v1/pages/16/

    HTTP/1.0 200 OK
    
    {
        "id": 16, 
        "title": "Blog post", 
        "type": "demo.BlogPage"
    }
```


Adding more data
----------------

In the above examples, the JSON documents only contain ``id``, ``type`` and ``title`` fields. In most cases, this isn't very useful.

To add more fields to the JSON documents, add an ``api_fields`` attribute to your page model set to a list/tuple of names of fields to include in the JSON document.


Example:

```
    # models.py

    class BlogPage(Page):  
        posted_by = models.CharField()
        posted_at = models.DateTimeField()

        api_fields = ('posted_by', 'posted_at')
```

```
    > http http://localhost:8000/api/v1/pages/?type=demo.BlogPage

    HTTP/1.0 200 OK
    
    {
        "count": 3, 
        "results": [
            {
                "id": 16, 
                "title": "Blog post", 
                "type": "demo.BlogPage",
                "posted_by": "Tom",
                "posted_at": "2014-01-21 12:30:00"
            }, 
            {
                "id": 18, 
                "title": "Blog post again", 
                "type": "demo.BlogPage",
                "posted_by": "Dick",
                "posted_at": "2014-01-22 17:00:00"
            }, 
            {
                "id": 19, 
                "title": "Another blog post", 
                "type": "demo.BlogPage",
                "posted_by": "Harry",
                "posted_at": "2014-01-23 11:45:00"
            }
        ]
    }
```


Filtering, ordering and Searching
---------------------------------

### Filtering by field values


### Filtering by page type

Add ``type?app_label.ModelName`` to the request.

### Filtering by tree position

**NOT YET IMPLEMENTED**

You can also filter by a pages tree position. This lets you find the decendants, siblings and ancestors of any other page.

#### ``descendant_of``

#### ``child_of``

#### ``ancestor_of``

#### ``parent_of``

#### ``sibling_of``


### Ordering

**NOT YET IMPLEMENTED**


#### ``order_by``

### Searching

Full text searching is also supported. Just add ``?search=Search query here`` on any listing.


Images and Documents
--------------------

