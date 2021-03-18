import json
import jsonschema
import pytest
from unittest.mock import patch

from tests import constants
from tap_mavenlink import main


EXPECTED_CATALOG_DISCOVERED_CONTENT = './tests/catalog-discovered.json'
EXPECTED_CATALOG_SCHEMA_CONTENT = './tests/catalog-schema.json'


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
    catalog_discovered = json.loads(captur.out)

    with open(EXPECTED_CATALOG_DISCOVERED_CONTENT, 'r') as f:
        expected_catalog_discovered = json.loads(f.read())

    with open(EXPECTED_CATALOG_SCHEMA_CONTENT, 'r') as f:
        expected_catalog_schema = json.loads(f.read())

    # Then
    assert catalog_discovered == expected_catalog_discovered
    jsonschema.validate(expected_catalog_discovered, expected_catalog_schema)
