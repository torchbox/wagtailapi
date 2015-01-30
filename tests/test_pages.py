import json
import unittest
import mock

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.conf import settings

from wagtail.wagtailcore.models import Page

from wagtailapi import signal_handlers

from . import models


def get_total_page_count():
    # Need to take away 1 as the root page is invisible over the API
    return Page.objects.live().public().count() - 1


class TestPageListing(TestCase):
    fixtures = ['wagtailapi_tests.json']

    def get_response(self, **params):
        return self.client.get(reverse('wagtailapi_v1_pages:listing'), params)

    def get_page_id_list(self, content):
        return [page['id'] for page in content['pages']]


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

    def test_pages_section_is_present(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertIn('pages', content)
        self.assertIsInstance(content['pages'], list)

    def test_total_count(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(content['meta']['total_count'], get_total_page_count())

    def test_unpublished_pages_dont_appear_in_list(self):
        total_count = get_total_page_count()

        page = models.BlogEntryPage.objects.get(id=16)
        page.unpublish()

        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(content['meta']['total_count'], total_count - 1)

    def test_private_pages_dont_appear_in_list(self):
        total_count = get_total_page_count()

        page = models.BlogIndexPage.objects.get(id=5)
        page.view_restrictions.create(password='test')

        new_total_count = get_total_page_count()
        self.assertNotEqual(total_count, new_total_count)

        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        self.assertEqual(content['meta']['total_count'], new_total_count)


    # TYPE FILTER

    def test_type_filter_results_are_all_blog_entries(self):
        response = self.get_response(type='tests.BlogEntryPage')
        content = json.loads(response.content.decode('UTF-8'))

        for page in content['pages']:
            self.assertEqual(page['meta']['type'], 'tests.BlogEntryPage')

    def test_type_filter_total_count(self):
        response = self.get_response(type='tests.BlogEntryPage')
        content = json.loads(response.content.decode('UTF-8'))

        # Total count must be reduced as this filters the results
        self.assertEqual(content['meta']['total_count'], 3)

    def test_non_existant_type_gives_error(self):
        response = self.get_response(type='tests.IDontExist')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(content, {'message': "Type doesn't exist"})


    # EXTRA FIELDS

    def test_extra_fields_default(self):
        response = self.get_response(type='tests.BlogEntryPage')
        content = json.loads(response.content.decode('UTF-8'))

        for page in content['pages']:
            self.assertEqual(page.keys(), set(['id', 'meta', 'title']))

    def test_extra_fields(self):
        response = self.get_response(type='tests.BlogEntryPage', fields='title,date,feed_image')
        content = json.loads(response.content.decode('UTF-8'))

        for page in content['pages']:
            self.assertEqual(page.keys(), set(['id', 'meta', 'title', 'date', 'feed_image']))

    def test_extra_fields_child_relation(self):
        response = self.get_response(type='tests.BlogEntryPage', fields='title,related_links')
        content = json.loads(response.content.decode('UTF-8'))

        for page in content['pages']:
            self.assertEqual(page.keys(), set(['id', 'meta', 'title', 'related_links']))
            self.assertIsInstance(page['related_links'], list)

    def test_extra_fields_without_type_gives_error(self):
        response = self.get_response(fields='title,related_links')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "unknown fields: related_links"})

    def test_extra_fields_which_are_not_in_api_fields_gives_error(self):
        response = self.get_response(fields='path')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "unknown fields: path"})

    def test_extra_fields_unknown_field_gives_error(self):
        response = self.get_response(fields='123,title,abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "unknown fields: 123, abc"})


    # FILTERING

    def test_filtering_exact_filter(self):
        response = self.get_response(title='Home page')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [2])

    def test_filtering_exact_filter_on_specific_field(self):
        response = self.get_response(type='tests.BlogEntryPage', date='2013-12-02')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [16])

    def test_filtering_doesnt_work_on_specific_fields_without_type(self):
        response = self.get_response(date='2013-12-02')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "query parameter is not an operation or a recognised field: date"})

    def test_filtering_unknown_field_gives_error(self):
        response = self.get_response(not_a_field='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "query parameter is not an operation or a recognised field: not_a_field"})


    # CHILD OF FILTER

    def test_child_of_filter(self):
        response = self.get_response(child_of=5)
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [16, 18, 19])

    def test_child_of_with_type(self):
        response = self.get_response(type='tests.EventPage', child_of=5)
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [])

    def test_child_of_unknown_page_gives_error(self):
        response = self.get_response(child_of=1000)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(content, {'message': "Parent page doesn't exist"})


    # ORDERING

    def test_ordering_default(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [2, 4, 8, 9, 5, 16, 18, 19, 6, 10, 15, 17, 21, 22, 23, 20, 13, 14, 12])

    def test_ordering_by_title(self):
        response = self.get_response(order='title')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [21, 22, 19, 23, 5, 16, 18, 12, 14, 8, 9, 4, 2, 13, 20, 17, 6, 10, 15])

    def test_ordering_by_title_backwards(self):
        response = self.get_response(order='-title')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [15, 10, 6, 17, 20, 13, 2, 4, 9, 8, 14, 12, 18, 16, 5, 23, 19, 22, 21])

    def test_ordering_by_random(self):
        response_1 = self.get_response(order='random')
        content_1 = json.loads(response_1.content.decode('UTF-8'))
        page_id_list_1 = self.get_page_id_list(content_1)

        response_2 = self.get_response(order='random')
        content_2 = json.loads(response_2.content.decode('UTF-8'))
        page_id_list_2 = self.get_page_id_list(content_2)

        self.assertNotEqual(page_id_list_1, page_id_list_2)

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

    def test_ordering_default_with_type(self):
        response = self.get_response(type='tests.BlogEntryPage')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [16, 18, 19])

    def test_ordering_by_title_with_type(self):
        response = self.get_response(type='tests.BlogEntryPage', order='title')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [19, 16, 18])

    def test_ordering_by_specific_field_with_type(self):
        response = self.get_response(type='tests.BlogEntryPage', order='date')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list, [16, 18, 19])

    def test_ordering_by_unknown_field_gives_error(self):
        response = self.get_response(order='not_a_field')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "cannot order by 'not_a_field' (unknown field)"})


    # LIMIT

    def test_limit_only_two_results_returned(self):
        response = self.get_response(limit=2)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(len(content['pages']), 2)

    def test_limit_total_count(self):
        response = self.get_response(limit=2)
        content = json.loads(response.content.decode('UTF-8'))

        # The total count must not be affected by "limit"
        self.assertEqual(content['meta']['total_count'], get_total_page_count())

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

        self.assertEqual(len(content['pages']), 2)


    # OFFSET

    def test_offset_5_usually_appears_5th_in_list(self):
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))
        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list.index(5), 4)

    def test_offset_5_moves_after_offset(self):
        response = self.get_response(offset=4)
        content = json.loads(response.content.decode('UTF-8'))
        page_id_list = self.get_page_id_list(content)
        self.assertEqual(page_id_list.index(5), 0)

    def test_offset_total_count(self):
        response = self.get_response(offset=10)
        content = json.loads(response.content.decode('UTF-8'))

        # The total count must not be affected by "offset"
        self.assertEqual(content['meta']['total_count'], get_total_page_count())

    def test_offset_not_integer_gives_error(self):
        response = self.get_response(offset='abc')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "offset must be a positive integer"})


    # SEARCH

    def test_search_for_blog(self):
        response = self.get_response(search='blog')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)

        # Check that the results are the blog index and three blog pages
        self.assertEqual(set(page_id_list), set([5, 16, 18, 19]))

    def test_search_with_type(self):
        response = self.get_response(type='tests.BlogEntryPage', search='blog')
        content = json.loads(response.content.decode('UTF-8'))

        page_id_list = self.get_page_id_list(content)

        self.assertEqual(set(page_id_list), set([16, 18, 19]))

    def test_search_when_ordering_gives_error(self):
        response = self.get_response(search='blog', order='title')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "ordering with a search query is not supported"})

    @override_settings(WAGTAILAPI_SEARCH_ENABLED=False)
    def test_search_when_disabled_gives_error(self):
        response = self.get_response(search='blog')
        content = json.loads(response.content.decode('UTF-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content, {'message': "search is disabled"})


class TestPageDetail(TestCase):
    fixtures = ['wagtailapi_tests.json']

    def get_response(self, page_id, **params):
        return self.client.get(reverse('wagtailapi_v1_pages:detail', args=(page_id, )), params)

    def test_status_code(self):
        response = self.get_response(16)
        self.assertEqual(response.status_code, 200)

    def test_content_type_header(self):
        response = self.get_response(16)
        self.assertEqual(response['Content-type'], 'application/json')

    def test_valid_json(self):
        response = self.get_response(16)

        # Will crash if there's a problem
        json.loads(response.content.decode('UTF-8'))

    def test_meta(self):
        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('meta', content)
        self.assertIsInstance(content['meta'], dict)

    def test_meta_type(self):
        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('type', content['meta'])
        self.assertEquals(content['meta']['type'], 'tests.BlogEntryPage')

    def test_meta_parent_id(self):
        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('parent_id', content['meta'])
        self.assertEquals(content['meta']['parent_id'], 5)

    def test_custom_fields(self):
        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('date', content)
        self.assertEquals(content['date'], '2013-12-02')

        self.assertIn('body', content)

    def test_child_relations(self):
        response = self.get_response(16)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('related_links', content)
        self.assertEquals(content['related_links'], [])

        self.assertIn('carousel_items', content)

        for carousel_item in content['carousel_items']:
            self.assertEquals(carousel_item.keys(), {'embed_url', 'link', 'caption', 'image'})


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
class TestPageCacheInvalidation(TestCase):
    fixtures = ['wagtailapi_tests.json']

    @classmethod
    def setUpClass(cls):
        signal_handlers.register_signal_handlers()

    @classmethod
    def tearDownClass(cls):
        signal_handlers.unregister_signal_handlers()

    def test_republish_page_purges(self, purge):
        Page.objects.get(id=2).save_revision().publish()

        purge.assert_any_call('http://api.example.com/api/v1/pages/2/')

    def test_unpublish_page_purges(self, purge):
        Page.objects.get(id=2).unpublish()

        purge.assert_any_call('http://api.example.com/api/v1/pages/2/')

    def test_delete_page_purges(self, purge):
        Page.objects.get(id=16).delete()

        purge.assert_any_call('http://api.example.com/api/v1/pages/16/')

    def test_save_draft_doesnt_purge(self, purge):
        Page.objects.get(id=2).save_revision()

        purge.assert_not_called()
