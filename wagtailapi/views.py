from __future__ import absolute_import

import json
import urllib
from functools import wraps
from collections import OrderedDict

from django_filters.filterset import filterset_factory

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, Http404
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import get_image_model
from wagtail.wagtaildocs.models import Document
from wagtail.wagtailcore.utils import resolve_model_string

from . import serialize


class BadAPIRequestError(Exception):
    pass


def get_base_queryset(request, model=Page):
    queryset = model.objects.public().live()

    # Filter by site
    queryset = queryset.descendant_of(request.site.root_page, inclusive=True)

    return queryset


def json_response(data, cls=HttpResponse):
    return cls(
        json.dumps(data, indent=4),
        content_type='application/json'
    )


def format_api_exceptions(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except Http404 as e:
            return json_response({
                'message': str(e)
            }, cls=HttpResponseNotFound)
        except BadAPIRequestError as e:
            return json_response({
                'message': str(e)
            }, cls=HttpResponseBadRequest)

    return wrapper


@format_api_exceptions
def page_listing(request):
    # Get model
    if 'type' in request.GET:
        model_name = request.GET['type']

        try:
            model = resolve_model_string(model_name)
        except LookupError:
            raise Http404("Type doesn't exist")
    else:
        model = Page

    # Get queryset
    queryset = get_base_queryset(request, model=model)

    # Find filterset class
    if hasattr(queryset.model, 'api_filterset_class'):
        filterset_class = queryset.model.filterset_class
    else:
        filterset_class = filterset_factory(queryset.model)

    # Run field filters
    queryset = filterset_class(request.GET, queryset=queryset).qs

    # Child of filter
    if 'child_of' in request.GET:
        parent_page_id = request.GET['child_of']

        try:
            parent_page = Page.objects.get(id=parent_page_id)
            queryset = queryset.child_of(parent_page)
        except Page.DoesNotExist:
            raise Http404("Parent page doesn't exist")

    # Ordering
    if 'order' in request.GET:
        order_by = request.GET['order']

        if order_by == 'random':
             queryset = queryset.order_by('?')
        elif order_by in ('id', 'title'):
            queryset = queryset.order_by(order_by)
        elif hasattr(queryset.model, 'api_fields') and order_by in queryset.model.api_fields:
            # Make sure that the field is a django field
            try:
                field = obj._meta.get_field_by_name(field_name)[0]

                queryset = queryset.order_by(order_by)
            except:
                pass

    # Search
    if 'search' in request.GET:
        search_query = request.GET['search']
        queryset = queryset.search(search_query)

    # Pagination
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    start = offset
    stop = offset + limit
    results = queryset[start:stop]

    # Get list of fields to show in results
    if 'fields' in request.GET:
        fields = request.GET['fields'].split(',')
    else:
        fields = ('title', )

    return json_response(
        OrderedDict([
            ('meta', OrderedDict([
                ('total_count', queryset.count()),
            ])),
            ('pages', [
                serialize.serialize_page(result, fields=fields)
                for result in results
            ]),
        ])
    )


@format_api_exceptions
def page_detail(request, pk):
    page = get_object_or_404(get_base_queryset(request), pk=pk).specific
    data = serialize.serialize_page(page, all_fields=True, parent_id=True)

    return json_response(data)


@format_api_exceptions
def image_listing(request):
    queryset = get_image_model().objects.all()

    # Pagination
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    start = offset
    stop = offset + limit
    results = queryset[start:stop]

    # Get list of fields to show in results
    if 'fields' in request.GET:
        fields = request.GET['fields'].split(',')
    else:
        fields = ('title', )

    return json_response(
        OrderedDict([
            ('meta', OrderedDict([
                ('total_count', queryset.count()),
            ])),
            ('pages', [
                serialize.serialize_image(result, fields=fields)
                for result in results
            ]),
        ])
    )


@format_api_exceptions
def image_detail(request, pk):
    image = get_object_or_404(get_image_model(), pk=pk)
    data = serialize.serialize_image(image, all_fields=True)

    return json_response(data)


@format_api_exceptions
def document_listing(request):
    queryset = Document.objects.all()

    # Pagination
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    start = offset
    stop = offset + limit
    results = queryset[start:stop]

    # Get list of fields to show in results
    if 'fields' in request.GET:
        fields = request.GET['fields'].split(',')
    else:
        fields = ('title', )

    return json_response(
        OrderedDict([
            ('meta', OrderedDict([
                ('total_count', queryset.count()),
            ])),
            ('documents', [
                serialize.serialize_document(result)
                for result in results
            ]),
        ])
    )


@format_api_exceptions
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    data = serialize.serialize_document(document)

    return json_response(data)
