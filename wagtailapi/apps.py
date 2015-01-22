from django.apps import AppConfig, apps


class WagtailAPIAppConfig(AppConfig):
    name = 'wagtailapi'
    label = 'wagtailapi'
    verbose_name = "Wagtail API"

    def ready(self):
        # Install cache purging signal handlers if frontendcache is installed
        if apps.is_installed('wagtail.contrib.wagtailfrontendcache'):
            from wagtailapi.signal_handlers import register_signal_handlers

            register_signal_handlers()
