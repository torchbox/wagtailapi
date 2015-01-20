Wagtail API
===========

The ``wagtailapi`` module can be used to create a simple, read-only, JSON-based API for viewing your Wagtail content.


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



Usage
-----

### Listing all pages

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


### Listing pages of a specific type

You can narrow down this list by page type by appending the app label and model name to the end of the path.

Example:

```
    > http http://localhost:8000/api/v1/pages/demo.BlogPage/

    HTTP/1.0 200 OK
    
    {
        "count": 3, 
        "results": [
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

The simplest way to add fields to the JSON, is to define one or both of the following methods on the page model:

#### ``get_api_summary_data()``

Returns a ``dict`` of values to append to the page in listings.

Example:

```
    # models.py

    class BlogPage(Page):  
        posted_by = models.CharField()
        posted_at = models.DateTimeField()

        def get_api_summary_data(self):  
            return {
                'posted_by': self.posted_by,
                'posted_at': self.posted_at,
            }
```

```
    > http http://localhost:8000/api/v1/pages/demo.BlogPage/

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


#### ``get_api_detail_data()``

Returns a ``dict`` of values to append to the page on its detail page.

Example:

```
    # models.py

    class BlogPage(Page):  
        posted_by = models.CharField()
        posted_at = models.DateTimeField()
        body = models.TextField()

        def get_api_detail_data(self):  
            return {
                'posted_by': self.posted_by,
                'posted_at': self.posted_at,
                'body': self.body,
            }
```

```
    > http http://localhost:8000/api/v1/pages/16/

    HTTP/1.0 200 OK
    
    {
        "id": 16, 
        "title": "Blog post", 
        "type": "demo.BlogPage",
        "posted_by": "Tom",
        "posted_at": "2014-01-21 12:30:00",
        "body": "<p>Wagtails are slender, often colourful, ground-feeding insectivores of open country in the Old World.</p>"
    }
```


### Images and Documents

Images and documents can also be put in the response. When ``wagtailapi`` detects these, it will automatically convert them into a serializable format.

You could return the image object directly but would only give the user access to basic information such as the images title. To return a URL to an image that could be downloaded and shown to the user, call ``get_rendition`` on the object and return that instead.

Example:

```
    # models.py

    class BlogPage(Page):  
        posted_by = models.CharField()
        posted_at = models.DateTimeField()
        image = models.ForeignKey('wagtailimages.Image')
        document = models.ForeignKey('wagtaildocs.Document')

        def get_api_detail_data(self):  
            return {
                'posted_by': self.posted_by,
                'posted_at': self.posted_at,
                'image': self.image.get_rendition('width-800'),
                'document': self.document,
            }
```

```
    > http http://localhost:8000/api/v1/pages/16/

    HTTP/1.0 200 OK
    
    {
        "id": 16, 
        "title": "Blog post", 
        "type": "demo.BlogPage",
        "posted_by": "Tom",
        "posted_at": "2014-01-21 12:30:00",
        "image": {
            "url": "/media/images/myimage.jpg",
            "width": 800,
            "height": 600,
            "image": {
                "id": 10,
                "title:": "Wagtail"
            }
        },
        "document": {
            "id": 1,
            "title": "A document",
            "url": "/documents/document.pdf"
        }
    }
```


### Nesting listings of pages

You can also nest a listing of pages inside the returned document


Django REST framework serializers
---------------------------------

``wagtailapi`` supports Django REST frameworks serializers API for defining fields to go into the page.



Advanced usage
--------------

### Filtering

``wagtailapi`` uses ``django-filter`` internally.


### Ordering

### Searching


