import json
import unittest

from django.test import TestCase
from django.core.urlresolvers import reverse

from wagtail.wagtailimages.models import get_image_model

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

    @unittest.expectedFailure
    def test_extra_fields_which_are_not_in_api_fields_gives_error(self):
        response = self.get_response(fields='uploaded_by_user')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)

    @unittest.expectedFailure
    def test_extra_fields_unknown_field_gives_error(self):
        response = self.get_response(fields='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)


    # FILTERING

    def test_filtering_exact_filter(self):
        response = self.get_response(title='James Joyce')
        content = json.loads(response.content.decode('UTF-8'))

        image_id_list = self.get_image_id_list(content)
        self.assertEqual(image_id_list, [5])

    @unittest.expectedFailure
    def test_filtering_unknown_field_gives_error(self):
        response = self.get_response(not_a_field='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)


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

    @unittest.expectedFailure
    def test_ordering_by_title_backwards(self):
        response = self.get_response(order='-title')
        content = json.loads(response.content.decode('UTF-8'))

        image_id_list = self.get_image_id_list(content)
        self.assertEqual(image_id_list, [9, 14, 8, 4, 7, 11, 12, 10, 5, 13, 15, 6])

    @unittest.expectedFailure
    def test_ordering_by_unknown_field_gives_error(self):
        response = self.get_response(order='not_a_field')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)


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
