# Wagtail API Documentation

## Usage


### Listing views

Performing a ``GET`` request against one of the endpoints will get you a listing of objects in that endpoint. The response will look a little bit like this:

```json
    GET /api/v1/endpoint name/

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": "total number of results"
        },
        "endpoint name": [
            {

            },
            {

            }
        ]
    }
```

This is the basic structure of all of the listing views. They all have a ``meta`` section with a ``total_count`` variable and a listing of things.


### Detail views

All of the endpoints also contain a "detail" view which returns information on an individual object. This view is always acessed by appending the id of the object to the URL.


### The ``pages`` endpoint

This endpoint includes all live pages in your site that have not been put in a private section.


#### The listing view (``/api/v1/pages/``)


This is what a typical response from a ``GET`` request to this listing would look like:

```json
    GET /api/v1/pages/

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": 2
        },
        "pages": [
            {
                "id": 2,
                "meta": {
                    "type": "demo.HomePage"
                },
                "title": "Homepage"
            },
            {
                "id": 3,
                "meta": {
                    "type": "demo.BlogIndexPage"
                },
                "title": "Blog"
            }
        ]
    }
```

Each page object contains the ``id``, a ``meta`` section and the fields with their values.


##### ``meta``

This section is for any piece of information that is useful, but not a database field. The initial implementation only includes the type name here, but possible additions would be things like urls to relevant parts of the api (eg. detail/edit views), status, parent page, etc.


##### Selecting a page type

Most Wagtail sites are made up of multiple different types of page that each have their own specific fields. In order to view/filter/order on fields specific to one page type, you must select that page type using the ``type`` query parameter.

The ``type`` query parameter must be set to the Pages model name in the format: ``app_label.ModelName``.

```json
    GET /api/v1/pages/?type=demo.BlogPage

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": 3
        },
        "pages": [
            {
                "id": 4,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 1"
            },
            {
                "id": 5,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 2"
            },
            {
                "id": 6,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 3"
            }
        ]
    }
```


##### Specifying a list of fields to return

As you can see, we still only get the ``title`` field, even though we have selected a type. That's because listing pages require you to explicitly tell it what extra fields you would like to see. You can do this with the ``fields`` query parameter.

Just set ``fields`` to a command-separated list of field names that you would like to use.

```json
    GET /api/v1/pages/?type=demo.BlogPage&fields=title,date_posted,feed_image

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": 3
        },
        "pages": [
            {
                "id": 4,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 1",
                "date_posted": "2015-01-23",
                "feed_image": 1
            },
            {
                "id": 5,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 2",
                "date_posted": "2015-01-24",
                "feed_image": 2
            },
            {
                "id": 6,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 3",
                "date_posted": "2015-01-25",
                "feed_image": 3
            }
        ]
    }
```

We now have enough information to make a basic blog listing with a feed image and date that the blog was posted.


##### Filtering on fields

Exact matches on field values can be done by using a query parameter with the same name as the field. Any pages with the field that exactly matches the value of this parameter will be returned.

```json
    GET /api/v1/pages/?type=demo.BlogPage&date_posted=2015-01-24

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": 1
        },
        "pages": [

            {
                "id": 5,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 2",
                "date_posted": "2015-01-24",
                "feed_image": 2
            }
        ]
    }
```


##### Filtering by section of the tree

It is also possible to filter the listing to only include pages with a particular parent. This is useful if you have multiple blogs on your site and only want to view the contents of one of them.

For example (imagine we are in the same project as all previous examples, and page id ``7`` refers to the other blog index):

```json
    GET /api/v1/pages/?type=demo.BlogPage&child_of=7

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": 1
        },
        "pages": [
            {
                "id": 4,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "Other blog 1"
            }
        ]
    }
```


##### Ordering

Like filtering, it is also possible to order on database fields. The endpoint accepts a query parameter called ``order`` which should be set to the field name to order by. Field names can be prefixed with a ``-`` to reverse the ordering. It is also possible to order randomly by setting this parameter to ``random``.

```json
    GET /api/v1/pages/?type=demo.BlogPage&order=-date_posted

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": 3
        },
        "pages": [
            {
                "id": 6,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 3",
                "date_posted": "2015-01-25",
                "feed_image": 3
            },
            {
                "id": 5,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 2",
                "date_posted": "2015-01-24",
                "feed_image": 2
            },
            {
                "id": 4,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 1",
                "date_posted": "2015-01-23",
                "feed_image": 1
            }
        ]
    }
```


##### Pagination

Pagination is done using two query parameters called ``limit`` and ``offset``. ``limit`` sets the number of results to return and ``offset`` is the index of the first result to return. The default value for ``limit`` is ``20`` and its maximum value is ``100`` (which can be changed using the ``WAGTAILAPI_MAX_RESULTS`` setting).

```json
    GET /api/v1/pages/?limit=1&offset=1

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": 2
        },
        "pages": [
            {
                "id": 3,
                "meta": {
                    "type": "demo.BlogIndexPage"
                },
                "title": "Blog"
            }
        ]
    }
```

Pagination will not change the ``total_count`` value in the meta.


##### Searching

To perform a full-text search, set the ``search`` parameter to the query string you would like to search on.

```json
    GET /api/v1/pages/?search=Blog

    HTTP 200 OK
    Content-Type: application/json

    {
        "meta": {
            "total_count": 3
        },
        "pages": [
            {
                "id": 3,
                "meta": {
                    "type": "demo.BlogIndexPage"
                },
                "title": "Blog"
            },
            {
                "id": 4,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 1",
            },
            {
                "id": 5,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 2",
            },
            {
                "id": 6,
                "meta": {
                    "type": "demo.BlogPage"
                },
                "title": "My blog 3",
            }
        ]
    }
```

The results are ordered by relevance. It is not possible to use the ``order`` parameter with a search query.

Also, if your Wagtail site is using Elasticsearch, you do not need to select a type to access specific fields. This will search anything that's defined in the models' ``search_fields``.


##### Reference

Parameters:
 * ``type``
 * ``limit``
 * ``offset``
 * ``fields``
 * ``child_of``
 * ``order``
 * ``search``


#### The detail view (``/api/v1/pages/{id}/``)

This view gives you access to all of the details for a particular page.

```json
    GET /api/v1/pages/6/

    HTTP 200 OK
    Content-Type: application/json

    {
        "id": 6,
        "meta": {
            "type": "demo.BlogPage",
            "parent_id": 3
        },
        "title": "My blog 3",
        "date_posted": "2015-01-25",
        "feed_image": 3,
        "related_links": [
            {
                "title": "Other blog page",
                "page": 6
            }
        ]
    }
```

The format is the same as what is returned inside the listing view, with two additions:
 - All of the available fields are added to the detail page by default
 - The ``meta`` section has a ``parent_id`` field that contains the ID of the parent page


The ``images`` endpoint
-----------------------

This endpoint gives access to all uploaded images. This will use the custom image model if one was specified. Otherwise, it falls back to ``wagtailimages.Image``.


#### The listing view (``/api/v1/images/``)


#### The detail view (``/api/v1/images/{id}/``)



The ``documents`` endpoint
--------------------------

This endpoint gives access to all uploaded documents.


#### The listing view (``/api/v1/documents/``)


#### The detail view (``/api/v1/documents/{id}/``)

