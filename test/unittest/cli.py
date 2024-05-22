from phenoplier.cli import load_config_files, create_config_files
from pytest import fixture, mark, raises
from tempfile import TemporaryDirectory
from phenoplier.config import settings, SETTINGS_FILES
import random

_TEST_OUTPUT_DIR = settings.TEST_OUTPUT_DIR / "unittest"


@mark.parametrize("directory", [
    _TEST_OUTPUT_DIR,
])
def test_create_user_settings(directory):
    create_config_files(directory)
    for file_name in SETTINGS_FILES:
        assert (directory / file_name).exists()
        (directory / file_name).unlink()


@mark.parametrize("directory", [
    _TEST_OUTPUT_DIR / f"{random.getrandbits(128)}",
    _TEST_OUTPUT_DIR / f"{random.getrandbits(128)}",
    _TEST_OUTPUT_DIR / f"{random.getrandbits(128)}",
])
def test_load_config_file_on_non_existing_dir(directory):
    with (raises(Exception)): load_config_files(directory)
