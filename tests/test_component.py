import copy
import json
from datetime import datetime
from unittest.mock import patch, call

import pytz
import requests

import tap_mavenlink
from tap_mavenlink import main
from tap_mavenlink.streams.base import BaseStream
from tests import constants

# Must align with catalog fixture
class FakeIncrementalStream(BaseStream):
    NAME = 'FakeIncrementalStream'
    API_METHOD = 'GET'
    TABLE = 'fake_incremental_stream'
    KEY_PROPERTIES = ['id']

    def extra_params(self):
        return {}

    @property
    def path(self):
        return '/fake_incremental_stream.json'

    @property
    def response_key(self):
        return 'fake_incremental_stream'

# Must align with catalog fixture
class FakeFullTableStream(BaseStream):
    NAME = 'FakeFullTabletream'
    API_METHOD = 'GET'
    TABLE = 'fake_full_table_stream'
    KEY_PROPERTIES = ['id']

    def extra_params(self):
        return {}

    @property
    def path(self):
        return '/fake_full_table_stream.json'

    @property
    def response_key(self):
        return 'fake_full_table_stream'

# custom class to be the mock return value
# will override the requests.Response returned from requests.get
class MockIncrementalAPIResponse:
    status_code = 200
    text = 'foo'

    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {
            "count": 2,
            "results": [
                {"key": 'fake_incremental_stream', "id": "1"},
                {"key": 'fake_incremental_stream', "id": "2"}
            ],
            "fake_incremental_stream": {
                '1': {'updated_at': '2001-01-01T00:00:00Z'},
                '2': {'updated_at': '2002-01-01T00:00:00Z'}
            },
            "meta": {
                "count": 2,
                "page_count": 1,
                "page_number": 1,
                "page_size": 2
            }
        }

class MockIncrementalAPIResponseNoResults:
    status_code = 200
    text = 'foo'

    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {
            "count": 0,
            "results": [],
            "fake_incremental_stream": {},
            "meta": {
                "count": 0,
                "page_count": 0,
                "page_number": 0,
                "page_size": 20
            }
        }

class MockFullTableAPIResponse:
    status_code = 200
    text = 'bar'

    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {
            "count": 3,
            "results": [
                {"key": 'fake_full_table_stream', "id": "1"},
                {"key": 'fake_full_table_stream', "id": "2"},
                {"key": 'fake_full_table_stream', "id": "3"}
            ],
            "fake_full_table_stream": {
                '1': {'updated_at': '2010-01-01T00:00:00Z'},
                '2': {'updated_at': '2011-01-01T00:00:00Z'},
                '3': {'updated_at': '2012-01-01T00:00:00Z'},
            },
            "meta": {
                "count": 3,
                "page_count": 1,
                "page_number": 1,
                "page_size": 3
            }
        }


@patch('tap_mavenlink.client.requests')
class TestComponent:

    def test_component_incremental_stream_happy_path(
            self, mock_requests, tmp_path, config, catalog, state, capsys, monkeypatch
    ):
        # Given - We configure
        # Tap inputs
        # catalog.json, config.json, and state.json come from fixtures
        monkeypatch.setattr(tap_mavenlink, "AVAILABLE_STREAMS", [FakeIncrementalStream])

        # And the API response
        mock_requests.request.return_value = MockIncrementalAPIResponse()

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

        # Then
        # Check requests.request method gets expected parameters
        e_url = f'https://api.mavenlink.com/api/v1/fake_incremental_stream.json'
        e_api_method = 'GET'
        e_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {constants.CONFIG["token"]}'
        }
        e_params = {
            'page': 1,
            'per_page': 200,
            'updated_after': pytz.utc.localize(datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')),
            'order': 'updated_at'
        }
        e_json = None
        mock_requests.request.assert_called_once_with(
            e_api_method,
            e_url,
            headers=e_headers,
            params=e_params,
            json=e_json
        )

        # Check last state message emitted
        captured = capsys.readouterr()
        last_line = captured.out.splitlines()[-1]
        last_line = json.loads(last_line)
        assert last_line['type'] == 'STATE', "expect final message to be a STATE message"
        e_bookmark = copy.deepcopy(constants.STATE)
        e_bookmark['bookmarks']['fake_incremental_stream']['last_record'] = '2002-01-01T00:00:00Z'
        assert last_line['value'] == e_bookmark, "expect bookmark to show we've processed the most recent record"


    def test_component_missing_state_file_means_no_updated_after_api_param(
            self, mock_requests, tmp_path, config, catalog, capsys, monkeypatch
    ):
        # Given - We configure
        # Tap inputs
        # catalog.json and config.json come from fixtures (but not state.json!)
        monkeypatch.setattr(tap_mavenlink, "AVAILABLE_STREAMS", [FakeIncrementalStream])

        # And the API response
        mock_requests.request.return_value = MockIncrementalAPIResponse()

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
        # Check requests.request method gets expected parameters
        e_url = f'https://api.mavenlink.com/api/v1/fake_incremental_stream.json'
        e_api_method = 'GET'
        e_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {constants.CONFIG["token"]}'
        }
        # Note there is no 'updated_after' parameter.
        e_params = {
            'page': 1,
            'per_page': 200,
            'order': 'updated_at'
        }
        e_json = None
        mock_requests.request.assert_called_once_with(
            e_api_method,
            e_url,
            headers=e_headers,
            params=e_params,
            json=e_json
        )

        # Check last state message emitted
        captured = capsys.readouterr()
        last_line = captured.out.splitlines()[-1]
        last_line = json.loads(last_line)
        assert last_line['type'] == 'STATE', "expect final message to be a STATE message"
        e_bookmark = copy.deepcopy(constants.STATE)
        e_bookmark['bookmarks']['fake_incremental_stream']['last_record'] = '2002-01-01T00:00:00Z'
        assert last_line['value'] == e_bookmark, "expect bookmark to show we've processed the most recent record"


    def test_component_full_table_stream_happy_path(
            self, mock_requests, tmp_path, config, catalog, state, capsys, monkeypatch
    ):
        # Given - We configure
        # Tap inputs
        # catalog.json, config.json, and state.json come from fixtures
        monkeypatch.setattr(tap_mavenlink, "AVAILABLE_STREAMS", [FakeFullTableStream])

        # And the API response
        mock_requests.request.return_value = MockFullTableAPIResponse()

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

        # Then
        # Check requests.request method gets expected parameters
        e_url = f'https://api.mavenlink.com/api/v1/fake_full_table_stream.json'
        e_api_method = 'GET'
        e_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {constants.CONFIG["token"]}'
        }
        # Note there is no 'updated_after' or 'order' parameters.
        e_params = {
            'page': 1,
            'per_page': 200,
        }
        e_json = None
        mock_requests.request.assert_called_once_with(
            e_api_method,
            e_url,
            headers=e_headers,
            params=e_params,
            json=e_json
        )


    def test_component_with_two_streams_one_incremental_and_one_full_table_happy_path(
            self, mock_requests, tmp_path, config, catalog, state, capsys, monkeypatch
    ):
        # Given - We configure
        # Tap inputs
        # catalog.json, config.json, and state.json come from fixtures
        # And we process an incremental stream and then a full table stream
        monkeypatch.setattr(tap_mavenlink, "AVAILABLE_STREAMS", [
            FakeIncrementalStream,
            FakeFullTableStream
        ])

        # And the API responses, in order, will be
        mock_requests.request.side_effect = [
            MockIncrementalAPIResponse(),
            MockFullTableAPIResponse()
        ]

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

        # Then
        # Set expected common API params
        e_api_method = 'GET'
        e_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {constants.CONFIG["token"]}'
        }
        e_json = None

        # Check requests.request method gets expected parameters for the FIRST call
        e_url = f'https://api.mavenlink.com/api/v1/fake_incremental_stream.json'
        e_params = {
            'page': 1,
            'per_page': 200,
            'updated_after': pytz.utc.localize(datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')),
            'order': 'updated_at'
        }
        call1 = call(
            e_api_method,
            e_url,
            headers=e_headers,
            params=e_params,
            json=e_json
        )

        # Check requests.request method gets expected parameters for the SECOND call
        e_url = f'https://api.mavenlink.com/api/v1/fake_full_table_stream.json'
        e_params = {
            'page': 1,
            'per_page': 200,
        }
        call2 = call(
            e_api_method,
            e_url,
            headers=e_headers,
            params=e_params,
            json=e_json
        )

        mock_requests.request.assert_has_calls([call1, call2])

        captured = capsys.readouterr()
        assert captured.out.strip() == \
        """{"type": "SCHEMA", "stream": "fake_incremental_stream", "schema": {"properties": {"id": {"type": "string"}, "updated_at": {"format": "date-time", "type": "string"}}, "selected": true}, "key_properties": ["id"]}\n""" + \
        """{"type": "RECORD", "stream": "fake_incremental_stream", "record": {"updated_at": "2001-01-01T00:00:00Z"}}\n""" + \
        """{"type": "RECORD", "stream": "fake_incremental_stream", "record": {"updated_at": "2002-01-01T00:00:00Z"}}\n""" + \
        """{"type": "STATE", "value": {"bookmarks": {"fake_incremental_stream": {"field": "updated_at", "last_record": "2002-01-01T00:00:00Z"}}}}\n""" + \
        """{"type": "SCHEMA", "stream": "fake_full_table_stream", "schema": {"properties": {"id": {"type": "string"}, "updated_at": {"format": "date-time", "type": "string"}}, "selected": true}, "key_properties": ["id"]}\n""" + \
        """{"type": "RECORD", "stream": "fake_full_table_stream", "record": {"updated_at": "2010-01-01T00:00:00Z"}}\n""" + \
        """{"type": "RECORD", "stream": "fake_full_table_stream", "record": {"updated_at": "2011-01-01T00:00:00Z"}}\n""" + \
        """{"type": "RECORD", "stream": "fake_full_table_stream", "record": {"updated_at": "2012-01-01T00:00:00Z"}}\n""" \
            .strip(), "expect the full stdout to look like this"

    def test_component_incremental_stream_api_response_contains_no_new_results(
            self, mock_requests, tmp_path, config, catalog, state, capsys, monkeypatch
    ):
        # Given - We configure
        # Tap inputs
        # catalog.json, config.json, and state.json come from fixtures
        monkeypatch.setattr(tap_mavenlink, "AVAILABLE_STREAMS", [FakeIncrementalStream])

        # And an API response that contains no results.
        # This can happen if a table has no new rows since the tap was last run.
        mock_requests.request.return_value = MockIncrementalAPIResponseNoResults()

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

        # Then
        # We see a SCHEMA message, but no RECORD or STATE messages.
        captured = capsys.readouterr()
        assert captured.out == \
        """{"type": "SCHEMA", "stream": "fake_incremental_stream", "schema": {"properties": {"id": {"type": "string"}, "updated_at": {"format": "date-time", "type": "string"}}, "selected": true}, "key_properties": ["id"]}\n""", \
            "expect the full stdout to look like this"

