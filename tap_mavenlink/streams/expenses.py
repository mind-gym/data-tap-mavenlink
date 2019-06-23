from tap_mavenlink.streams.base import BaseStream
import singer

LOGGER = singer.get_logger()  # noqa


class ExpensesStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'expenses'
    KEY_PROPERTIES = ['id']

    @property
    def path(self):
        return '/expenses.json'

    @property
    def response_key(self):
        return 'expenses'
