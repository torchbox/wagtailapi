from __future__ import absolute_import

import json
import urllib

from django_filters.filterset import filterset_factory

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import get_image_model
from wagtail.wagtaildocs.models import Document
from wagtail.wagtailcore.utils import resolve_model_string

from . import serialize
from .json import WagtailAPIJSONEncoder


def parse_int(i):
    if i:
        try:
            return int(i)
        except ValueError:
            pass


class PageListingFilters(object):
    def __init__(self, filters):
        self.model_name = filters.pop('type', None)
        self.page_number = filters.pop('page', 1)
        self.search_query = filters.pop('search', '')
        self.order_by = filters.pop('order', '')

        self.exclude = parse_int(filters.pop('exclude', None))
        self.child_of = parse_int(filters.pop('child_of', None))

        self.filters = filters

    @classmethod
    def from_request(cls, request):
        return cls(dict(request.GET.iteritems()))

    def get_model(self):
        if self.model_name:
            return resolve_model_string(self.model_name)
        else:
            return Page

    def filter_queryset(self, queryset):
        # Find filterset class
        if hasattr(queryset.model, 'api_filterset_class'):
            filterset_class = queryset.model.filterset_class
        else:
            filterset_class = filterset_factory(queryset.model)

        # Run field filters
        queryset = filterset_class(self.filters, queryset=queryset).qs

        # Exclusion filter
        if self.exclude:
            queryset = queryset.exclude(id=self.exclude)

        # Child of filter
        if self.child_of:
            parent_page = Page.objects.get(id=self.child_of)
            queryset = queryset.child_of(parent_page)

        # Ordering
        if self.order_by:
            if self.order_by == 'random':
                 queryset = queryset.order_by('?')
            elif self.order_by in ('id', 'title'):
                queryset = queryset.order_by(self.order_by)
            elif hasattr(queryset.model, 'api_fields') and self.order_by in queryset.model.api_fields:
                # Make sure that the field is a django field
                try:
                    field = obj._meta.get_field_by_name(field_name)[0]

                    queryset = queryset.order_by(self.order_by)
                except:
                    pass

        # Search
        if self.search_query:
            queryset = queryset.search(self.search_query)

        # Pagination
        paginator = Paginator(queryset, 10)
        try:
            results = paginator.page(self.page_number)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        return results

    def get_query_params(self):
        query_params = {}

        if self.page_number and self.page_number != 1:
            query_params['page'] = self.page_number

        if self.model_name:
            query_params['type'] = self.model_name

        if self.order_by:
            query_params['order'] = self.order_by

        if self.exclude:
            query_params['exclude'] = self.exclude

        if self.child_of:
            query_params['child_of'] = self.child_of

        if self.search_query:
            query_params['search'] = self.search_query

        query_params.update(self.filters)

        return query_params


def get_base_queryset(request, model=Page):
    queryset = model.objects.public().live()

    # Filter by site
    queryset = queryset.descendant_of(request.site.root_page, inclusive=True)

    return queryset


def json_response(data):
    return HttpResponse(
        json.dumps(data, cls=WagtailAPIJSONEncoder, sort_keys=True, indent=4),
        content_type='application/json'
    )


def page_listing(request):
    filters = PageListingFilters.from_request(request)
    queryset = get_base_queryset(request, model=filters.get_model())
    results = filters.filter_queryset(queryset)

    # Response data
    data = {
        'count': results.paginator.count,
        'results': list(results.object_list),
        'previous': None,
        'next': None,
    }

    # Next/previous urls
    if results.has_next():
        query_params = filters.get_query_params()
        query_params['page'] = results.next_page_number()
        data['next'] = request.path + '?' + urllib.urlencode(query_params)

    if results.has_previous():
        query_params = filters.get_query_params()
        query_params['page'] = results.previous_page_number()
        data['previous'] = request.path + '?' + urllib.urlencode(query_params)

    return json_response(data)


def page_detail(request, pk):
    page = get_object_or_404(get_base_queryset(request), pk=pk).specific
    data = serialize.serialize_page(page, show_child_relations=True)

    return json_response(data)


def image_listing(request):
    queryset = get_image_model().objects.all()

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
    try:
        results = paginator.page(page_number)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    # Response data
    data = {
        'count': results.paginator.count,
        'results': list(results.object_list),
        'previous': None,
        'next': None,
    }

    # Next/previous urls
    if results.has_next():
        query_params = {}
        query_params['page'] = results.next_page_number()
        data['next'] = request.path + '?' + urllib.urlencode(query_params)

    if results.has_previous():
        query_params = {}
        query_params['page'] = results.previous_page_number()
        data['previous'] = request.path + '?' + urllib.urlencode(query_params)

    return json_response(data)


def image_detail(request, pk):
    image = get_object_or_404(get_image_model(), pk=pk)
    data = serialize.serialize_image(image)

    return json_response(data)


def document_listing(request):
    queryset = Document.objects.all()

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)
    try:
        results = paginator.page(page_number)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    # Response data
    data = {
        'count': results.paginator.count,
        'results': list(results.object_list),
        'previous': None,
        'next': None,
    }

    # Next/previous urls
    if results.has_next():
        query_params = {}
        query_params['page'] = results.next_page_number()
        data['next'] = request.path + '?' + urllib.urlencode(query_params)

    if results.has_previous():
        query_params = {}
        query_params['page'] = results.previous_page_number()
        data['previous'] = request.path + '?' + urllib.urlencode(query_params)

    return json_response(data)


def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    data = serialize.serialize_image(document)

    return json_response(data)
