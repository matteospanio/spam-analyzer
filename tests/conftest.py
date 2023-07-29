import os
import shutil

import click
import pytest

from app import files


@pytest.fixture(scope="session", autouse=True)
def setup():
    app_dir = click.get_app_dir("spam-analyzer")

    if not os.path.exists(app_dir):
        _ = files.handle_configuration_files()

    def teardown():
        try:
            shutil.rmtree(app_dir)
        except FileNotFoundError:
            pass

    yield

    teardown()
