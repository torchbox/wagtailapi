def serialize_page(page, with_details=False):
    specific_class = page.specific_class

    # Create a basic document that describes the page
    data = {
        'id': page.id,
        'title': page.title,
        'type': specific_class._meta.app_label + '.' + specific_class.__name__,
    }

    if with_details and hasattr(specific_class, 'get_api_detail_data'):
        # Add detail data
        data.update(page.specific.get_api_detail_data())
    elif hasattr(specific_class, 'get_api_summary_data'):
        # Add summary data
        data.update(page.specific.get_api_summary_data())

    # Add data from child relations
    if with_details:
        for child_relation in specific_class._meta.child_relations:
            if hasattr(child_relation.model, 'get_api_data'):
                parental_key_name = child_relation.field.rel.related_name
                child_objects = getattr(page.specific, child_relation.get_accessor_name(), None)

                data[parental_key_name] = [
                    child_object.get_api_data()
                    for child_object in child_objects.all()
                ]

    return data


def serialize_pagequeryset(queryset):
    return [
        serialize_page(page)
        for page in queryset
    ]


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


def serialize_rendition(rendition):
    return {
        'image': serialize_image(rendition.image),
        'download_url': rendition.url,
        'width': rendition.width,
        'height': rendition.height,
    }
