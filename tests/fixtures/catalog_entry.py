import json
import pytest
from singer import Schema
from singer.catalog import CatalogEntry

from tests import constants


@pytest.fixture()
def catalog_entry():
    def _catalog_entry(stream_name, replication_method, replication_key):
        """
        Create parameterised catalog entries
        """

        metadata = {"inclusion": "automatic"}

        if replication_method:
            metadata.update({"replication-method": replication_method})

        if replication_key:
            metadata.update({"replication-key": replication_key})

        entry = CatalogEntry(
                    stream=stream_name,
                    tap_stream_id=stream_name,
                    key_properties='id',
                    schema=Schema(
                        selected=True,
                        properties={
                            'id': Schema(type='string'),
                            'updated_at': Schema(type='string', format="date-time")}),
                    metadata=[
                        {
                            "metadata": metadata,
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
                )

        return entry

    return _catalog_entry
