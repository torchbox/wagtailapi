from __future__ import absolute_import

import json
import urllib
from functools import wraps
from collections import OrderedDict

from modelcluster.models import get_all_child_relations
from taggit.managers import _TaggableManager
from taggit.models import Tag

from django.db import models
from django.utils.encoding import force_text
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, Http404
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.conf.urls import url
from django.conf import settings

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import get_image_model
from wagtail.wagtaildocs.models import Document
from wagtail.wagtailcore.utils import resolve_model_string
from wagtail.wagtailsearch.backends import get_search_backend

from .utils import get_base_url


class WagtailAPIJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, _TaggableManager):
            return list(o.all())
        elif isinstance(o, Tag):
            return o.name
        else:
            return super(WagtailAPIJSONEncoder, self).default(o)


def get_api_data(obj, fields):
    # Find any child relations (pages only)
    child_relations = {}
    if isinstance(obj, Page):
        child_relations = {
            child_relation.field.rel.related_name: child_relation.model
            for child_relation in get_all_child_relations(type(obj))
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
        except models.fields.FieldDoesNotExist:
            pass

        # Check attributes
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            yield field_name, force_text(value, strings_only=True)
            continue


class BaseAPIEndpoint(object):
    class BadRequestError(Exception):
        pass

    known_query_parameters = (
        'limit',
        'offset',
        'fields',
        'order',
        'search',
    )

    def listing_view(self, request):
        return NotImplemented

    def detail_view(self, request, pk):
        return NotImplemented

    def get_api_fields(self, model):
        """
        This returns a list of field names that are allowed to
        be used in the API (excluding the id field).
        """
        api_fields = []

        if hasattr(model, 'api_fields'):
            api_fields.extend(model.api_fields)

        return api_fields

    def serialize_object_metadata(self, obj, show_details=False, base_url=None):
        """
        This returns a JSON-serialisable dict to use for the "meta"
        section of a particlular object.
        """
        return OrderedDict()

    def serialize_object(self, obj, fields=(), all_fields=False, show_details=False, base_url=None):
        """
        This converts an object into JSON-serialisable dict so it can
        be used in the API.
        """
        data = [
            ('id', obj.id),
        ]

        # Add meta
        metadata = self.serialize_object_metadata(obj, show_details=show_details, base_url=base_url)
        if metadata:
            data.append(('meta', metadata))

        # Add other fields
        api_fields = self.get_api_fields(type(obj))
        if all_fields:
            fields = api_fields
        else:
            bad_fields = [field for field in fields if field not in api_fields]

            if bad_fields:
                raise self.BadRequestError("unknown fields: %s" % ', '.join(bad_fields))

        data.extend(get_api_data(obj, fields))

        return OrderedDict(data)

    def check_query_parameters(self, request, queryset):
        query_parameters = set(request.GET.keys())

        # All query paramters must be either a field or an operation
        allowed_query_parameters = set(list(self.known_query_parameters) + self.get_api_fields(queryset.model))
        bad_parameters = query_parameters - allowed_query_parameters
        if bad_parameters:
            raise self.BadRequestError("query parameter is not an operation or a recognised field: %s" % ', '.join(bad_parameters))

    def do_field_filtering(self, request, queryset):
        """
        This performs field level filtering on the result set
        Eg: ?title=James Joyce
        """
        fields = self.get_api_fields(queryset.model)

        for field_name, value in request.GET.items():
            if field_name in fields:
                field = getattr(queryset.model, field_name, None)

                if isinstance(field, _TaggableManager):
                    for tag in value.split(','):
                        queryset = queryset.filter(**{field_name + '__name': tag})

                    # Stick a message on the queryset to indicate that tag filtering has been performed
                    # This will let the do_search method know that it must raise an error as searching
                    # and tag filtering at the same time is not supported
                    queryset._filtered_by_tag = True
                else:
                    queryset = queryset.filter(**{field_name: value})

        return queryset

    def do_ordering(self, request, queryset):
        """
        This applies ordering to the result set
        Eg: ?order=title

        It also supports reverse ordering
        Eg: ?order=-title

        And random ordering
        Eg: ?order=random
        """
        if 'order' in request.GET:
            # Prevent ordering while searching
            if 'search' in request.GET:
                raise self.BadRequestError("ordering with a search query is not supported")

            order_by = request.GET['order']

            # Random ordering
            if order_by == 'random':
                # Prevent ordering by random with offset
                if 'offset' in request.GET:
                    raise self.BadRequestError("random ordering with offset is not supported")

                return queryset.order_by('?')

            # Check if reverse ordering is set
            if order_by.startswith('-'):
                reverse_order = True
                order_by = order_by[1:]
            else:
                reverse_order = False

            # Add ordering
            if order_by == 'id' or order_by in self.get_api_fields(queryset.model):
                queryset = queryset.order_by(order_by)
            else:
                # Unknown field
                raise self.BadRequestError("cannot order by '%s' (unknown field)" % order_by)

            # Reverse order
            if reverse_order:
                queryset = queryset.reverse()

        return queryset

    def do_search(self, request, queryset):
        """
        This performs a full-text search on the result set
        Eg: ?search=James Joyce
        """
        search_enabled = getattr(settings, 'WAGTAILAPI_SEARCH_ENABLED', True)

        if 'search' in request.GET:
            if not search_enabled:
                raise self.BadRequestError("search is disabled")

            # Searching and filtering by tag at the same time is not supported
            if getattr(queryset, '_filtered_by_tag', False):
                raise self.BadRequestError("filtering by tag with a search query is not supported")

            search_query = request.GET['search']

            sb = get_search_backend()
            queryset = sb.search(search_query, queryset)

        return queryset

    def do_pagination(self, request, queryset):
        """
        This performs limit/offset based pagination on the result set
        Eg: ?limit=10&offset=20 -- Returns 10 items starting at item 20
        """
        limit_max = getattr(settings, 'WAGTAILAPI_LIMIT_MAX', 20)

        try:
            offset = int(request.GET.get('offset', 0))
            assert offset >= 0
        except (ValueError, AssertionError):
            raise self.BadRequestError("offset must be a positive integer")

        try:
            limit = int(request.GET.get('limit', min(20, limit_max)))

            if limit > limit_max:
                raise self.BadRequestError("limit cannot be higher than %d" % limit_max)

            assert limit >= 0
        except (ValueError, AssertionError):
            raise self.BadRequestError("limit must be a positive integer")

        start = offset
        stop = offset + limit

        return queryset[start:stop]

    def json_response(self, data, response_cls=HttpResponse):
        """
        This takes a JSON-serialisable thing and builds a HTTP response
        from it
        """
        return response_cls(
            json.dumps(data, indent=4, cls=WagtailAPIJSONEncoder),
            content_type='application/json'
        )

    def api_view(self, view):
        """
        This is a decorator that is applied to all API views.

        It's only job currently is to catch Http404 and BadRequestError
        exceptions and convert them into nicer error messages for the user.
        """
        @wraps(view)
        def wrapper(*args, **kwargs):
            # Catch exceptions and format them as JSON documents
            try:
                return view(*args, **kwargs)
            except Http404 as e:
                return self.json_response({
                    'message': str(e)
                }, response_cls=HttpResponseNotFound)
            except self.BadRequestError as e:
                return self.json_response({
                    'message': str(e)
                }, response_cls=HttpResponseBadRequest)

        return wrapper

    def get_urlpatterns(self):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            url(r'^$', self.api_view(self.listing_view), name='listing'),
            url(r'^(\d+)/$', self.api_view(self.detail_view), name='detail'),
        ]


class PagesAPIEndpoint(BaseAPIEndpoint):
    known_query_parameters = BaseAPIEndpoint.known_query_parameters + (
        'type',
        'child_of',
    )

    def get_queryset(self, request, model=Page):
        # Get live pages that are not in a private section
        queryset = model.objects.public().live()

        # Filter by site
        queryset = queryset.descendant_of(request.site.root_page, inclusive=True)

        return queryset

    def get_api_fields(self, model):
        api_fields = ['title']
        api_fields.extend(super(PagesAPIEndpoint, self).get_api_fields(model))
        return api_fields

    def serialize_object_metadata(self, page, show_details=False, base_url=None):
        data = super(PagesAPIEndpoint, self).serialize_object_metadata(page, show_details=show_details, base_url=base_url)

        # Add type
        data['type'] = page.specific_class._meta.app_label + '.' + page.specific_class.__name__

        # Add parent id
        if show_details:
            data['parent_id'] = page.get_parent().id

        return data

    def get_model(self, request):
        if 'type' not in request.GET:
            return Page

        model_name = request.GET['type']
        try:
            return resolve_model_string(model_name)
        except LookupError:
            raise self.BadRequestError("type doesn't exist")

    def do_child_of_filter(self, request, queryset):
        if 'child_of' in request.GET:
            parent_page_id = request.GET['child_of']

            try:
                parent_page = Page.objects.get(id=parent_page_id)
                return queryset.child_of(parent_page)
            except Page.DoesNotExist:
                raise self.BadRequestError("parent page doesn't exist")

        return queryset

    def listing_view(self, request):
        # Get model and queryset
        model = self.get_model(request)
        queryset = self.get_queryset(request, model=model)

        # Check query paramters
        self.check_query_parameters(request, queryset)

        # Filtering
        queryset = self.do_field_filtering(request, queryset)
        queryset = self.do_child_of_filter(request, queryset)

        # Ordering
        queryset = self.do_ordering(request, queryset)

        # Search
        queryset = self.do_search(request, queryset)

        # Pagination
        total_count = queryset.count()
        queryset = self.do_pagination(request, queryset)

        # Get list of fields to show in results
        if 'fields' in request.GET:
            fields = request.GET['fields'].split(',')
        else:
            fields = ('title', )

        return self.json_response(
            OrderedDict([
                ('meta', OrderedDict([
                    ('total_count', total_count),
                ])),
                ('pages', [
                    self.serialize_object(page, fields=fields, base_url=get_base_url(request))
                    for page in queryset
                ]),
            ])
        )

    def detail_view(self, request, pk):
        page = get_object_or_404(self.get_queryset(request), pk=pk).specific
        data = self.serialize_object(page, all_fields=True, show_details=True, base_url=get_base_url(request))

        return self.json_response(data)


class ImagesAPIEndpoint(BaseAPIEndpoint):
    model = get_image_model()

    def get_queryset(self, request):
        return self.model.objects.all()

    def get_api_fields(self, model):
        api_fields = ['title', 'tags', 'width', 'height']
        api_fields.extend(super(ImagesAPIEndpoint, self).get_api_fields(model))
        return api_fields

    def listing_view(self, request):
        queryset = self.get_queryset(request)

        # Check query paramters
        self.check_query_parameters(request, queryset)

        # Filtering
        queryset = self.do_field_filtering(request, queryset)

        # Ordering
        queryset = self.do_ordering(request, queryset)

        # Search
        queryset = self.do_search(request, queryset)

        # Pagination
        total_count = queryset.count()
        queryset = self.do_pagination(request, queryset)

        # Get list of fields to show in results
        if 'fields' in request.GET:
            fields = request.GET['fields'].split(',')
        else:
            fields = ('title', )

        return self.json_response(
            OrderedDict([
                ('meta', OrderedDict([
                    ('total_count', total_count),
                ])),
                ('images', [
                    self.serialize_object(image, fields=fields, base_url=get_base_url(request))
                    for image in queryset
                ]),
            ])
        )

    def detail_view(self, request, pk):
        image = get_object_or_404(self.get_queryset(request), pk=pk)
        data = self.serialize_object(image, all_fields=True, base_url=get_base_url(request))

        return self.json_response(data)


class DocumentsAPIEndpoint(BaseAPIEndpoint):
    def get_api_fields(self, model):
        api_fields = ['title', 'tags']
        api_fields.extend(super(DocumentsAPIEndpoint, self).get_api_fields(model))
        return api_fields

    def serialize_object_metadata(self, document, show_details=False, base_url=None):
        data = super(DocumentsAPIEndpoint, self).serialize_object_metadata(document, show_details=show_details, base_url=base_url)

        # Download URL
        if show_details:
            data['download_url'] = (base_url or '') + document.url

        return data

    def listing_view(self, request):
        queryset = Document.objects.all()

        # Check query paramters
        self.check_query_parameters(request, queryset)

        # Filtering
        queryset = self.do_field_filtering(request, queryset)

        # Ordering
        queryset = self.do_ordering(request, queryset)

        # Search
        queryset = self.do_search(request, queryset)

        # Pagination
        total_count = queryset.count()
        queryset = self.do_pagination(request, queryset)

        # Get list of fields to show in results
        if 'fields' in request.GET:
            fields = request.GET['fields'].split(',')
        else:
            fields = ('title', )

        return self.json_response(
            OrderedDict([
                ('meta', OrderedDict([
                    ('total_count', total_count),
                ])),
                ('documents', [
                    self.serialize_object(document, fields=fields, base_url=get_base_url(request))
                    for document in queryset
                ]),
            ])
        )

    def detail_view(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        data = self.serialize_object(document, all_fields=True, show_details=True, base_url=get_base_url(request))

        return self.json_response(data)
