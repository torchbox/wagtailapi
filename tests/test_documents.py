import json
import unittest

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from wagtail.wagtaildocs.models import Document

from . import models


class TestDocumentListing(TestCase):
    fixtures = ['wagtailapi_tests.json']

    def get_response(self, **params):
        return self.client.get(reverse('wagtailapi_v1_documents:listing'), params)

    def get_document_id_list(self, content):
        return [page['id'] for page in content['documents']]


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

    def test_documents_section_is_present(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertIn('documents', content)
        self.assertIsInstance(content['documents'], list)

    def test_total_count(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(content['meta']['total_count'], Document.objects.count())


    # FILTERING

    def test_filtering_exact_filter(self):
        response = self.get_response(title='James Joyce')
        content = json.loads(response.content.decode('UTF-8'))

        document_id_list = self.get_document_id_list(content)
        self.assertEqual(document_id_list, [2])

    @unittest.expectedFailure
    def test_filtering_unknown_field_gives_error(self):
        response = self.get_response(not_a_field='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)


    # ORDERING

    def test_ordering_default(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))

        document_id_list = self.get_document_id_list(content)
        self.assertEqual(document_id_list, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    def test_ordering_by_title(self):
        response = self.get_response(order='title')
        content = json.loads(response.content.decode('UTF-8'))

        document_id_list = self.get_document_id_list(content)
        self.assertEqual(document_id_list, [3, 12, 10, 2, 7, 9, 8, 4, 1, 5, 11, 6])

    def test_ordering_by_title_backwards(self):
        response = self.get_response(order='-title')
        content = json.loads(response.content.decode('UTF-8'))

        document_id_list = self.get_document_id_list(content)
        self.assertEqual(document_id_list, [6, 11, 5, 1, 4, 8, 9, 7, 2, 10, 12, 3])

    def test_ordering_by_unknown_field_gives_error(self):
        response = self.get_response(order='not_a_field')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "cannot order by 'not_a_field' (unknown field)"})


    # LIMIT

    def test_limit_only_two_results_returned(self):
        response = self.get_response(limit=2)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(len(content['documents']), 2)

    def test_limit_total_count(self):
        response = self.get_response(limit=2)
        content = json.loads(response.content.decode('UTF-8'))

        # The total count must not be affected by "limit"
        self.assertEqual(content['meta']['total_count'], Document.objects.count())

    def test_limit_not_integer_gives_error(self):
        response = self.get_response(limit='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "limit must be a positive integer"})


    # OFFSET

    def test_offset_5_usually_appears_5th_in_list(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        document_id_list = self.get_document_id_list(content)
        self.assertEqual(document_id_list.index(5), 4)

    def test_offset_5_moves_after_offset(self):
        response = self.get_response(offset=4)
        content = json.loads(response.content.decode('UTF-8'))
        document_id_list = self.get_document_id_list(content)
        self.assertEqual(document_id_list.index(5), 0)

    def test_offset_total_count(self):
        response = self.get_response(offset=10)
        content = json.loads(response.content.decode('UTF-8'))

        # The total count must not be affected by "offset"
        self.assertEqual(content['meta']['total_count'], Document.objects.count())

    def test_offset_not_integer_gives_error(self):
        response = self.get_response(offset='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "offset must be a positive integer"})


    # SEARCH

    def test_search_for_james_joyce(self):
        response = self.get_response(search='james')
        content = json.loads(response.content.decode('UTF-8'))

        document_id_list = self.get_document_id_list(content)

        self.assertEqual(set(document_id_list), set([2]))


class TestDocumentDetail(TestCase):
    fixtures = ['wagtailapi_tests.json']

    def get_response(self, image_id, **params):
        return self.client.get(reverse('wagtailapi_v1_documents:detail', args=(image_id, )), params)

    def test_status_code(self):
        response = self.get_response(1)
        self.assertEqual(response.status_code, 200)

    def test_content_type_header(self):
        response = self.get_response(1)
        self.assertEqual(response['Content-type'], 'application/json')

    def test_valid_json(self):
        response = self.get_response(1)

        # Will crash if there's a problem
        json.loads(response.content.decode('UTF-8'))

    def test_id(self):
        response = self.get_response(1)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('id', content)
        self.assertEqual(content['id'], 1)

    def test_no_meta(self):
        response = self.get_response(5)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertNotIn('meta', content)

    def test_title(self):
        response = self.get_response(1)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('title', content)
        self.assertEqual(content['title'], "Wagtail by Mark Harkin")

    @unittest.expectedFailure
    @override_settings(WAGTAILAPI_BASE_URL='http://api.example.com/')
    def test_download_url(self):
        response = self.get_response(1)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('download_url', content)
        self.assertEqual(content['title'], 'http://api.example.com/documents/1/wagtail_by_markyharky.jpg')
