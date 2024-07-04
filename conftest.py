import os

import pytest


@pytest.fixture(scope="session")
def index_file_path() -> str:
    return os.path.expanduser("~/project/ffxiv/sqpack/0a0000.win32.index")


@pytest.fixture(scope="session")
def data_file_path() -> str:
    return os.path.expanduser("~/project/ffxiv/sqpack/0a0000.win32.dat0")
