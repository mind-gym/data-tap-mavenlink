from tap_mavenlink.streams.base import BaseStream
import singer

LOGGER = singer.get_logger()  # noqa


class WorkspaceGroupCustomFieldValuesStream(BaseStream):
    NAME = 'WorkspaceGroupCustomFieldValuesStream'
    API_METHOD = 'GET'
    TABLE = 'workspace_group_custom_field_values'
    KEY_PROPERTIES = ['id']

    def extra_params(self):
        return {
            "subject_type": "WorkspaceGroup"
        }

    @property
    def path(self):
        return '/custom_field_values.json'

    @property
    def response_key(self):
        return 'custom_field_values'
