class WagtailAPIRestFrameworkMixin(object):
    serializer_class = None

    def get_api_detail_data(self):
        return self.serializer_class().to_representation(self)
