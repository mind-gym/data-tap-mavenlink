import json
import pytest

from tests import constants


@pytest.fixture()
def config(tmp_path):
    """
    Write dummy config.json file for component tests to pick up.
    """

    path = tmp_path / constants.CONFIG_FILENAME
    path.write_text(json.dumps(constants.CONFIG))
