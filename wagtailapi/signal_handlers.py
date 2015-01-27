from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, post_delete
from django.conf import settings

from wagtail.wagtailcore.signals import page_published, page_unpublished
from wagtail.wagtailcore.models import PAGE_MODEL_CLASSES
from wagtail.wagtailimages.models import get_image_model
from wagtail.wagtaildocs.models import Document

from wagtail.contrib.wagtailfrontendcache.utils import purge_url_from_cache


def purge_page_from_cache(instance, **kwargs):
    for host in settings.ALLOWED_HOSTS:
        purge_url_from_cache('http://' + host + reverse('wagtailapi_v1_pages:detail', args=(instance.id, )))


def purge_image_from_cache(instance, **kwargs):
    for host in settings.ALLOWED_HOSTS:
        purge_url_from_cache('http://' + host + reverse('wagtailapi_v1_images:detail', args=(instance.id, )))


def purge_document_from_cache(instance, **kwargs):
    for host in settings.ALLOWED_HOSTS:
        purge_url_from_cache('http://' + host + reverse('wagtailapi_v1_documents:detail', args=(instance.id, )))


def register_signal_handlers():
    Image = get_image_model()

    for model in PAGE_MODEL_CLASSES:
        page_published.connect(purge_page_from_cache, sender=model)
        page_unpublished.connect(purge_page_from_cache, sender=model)

    post_save.connect(purge_image_from_cache, sender=Image)
    post_delete.connect(purge_image_from_cache, sender=Image)
    post_save.connect(purge_document_from_cache, sender=Document)
    post_delete.connect(purge_document_from_cache, sender=Document)
