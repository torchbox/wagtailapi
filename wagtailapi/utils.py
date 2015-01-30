from six.moves.urllib.parse import urlparse

from django.conf import settings


def get_base_url(request):
    base_url = getattr(settings, 'WAGTAILAPI_BASE_URL', request.site.root_url)

    # We only want the scheme and netloc
    base_url_parsed = urlparse(base_url)

    return base_url_parsed.scheme + '://' + base_url_parsed.netloc
