from __future__ import absolute_import

import json
import urllib

from django_filters.filterset import filterset_factory

from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.utils import resolve_model_string

from . import serialize
from .json import WagtailAPIJSONEncoder


class WagtailAPIPagesListing(object):
    def __init__(self, **kwargs):
        self.site = kwargs.pop('site', None)
        self.model_name = kwargs.pop('type', None)
        self.page_number = kwargs.pop('page', 1)
        self.search_query = kwargs.pop('search', '')
        self.filters = kwargs

    def get_model(self):
        if self.model_name:
            return resolve_model_string(self.model_name)
        else:
            return Page

    def run_filters(self, queryset, filters):
        # Find filterset class
        if hasattr(queryset.model, 'filterset_class'):
            filterset_class = queryset.model.filterset_class
        elif hasattr(queryset.model, 'get_filterset_class'):
            filterset_class = queryset.model.get_filterset_class()
        else:
            filterset_class = filterset_factory(queryset.model)

        # Run field filters
        queryset = filterset_class(filters, queryset=queryset).qs

        return queryset

    def get_queryset(self):
        model = self.get_model()
        queryset = model.objects.live().public()

        # Filter by site
        if self.site:
            queryset = queryset.descendant_of(self.site.root_page, inclusive=True)

        # Run filters
        queryset = self.run_filters(queryset, self.filters)

        # Search
        if self.search_query:
            queryset = queryset.search(self.search_query)

        return queryset

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

    @classmethod
    def from_request(cls, request):
        return cls(
            site=request.site,
            **dict(request.GET.iteritems())
        )


class WagtailPagesAPI(object):
    def listing_view(self, request):
        listing = WagtailAPIPagesListing.from_request(request)
        all_results = listing.get_queryset()

        # Pagination
        paginator = Paginator(all_results, 10)
        try:
            paginator_page = paginator.page(listing.page_number)
        except PageNotAnInteger:
            paginator_page = paginator.page(1)
        except EmptyPage:
            paginator_page = paginator.page(paginator.num_pages)

        # Response data
        response_data = {
            'count': all_results.count(),
            'results': paginator_page.object_list,
        }

        # Next/previous urls
        if paginator_page.has_next():
            query_params = listing.get_query_params()
            query_params['page'] = paginator_page.next_page_number()
            response_data['next'] = request.path + '?' + urllib.urlencode(query_params)

        if paginator_page.has_previous():
            query_params = listing.get_query_params()
            query_params['page'] = paginator_page.previous_page_number()
            response_data['previous'] = request.path + '?' + urllib.urlencode(query_params)

        return self.response(request, response_data)

    def detail_view(self, request, page_id):
        page = get_object_or_404(Page.objects.public().live(), id=page_id).specific
        data = serialize.serialize_page(page, with_details=True)

        return self.response(request, data)

    def get_urlpatterns(self):
        return [
            url(r'^$', self.listing_view, name='listing'),
            url(r'^(\d+)/$', self.detail_view, name='detail'),
        ]

    def response(self, request, data):
        response = HttpResponse(json.dumps(data, cls=WagtailAPIJSONEncoder), content_type="application/json")
        response['Access-Control-Allow-Origin'] = 'http://localhost:8000'
        return response

    def reverse(self, name, args=None, kwargs=None):
        return reverse('wagtailapi_v1_pages:' + name, args=args, kwargs=kwargs)
