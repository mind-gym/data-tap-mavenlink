from tap_mavenlink.streams.base import BaseStream
import singer

LOGGER = singer.get_logger()  # noqa


class CustomFieldSetsStream(BaseStream):
    NAME = 'CustomFieldSetsStream'
    API_METHOD = 'GET'
    TABLE = 'custom_field_sets'
    KEY_PROPERTIES = ['id']

    @property
    def path(self):
        return '/custom_field_sets.json'

    @property
    def response_key(self):
        return 'custom_field_sets'
