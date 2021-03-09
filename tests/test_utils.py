import json
from unittest.mock import patch

import pytest
from singer import Catalog

from tap_mavenlink import main
from tests import constants


class TestUtils:

    @pytest.mark.parametrize("field, last_record", [('created_at', '2002-01-01T00:00:00Z'),  # Bad field value
                                                    ('updated_at', '2foo-01-01T00:00:00Z')]) # Bad last_record value
    def test_arg_validation_state_file_contains_invalid_bookmarks(self, tmp_path, config, catalog, field, last_record):
        # Given - We configure
        # Tap inputs
        # catalog.json and config.json come from fixtures
        # state.json refers to a bookmark we don't cater for:
        path = tmp_path / constants.STATE_FILENAME
        path.write_text(json.dumps(
            {
                "bookmarks": {
                    "foo_stream": {
                        "field": field,
                        "last_record": last_record
                    }
                }
            }
        ))

        # Then
        with pytest.raises(ValueError):
            # When
            # We run the component
            sys_args = [
                'tap-mavenlink',
                '--config', str(tmp_path / constants.CONFIG_FILENAME),
                '--catalog', str(tmp_path / constants.CATALOG_FILENAME),
                '--state', str(tmp_path / constants.STATE_FILENAME)
            ]
            with patch('sys.argv', sys_args):
                main()


    @pytest.mark.parametrize("rep_method, rep_key", [
        (None, None),                   # No replication information; so assume FULL_TABLE
        ('FULL_TABLE', None),           # Explicitly FULL_TABLE
        ('INCREMENTAL', 'updated_at'),  # replication-key is a single value
    ])
    def test_arg_validation_replication_metadata_happy_path(self, tmp_path, config, rep_method, rep_key, catalog_entry):
        # Given - We configure
        # Tap inputs
        # config.json comes from a fixture
        # catalog.json is defined here:
        path = tmp_path / constants.CATALOG_FILENAME
        path.write_text(json.dumps(
            Catalog(streams=[
                catalog_entry(stream_name='fake_stream', replication_method=rep_method, replication_key=rep_key)
            ]).to_dict()
        ))

        # When
        # We run the component
        sys_args = [
            'tap-mavenlink',
            '--config', str(tmp_path / constants.CONFIG_FILENAME),
            '--catalog', str(tmp_path / constants.CATALOG_FILENAME)
        ]
        with patch('sys.argv', sys_args):
            main()

        # Then
        # No error is raised


    @pytest.mark.parametrize("rep_method, rep_key", [
        ('INCREMENTAL', None),          # Missing key
        (None, 'updated_at'),           # Missing method
        ('FULL_TABLE', 'updated_at'),   # Unexpected key
        ('FOO_METHOD', None),           # Unknown method
        ('INCREMENTAL', ['updated_at']) # replication-key is a list
    ])
    def test_arg_validation_replication_metadata_is_consistent(
            self, tmp_path, config, rep_method, rep_key, catalog_entry
    ):
        # Given - We configure
        # Tap inputs
        # config.json comes from a fixture
        # catalog.json is defined here:
        path = tmp_path / constants.CATALOG_FILENAME
        path.write_text(json.dumps(
            Catalog(streams=[
                catalog_entry(stream_name='fake_stream', replication_method=rep_method, replication_key=rep_key)
            ]).to_dict()
        ))

        # Then
        with pytest.raises(ValueError):
            # When
            # We run the component
            sys_args = [
                'tap-mavenlink',
                '--config', str(tmp_path / constants.CONFIG_FILENAME),
                '--catalog', str(tmp_path / constants.CATALOG_FILENAME)
            ]
            with patch('sys.argv', sys_args):
                main()
