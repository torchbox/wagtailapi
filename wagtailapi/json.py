from django.core.serializers.json import DjangoJSONEncoder

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.query import PageQuerySet
from wagtail.wagtailimages.models import AbstractImage, AbstractRendition
from wagtail.wagtaildocs.models import Document

from . import serialize


class WagtailAPIJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Page):
            return serialize.serialize_page(o)
        if isinstance(o, PageQuerySet):
            return serialize.serialize_pagequeryset(o)
        elif isinstance(o, AbstractImage):
            return serialize.serialize_image(o)
        elif isinstance(o, AbstractRendition):
            return serialize.serialize_rendition(o)
        elif isinstance(o, Document):
            return serialize.serialize_document(o)
        else:
            return super(WagtailAPIJSONEncoder, self).default(o)
