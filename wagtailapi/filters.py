from django_filters.filterset import filterset_factory

from wagtail.wagtailcore.models import Page


def install_filters_mixin():
    def get_filterset_class(cls):
        return cls.filterset_class or filterset_factory(cls)

    def run_api_filters(cls, queryset, filters):
        f = cls.get_filterset_class()(filters, queryset=queryset)
        return f.qs

    Page.filterset_class = None
    Page.get_filterset_class = classmethod(get_filterset_class)
    Page.run_api_filters = classmethod(run_api_filters)
