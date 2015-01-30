# Wagtail API Documentation

## Installation

The ``wagtailapi`` module can be installed with ``pip``:

``` python
    pip install wagtailapi
```

Once installed, you then need to add ``wagtailapi`` to ``INSTALLED_APPS`` in your Django settings and configure a URL for it in ``urls.py``

``` python
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
