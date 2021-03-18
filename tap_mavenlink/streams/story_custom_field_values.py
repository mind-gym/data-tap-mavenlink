from tap_mavenlink.streams.base import BaseStream
import singer

LOGGER = singer.get_logger()  # noqa


class StoryCustomFieldValuesStream(BaseStream):
    NAME = 'StoryCustomFieldValuesStream'
    API_METHOD = 'GET'
    TABLE = 'story_custom_field_values'
    KEY_PROPERTIES = ['id']

    def extra_params(self):
        return {
            "subject_type": "Story"
        }

    @property
    def path(self):
        return '/custom_field_values.json'

    @property
    def response_key(self):
        return 'custom_field_values'
