from phenoplier.cli import load_settings_files, create_settings_files, remove_settings_files
from pytest import fixture, mark, raises
import phenoplier.config
from pathlib import Path
import random
import importlib

_TEST_OUTPUT_DIR = phenoplier.config.settings.TEST_OUTPUT_DIR / "unittest"


@mark.parametrize("directory", [
    _TEST_OUTPUT_DIR,
])
def test_create_user_settings(directory):
    create_settings_files(directory)
    for file_name in phenoplier.config.SETTINGS_FILES:
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
    # Create the settings files
    directory = Path(_TEST_OUTPUT_DIR, test_load_settings_files.__name__)
    remove_settings_files(directory)
    remove_settings_files(Path(phenoplier.config.settings.CACHE_DIR))
    # Before loading the settings files, the following settings should not be present
    unloaded_settings = ['DATA_DIR']
    for s in unloaded_settings:
        assert not hasattr(phenoplier.config.settings, s)
    create_settings_files(directory)
    print(hex(id(phenoplier.config.settings)))
    load_settings_files(directory)
    print(hex(id(phenoplier.config.settings)))
    # importlib.reload(phenoplier.config)
    # Check that previous unloaded settings files were loaded
    try:
        for s in unloaded_settings:
            assert hasattr(phenoplier.config.settings, s)
    finally:
        # Clean up
        remove_settings_files(directory)
        remove_settings_files(Path(phenoplier.config.settings.CACHE_DIR))