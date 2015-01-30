import json
import unittest
import mock

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.conf import settings

from wagtail.wagtailimages.models import get_image_model

from wagtailapi import signal_handlers

from . import models


class TestImageListing(TestCase):
    fixtures = ['wagtailapi_tests.json']

    def get_response(self, **params):
        return self.client.get(reverse('wagtailapi_v1_images:listing'), params)

    def get_image_id_list(self, content):
        return [page['id'] for page in content['images']]


    # BASIC TESTS

    def test_status_code(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_content_type_header(self):
        response = self.get_response()
        self.assertEqual(response['Content-type'], 'application/json')

    def test_valid_json(self):
        response = self.get_response()

        # Will crash if there's a problem
        json.loads(response.content.decode('UTF-8'))

    def test_meta_section_is_present(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertIn('meta', content)
        self.assertIsInstance(content['meta'], dict)

    def test_total_count_is_present(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertIn('total_count', content['meta'])
        self.assertIsInstance(content['meta']['total_count'], int)

    def test_images_section_is_present(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertIn('images', content)
        self.assertIsInstance(content['images'], list)

    def test_total_count(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(content['meta']['total_count'], get_image_model().objects.count())


    # EXTRA FIELDS

    def test_extra_fields_default(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))

        for image in content['images']:
            self.assertEqual(image.keys(), set(['id', 'title']))

    def test_extra_fields(self):
        response = self.get_response(fields='title,width,height')
        content = json.loads(response.content.decode('UTF-8'))

        for image in content['images']:
            self.assertEqual(image.keys(), set(['id', 'title', 'width', 'height']))

    def test_extra_fields_which_are_not_in_api_fields_gives_error(self):
        response = self.get_response(fields='uploaded_by_user')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "unknown fields: uploaded_by_user"})

    def test_extra_fields_unknown_field_gives_error(self):
        response = self.get_response(fields='123,title,abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "unknown fields: 123, abc"})


    # FILTERING

    def test_filtering_exact_filter(self):
        response = self.get_response(title='James Joyce')
        content = json.loads(response.content.decode('UTF-8'))

        image_id_list = self.get_image_id_list(content)
        self.assertEqual(image_id_list, [5])

    def test_filtering_unknown_field_gives_error(self):
        response = self.get_response(not_a_field='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "query parameter is not an operation or a recognised field: not_a_field"})


    # ORDERING

    def test_ordering_default(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))

        image_id_list = self.get_image_id_list(content)
        self.assertEqual(image_id_list, [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    def test_ordering_by_title(self):
        response = self.get_response(order='title')
        content = json.loads(response.content.decode('UTF-8'))

        image_id_list = self.get_image_id_list(content)
        self.assertEqual(image_id_list, [6, 15, 13, 5, 10, 12, 11, 7, 4, 8, 14, 9])

    def test_ordering_by_title_backwards(self):
        response = self.get_response(order='-title')
        content = json.loads(response.content.decode('UTF-8'))

        image_id_list = self.get_image_id_list(content)
        self.assertEqual(image_id_list, [9, 14, 8, 4, 7, 11, 12, 10, 5, 13, 15, 6])

    def test_ordering_by_random(self):
        response_1 = self.get_response(order='random')
        content_1 = json.loads(response_1.content.decode('UTF-8'))
        image_id_list_1 = self.get_image_id_list(content_1)

        response_2 = self.get_response(order='random')
        content_2 = json.loads(response_2.content.decode('UTF-8'))
        image_id_list_2 = self.get_image_id_list(content_2)

        self.assertNotEqual(image_id_list_1, image_id_list_2)

    def test_ordering_by_random_backwards_gives_error(self):
        response = self.get_response(order='-random')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "cannot order by 'random' (unknown field)"})

    def test_ordering_by_random_with_offset_gives_error(self):
        response = self.get_response(order='random', offset=10)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "random ordering with offset is not supported"})

    def test_ordering_by_unknown_field_gives_error(self):
        response = self.get_response(order='not_a_field')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "cannot order by 'not_a_field' (unknown field)"})


    # LIMIT

    def test_limit_only_two_results_returned(self):
        response = self.get_response(limit=2)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(len(content['images']), 2)

    def test_limit_total_count(self):
        response = self.get_response(limit=2)
        content = json.loads(response.content.decode('UTF-8'))

        # The total count must not be affected by "limit"
        self.assertEqual(content['meta']['total_count'], get_image_model().objects.count())

    def test_limit_not_integer_gives_error(self):
        response = self.get_response(limit='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "limit must be a positive integer"})

    def test_limit_too_high_gives_error(self):
        response = self.get_response(limit=1000)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "limit cannot be higher than 20"})

    @override_settings(WAGTAILAPI_LIMIT_MAX=10)
    def test_limit_maximum_can_be_changed(self):
        response = self.get_response(limit=20)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "limit cannot be higher than 10"})

    @override_settings(WAGTAILAPI_LIMIT_MAX=2)
    def test_limit_default_changes_with_max(self):
        # The default limit is 20. If WAGTAILAPI_LIMIT_MAX is less than that,
        # the default should change accordingly.
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(len(content['images']), 2)


    # OFFSET

    def test_offset_10_usually_appears_7th_in_list(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        image_id_list = self.get_image_id_list(content)
        self.assertEqual(image_id_list.index(10), 6)

    def test_offset_10_moves_after_offset(self):
        response = self.get_response(offset=4)
        content = json.loads(response.content.decode('UTF-8'))
        image_id_list = self.get_image_id_list(content)
        self.assertEqual(image_id_list.index(10), 2)

    def test_offset_total_count(self):
        response = self.get_response(offset=10)
        content = json.loads(response.content.decode('UTF-8'))

        # The total count must not be affected by "offset"
        self.assertEqual(content['meta']['total_count'], get_image_model().objects.count())

    def test_offset_not_integer_gives_error(self):
        response = self.get_response(offset='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "offset must be a positive integer"})


    # SEARCH

    def test_search_for_james_joyce(self):
        response = self.get_response(search='james')
        content = json.loads(response.content.decode('UTF-8'))

        image_id_list = self.get_image_id_list(content)

        self.assertEqual(set(image_id_list), set([5]))

    def test_search_when_ordering_gives_error(self):
        response = self.get_response(search='james', order='title')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "ordering with a search query is not supported"})

    @override_settings(WAGTAILAPI_SEARCH_ENABLED=False)
    def test_search_when_disabled_gives_error(self):
        response = self.get_response(search='james')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "search is disabled"})


class TestImageDetail(TestCase):
    fixtures = ['wagtailapi_tests.json']

    def get_response(self, image_id, **params):
        return self.client.get(reverse('wagtailapi_v1_images:detail', args=(image_id, )), params)

    def test_status_code(self):
        response = self.get_response(5)
        self.assertEqual(response.status_code, 200)

    def test_content_type_header(self):
        response = self.get_response(5)
        self.assertEqual(response['Content-type'], 'application/json')

    def test_valid_json(self):
        response = self.get_response(5)

        # Will crash if there's a problem
        json.loads(response.content.decode('UTF-8'))

    def test_id(self):
        response = self.get_response(5)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('id', content)
        self.assertEqual(content['id'], 5)

    def test_no_meta(self):
        response = self.get_response(5)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertNotIn('meta', content)

    def test_title(self):
        response = self.get_response(5)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('title', content)
        self.assertEqual(content['title'], "James Joyce")

    def test_width_and_height(self):
        response = self.get_response(5)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('width', content)
        self.assertEqual(content['width'], 500)
        self.assertEqual(content['height'], 392)


@override_settings(
    INSTALLED_APPS=settings.INSTALLED_APPS + (
        'wagtail.contrib.wagtailfrontendcache',
    ),
    WAGTAILFRONTENDCACHE={
        'varnish': {
            'BACKEND': 'wagtail.contrib.wagtailfrontendcache.backends.HTTPBackend',
            'LOCATION': 'http://localhost:8000',
        },
    },
    WAGTAILAPI_BASE_URL='http://api.example.com',
)
@mock.patch('wagtail.contrib.wagtailfrontendcache.backends.HTTPBackend.purge')
class TestImageCacheInvalidation(TestCase):
    fixtures = ['wagtailapi_tests.json']

    @classmethod
    def setUpClass(cls):
        signal_handlers.register_signal_handlers()

    @classmethod
    def tearDownClass(cls):
        signal_handlers.unregister_signal_handlers()

    def test_resave_image_purges(self, purge):
        get_image_model().objects.get(id=5).save()

        purge.assert_any_call('http://api.example.com/api/v1/images/5/')

    def test_delete_image_purges(self, purge):
        get_image_model().objects.get(id=5).delete()

        purge.assert_any_call('http://api.example.com/api/v1/images/5/')
