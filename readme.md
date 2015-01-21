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


### Nested Pages, Images and Documents

Images and documents can also be put in the response. ``wagtailapi`` will automatically convert them into a serializable format.

Note: In order to create a downloadable URL to an image file, you must call ``get_rendition`` on the image object. This will resize the image on the server side and return a downloadable URL to the image in the JSON response. ``get_rendition`` takes only one parameter, the resize rule (which has the same format as described  [here](http://docs.wagtail.io/en/latest/core_components/images/index.html#using-images-in-templates)).

Nested pages would have their ``get_api_summary_data`` method called if it has been defined.

Example:

```
    # models.py

    class BlogPage(Page):  
        posted_by = models.CharField()
        posted_at = models.DateTimeField()
        image = models.ForeignKey('wagtailimages.Image')
        document = models.ForeignKey('wagtaildocs.Document')
        linked_page = models.ForeignKey('wagtailcore.Page')

        def get_api_detail_data(self):  
            return {
                'posted_by': self.posted_by,
                'posted_at': self.posted_at,
                'image': self.image.get_rendition('width-800'),
                'document': self.document,
                'linked_page': self.linked_page,
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
        },
        "linked_page": {
            "id": 18, 
            "title": "Blog post again", 
            "type": "demo.BlogPage"
        }
    }
```


### Nesting listings of pages

You can also nest a listing of pages inside the returned JSON document.

Like with nested pages, each page in the listing would have its ``get_api_summary_data`` method called.

Example:

```
    # models.py

    class BlogIndexPage(Page):  
        def get_blog_pages(self):  
            # Get list of blog pages underneath this page
            return BlogPage.objects.live().descendant_of(self)

        def get_api_detail_data(self):  
            return {
                'blog_pages': self.get_blog_pages(),
            }
```

```
    > http http://localhost:8000/api/v1/pages/5/

    HTTP/1.0 200 OK
    
    {
        "id": 5, 
        "title": "Blog index", 
        "type": "demo.BlogIndexPage",
        "blog_pages": [
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


Filtering, ordering and Searching
---------------------------------

### Filtering by field values

You can do som ebasic 


### Filtering by page type


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

