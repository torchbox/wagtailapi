from django.db import models
from django.utils.encoding import force_text

from wagtail.wagtailcore.models import Page


def get_api_data(obj, show_child_relations=False):
    # Find any child relations (pages only)
    child_relations = {}
    if isinstance(obj, Page):
        child_relations = {
            child_relation.field.rel.related_name: child_relation.model
            for child_relation in obj._meta.child_relations
        }

    # Loop through fields
    for field_name in obj.api_fields:
        # Check child relations
        if field_name in child_relations and hasattr(child_relations[field_name], 'api_fields'):
            if not show_child_relations:
                continue

            yield field_name, [
                dict(get_api_data(child_object))
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


def serialize_page(page, show_child_relations=False):
    # Create a basic document that describes the page
    data = {
        'id': page.id,
        'title': page.title,
        'type': page.specific_class._meta.app_label + '.' + page.specific_class.__name__,
    }

    if hasattr(page, 'api_fields'):
        # Add detail data
        data.update(dict(get_api_data(page, show_child_relations=show_child_relations)))

    return data


def serialize_document(document):
    return {
        'id': document.id,
        'title': document.title,
        'download_url': document.url,
    }


def serialize_image(image):
    return {
        'id': image.id,
        'title': image.title,
    }
