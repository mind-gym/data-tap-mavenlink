import pytest
from unittest.mock import patch

from tests import constants
from tap_mavenlink import main


def test_discover_no_catalog(tmp_path, config):
    sys_args = [
        'tap-mavenlink',
        '--config', str(tmp_path / constants.CONFIG_FILENAME),
        '--discover'
    ]
    with patch('sys.argv', sys_args):
        main()
