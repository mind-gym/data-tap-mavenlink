import json
import pytest

from tests import constants


@pytest.fixture()
def catalog(tmp_path):
    """
    Write dummy catalog.json file for component tests to pick up.
    """

    path = tmp_path / constants.CATALOG_FILENAME
    path.write_text(json.dumps(constants.CATALOG))
