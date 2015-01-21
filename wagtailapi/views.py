from __future__ import absolute_import

import json
import urllib

from django_filters.filterset import filterset_factory

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.utils import resolve_model_string

from . import serialize
from .json import WagtailAPIJSONEncoder


class PageListingFilters(object):
    def __init__(self, filters):
        self.model_name = filters.pop('type', None)
        self.page_number = filters.pop('page', 1)
        self.search_query = filters.pop('search', '')
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
        if hasattr(queryset.model, 'filterset_class'):
            filterset_class = queryset.model.filterset_class
        elif hasattr(queryset.model, 'get_filterset_class'):
            filterset_class = queryset.model.get_filterset_class()
        else:
            filterset_class = filterset_factory(queryset.model)

        # Run field filters
        queryset = filterset_class(self.filters, queryset=queryset).qs

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
    data = serialize.serialize_page(page, with_details=True)

    return json_response(data)
