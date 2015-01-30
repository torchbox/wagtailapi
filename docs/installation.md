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
