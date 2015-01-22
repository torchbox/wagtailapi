from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model, QuerySet

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.query import PageQuerySet
from wagtail.wagtailimages.models import AbstractImage
from wagtail.wagtaildocs.models import Document

from . import serialize


class WagtailAPIJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Page):
            return serialize.serialize_page(o)
        elif isinstance(o, AbstractImage):
            return serialize.serialize_image(o)
        elif isinstance(o, Document):
            return serialize.serialize_document(o)
        elif isinstance(o, Model):
            return o.pk
        elif isinstance(o, QuerySet):
            return list(o)
        else:
            return super(WagtailAPIJSONEncoder, self).default(o)
