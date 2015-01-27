from __future__ import absolute_import

import json
import urllib
from functools import wraps
from collections import OrderedDict

from django_filters.filterset import filterset_factory

from django.db import models
from django.utils.encoding import force_text
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, Http404
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.conf.urls import url

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import get_image_model
from wagtail.wagtaildocs.models import Document
from wagtail.wagtailcore.utils import resolve_model_string
from wagtail.wagtailsearch.backends import get_search_backend


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


class BaseAPIEndpoint(object):
    class BadRequestError(Exception):
        pass

    def listing_view(self, request):
        pass

    def detail_view(self, request, pk):
        pass

    def json_response(self, data, response_cls=HttpResponse):
        return response_cls(
            json.dumps(data, indent=4, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

    def api_view(self, view):
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
        return [
            url(r'^$', self.api_view(self.listing_view), name='listing'),
            url(r'^(\d+)/$', self.api_view(self.detail_view), name='detail'),
        ]


class PagesAPIEndpoint(BaseAPIEndpoint):
    def get_queryset(self, request, model=Page):
        # Get live pages that are not in a private section
        queryset = model.objects.public().live()

        # Filter by site
        queryset = queryset.descendant_of(request.site.root_page, inclusive=True)

        return queryset

    def serialize_page(self, page, fields=('title', ), all_fields=False, parent_id=False):
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

        allowed_fields = ['title']
        if hasattr(page, 'api_fields'):
            allowed_fields.extend(page.api_fields)

        if all_fields:
            # Show all possible fields
            fields = allowed_fields
        else:
            # Remove any fields that are not defined in allowed_fields
            fields = [field for field in fields if field in allowed_fields]

        data.extend(get_api_data(page, fields))

        return OrderedDict(data)

    def listing_view(self, request):
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
        queryset = self.get_queryset(request, model=model)

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

            if order_by in ('id', 'title'):
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
        try:
            offset = int(request.GET.get('offset', 0))
            assert offset >= 0
        except (ValueError, AssertionError):
            raise self.BadRequestError("offset must be a positive integer")

        try:
            limit = int(request.GET.get('limit', 20))
            assert limit >= 0
        except (ValueError, AssertionError):
            raise self.BadRequestError("limit must be a positive integer")

        start = offset
        stop = offset + limit
        results = queryset[start:stop]

        # Get list of fields to show in results
        if 'fields' in request.GET:
            fields = request.GET['fields'].split(',')
        else:
            fields = ('title', )

        return self.json_response(
            OrderedDict([
                ('meta', OrderedDict([
                    ('total_count', queryset.count()),
                ])),
                ('pages', [
                    self.serialize_page(result, fields=fields)
                    for result in results
                ]),
            ])
        )

    def detail_view(self, request, pk):
        page = get_object_or_404(self.get_queryset(request), pk=pk).specific
        data = self.serialize_page(page, all_fields=True, parent_id=True)

        return self.json_response(data)


class ImagesAPIEndpoint(BaseAPIEndpoint):
    model = get_image_model()

    def get_queryset(self, request):
        return self.model.objects.all()

    def serialize_image(self, image, fields=('title', ), all_fields=False):
        # Build data document
        data = [
            ('id', image.id),
        ]

        allowed_fields = ['title', 'width', 'height']
        if hasattr(image, 'api_fields'):
            allowed_fields.extend(image.api_fields)

        if all_fields:
            # Show all possible fields
            fields = allowed_fields
        else:
            # Remove any fields that are not defined in allowed_fields
            fields = [field for field in fields if field in allowed_fields]

        data.extend(get_api_data(image, fields))

        return OrderedDict(data)

    def listing_view(self, request):
        queryset = self.get_queryset(request)

        # Find filterset class
        if hasattr(queryset.model, 'api_filterset_class'):
            filterset_class = queryset.model.filterset_class
        else:
            filterset_class = filterset_factory(queryset.model)

        # Run field filters
        queryset = filterset_class(request.GET, queryset=queryset).qs

        # Ordering
        if 'order' in request.GET:
            order_by = request.GET['order']

            if order_by in ('id', 'title'):
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
            s = get_search_backend()
            queryset = s.search(search_query, queryset)

        # Pagination
        try:
            offset = int(request.GET.get('offset', 0))
            assert offset >= 0
        except (ValueError, AssertionError):
            raise self.BadRequestError("offset must be a positive integer")

        try:
            limit = int(request.GET.get('limit', 20))
            assert limit >= 0
        except (ValueError, AssertionError):
            raise self.BadRequestError("limit must be a positive integer")

        start = offset
        stop = offset + limit
        results = queryset[start:stop]

        # Get list of fields to show in results
        if 'fields' in request.GET:
            fields = request.GET['fields'].split(',')
        else:
            fields = ('title', )

        return self.json_response(
            OrderedDict([
                ('meta', OrderedDict([
                    ('total_count', queryset.count()),
                ])),
                ('images', [
                    self.serialize_image(result, fields=fields)
                    for result in results
                ]),
            ])
        )

    def detail_view(self, request, pk):
        image = get_object_or_404(self.get_queryset(request), pk=pk)
        data = self.serialize_image(image, all_fields=True)

        return self.json_response(data)


class DocumentsAPIEndpoint(BaseAPIEndpoint):
    def serialize_document(self, document):
        return OrderedDict([
            ('id', document.id),
            ('title', document.title),
            ('download_url', document.url),
        ])

    def listing_view(self, request):
        queryset = Document.objects.all()

        # Run field filters
        filterset_class = filterset_factory(queryset.model)
        queryset = filterset_class(request.GET, queryset=queryset).qs

        # Ordering
        if 'order' in request.GET:
            order_by = request.GET['order']

            if order_by in ('id', 'title'):
                queryset = queryset.order_by(order_by)

        # Search
        if 'search' in request.GET:
            search_query = request.GET['search']
            s = get_search_backend()
            queryset = s.search(search_query, queryset)

        # Pagination
        try:
            offset = int(request.GET.get('offset', 0))
            assert offset >= 0
        except (ValueError, AssertionError):
            raise self.BadRequestError("offset must be a positive integer")

        try:
            limit = int(request.GET.get('limit', 20))
            assert limit >= 0
        except (ValueError, AssertionError):
            raise self.BadRequestError("limit must be a positive integer")

        start = offset
        stop = offset + limit
        results = queryset[start:stop]

        return self.json_response(
            OrderedDict([
                ('meta', OrderedDict([
                    ('total_count', queryset.count()),
                ])),
                ('documents', [
                    self.serialize_document(result)
                    for result in results
                ]),
            ])
        )

    def detail_view(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        data = self.serialize_document(document)

        return self.json_response(data)
