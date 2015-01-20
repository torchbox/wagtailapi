from rest_framework import serializers

from wagtailapi import serialize


class PageSerializer(serializers.ModelSerializer):
    pass


class PageField(serializers.RelatedField):
    def to_representation(self, page):
        return serialize.serialize_page(page)


class ImageField(serializers.RelatedField):
    def to_representation(self, image):
        return serialize.serialize_image(image)


class ImageRenditionField(ImageField):
    def __init__(self, filter_spec, *args, **kwargs):
        super(ImageRenditionField, self).__init__(*args, **kwargs)
        self.filter_spec = filter_spec

    def to_representation(self, image):
        rendition = image.get_rendition(self.filter_spec)
        return serialize.serialize_rendition(rendition)


class DocumentField(serializers.RelatedField):
    def to_representation(self, document):
        return serialize.serialize_document(document)
