import json
import pytest

from tests import constants


@pytest.fixture()
def state(tmp_path):
    """
    Write dummy state.json file for component tests to pick up.
    """

    path = tmp_path / constants.STATE_FILENAME
    path.write_text(json.dumps(constants.STATE))
