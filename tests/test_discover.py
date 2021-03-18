import json
import jsonschema
import pytest
from unittest.mock import patch

from tests import constants
from tap_mavenlink import main


EXPECTED_DISCOVERY_CONTENT = './tests/discovery.json'
EXPECTED_DISCOVERY_SCHEMA_CONTENT = './tests/catalog-schema.json'


def test_discover_no_catalog(tmp_path, config, capsys):
    # Given
    sys_args = [
        'tap-mavenlink',
        '--config', str(tmp_path / constants.CONFIG_FILENAME),
        '--discover'
    ]

    # When
    with patch('sys.argv', sys_args):
        main()

    captur = capsys.readouterr()
    stdout = captur.out

    with open(EXPECTED_DISCOVERY_CONTENT, 'r') as f:
        expected_discovery = f.read()

    with open(EXPECTED_DISCOVERY_SCHEMA_CONTENT, 'r') as f:
        expected_discovery_schema = f.read()

    # Then
    assert stdout == expected_discovery
    jsonschema.validate(json.loads(expected_discovery), json.loads(expected_discovery_schema))
