from collections import OrderedDict

from django.db import models
from django.utils.encoding import force_text

from wagtail.wagtailcore.models import Page


def get_api_data(obj, fields):
    # Find any child relations (pages only)
    child_relations = {}
    if isinstance(obj, Page):
        child_relations = {
            child_relation.field.rel.related_name: child_relation.model
            for child_relation in obj._meta.child_relations
        }

    # Loop through fields
    for field_name in fields:
        # Check child relations
        if field_name in child_relations and hasattr(child_relations[field_name], 'api_fields'):
            yield field_name, [
                dict(get_api_data(child_object, child_relations[field_name].api_fields))
                for child_object in getattr(obj, field_name).all()
            ]
            continue

        # Check django fields
        try:
            field = obj._meta.get_field_by_name(field_name)[0]
            yield field_name, field._get_val_from_obj(obj)
            continue
        except (models.fields.FieldDoesNotExist, AttributeError):
            pass

        # Check attributes
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            if hasattr(value, '__call__'):
                value = value()

            yield field_name, force_text(value, strings_only=True)
            continue


def serialize_page(page, fields=('title', ), all_fields=False, parent_id=False):
    # Build metadata document
    metadata = [
        ('type', page.specific_class._meta.app_label + '.' + page.specific_class.__name__),
    ]

    if parent_id:
        metadata.append(('parent_id', page.get_parent().id))

    # Build data document
    data = [
        ('id', page.id),
        ('meta', OrderedDict(metadata)),
    ]

    if hasattr(page.specific_class, 'api_fields'):
        api_fields = ('title', ) + tuple(page.specific_class.api_fields)
        if all_fields:
            # Show all possible fields
            fields = api_fields
        else:
            # Remove any fields that are not defined in "api_fields"
            fields = [field for field in fields if field in api_fields]

    data.extend(get_api_data(page, fields))

    return OrderedDict(data)


def serialize_document(document):
    return OrderedDict([
        ('id', document.id),
        ('title', document.title),
        ('download_url', document.url),
    ])


def serialize_image(image, fields=('title', ), all_fields=False):
    # Build data document
    data = [
        ('id', image.id),
    ]

    if hasattr(image, 'api_fields'):
        api_fields = ('title', ) + tuple(image.api_fields)
        if all_fields:
            # Show all possible fields
            fields = api_fields
        else:
            # Remove any fields that are not defined in "api_fields"
            fields = [field for field in fields if field in api_fields]

    data.extend(get_api_data(image, fields))

    return OrderedDict(data)
