"""Test constants"""
from singer import Catalog, Schema
from singer.catalog import CatalogEntry

CATALOG_FILENAME = 'catalog.json'
CONFIG_FILENAME = 'config.json'
STATE_FILENAME = 'state.json'

CONFIG = {
    "token": "dummy_token",
    "user_agent": "tap-mavenlink mr_foo@bar.com>"
}

CATALOG = Catalog(streams=[
    CatalogEntry(
        stream='fake_incremental_stream',
        tap_stream_id='fake_incremental_stream',
        key_properties='id',
        schema=Schema(
            selected=True,
            properties={
                'id': Schema(type='string'),
                'updated_at': Schema(type='string', format="date-time")}),
        metadata=[
            {
                "metadata": {
                    "inclusion": "automatic",
                    "replication-method": "INCREMENTAL",
                    "replication-key": "updated_at"
                },
                "breadcrumb": []
            },
            {
                "metadata": {
                    "inclusion": "automatic"
                },
                "breadcrumb": ["properties", "id"]
            },
            {
                "metadata": {
                    "inclusion": "automatic"
                },
                "breadcrumb": ["properties", "updated_at"]
            }
        ]
    ),
    CatalogEntry(
        stream='fake_full_table_stream',
        tap_stream_id='fake_full_table_stream',
        key_properties='id',
        schema=Schema(
            selected=True,
            properties={
                'id': Schema(type='string'),
                'updated_at': Schema(type='string', format="date-time")}),
        metadata=[
            {
                "metadata": {
                    "inclusion": "automatic",
                    "replication-method": "FULL_TABLE",
                },
                "breadcrumb": []
            },
            {
                "metadata": {
                    "inclusion": "automatic"
                },
                "breadcrumb": ["properties", "id"]
            },
            {
                "metadata": {
                    "inclusion": "automatic"
                },
                "breadcrumb": ["properties", "updated_at"]
            }
        ]
    ),
    # Add more test streams to catalog here
    # ...
]).to_dict()

STATE = {
    "bookmarks": {
        'fake_incremental_stream': {
            "field": "updated_at",
            "last_record": "2000-01-01T00:00:00Z"
        }
    }
}
