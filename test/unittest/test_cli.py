from phenoplier.cli import load_settings_files, create_settings_files, remove_settings_files
from pytest import fixture, mark, raises
from phenoplier.config import settings, SETTINGS_FILES
from pathlib import Path
import random

_TEST_OUTPUT_DIR = settings.TEST_OUTPUT_DIR / "unittest"


@mark.parametrize("directory", [
    _TEST_OUTPUT_DIR,
])
def test_create_user_settings(directory):
    create_settings_files(directory)
    for file_name in SETTINGS_FILES:
        assert (directory / file_name).exists()
        (directory / file_name).unlink()


@mark.parametrize("directory", [
    _TEST_OUTPUT_DIR / f"{random.getrandbits(128)}",
    _TEST_OUTPUT_DIR / f"{random.getrandbits(128)}",
    _TEST_OUTPUT_DIR / f"{random.getrandbits(128)}",
])
def test_load_settings_files_on_non_existing_dir(directory):
    with (raises(Exception)): load_settings_files(directory)


def test_load_settings_files():
    directory = Path(_TEST_OUTPUT_DIR, test_load_settings_files.__name__)
    create_settings_files(directory)
    load_settings_files(directory)
    for file_name in SETTINGS_FILES:
        file = Path(settings.CACHE_DIR, file_name)
        assert file.exists()
        file.unlink()
    remove_settings_files(directory)