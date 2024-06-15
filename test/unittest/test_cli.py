import os
import random
import shutil
from pathlib import Path

from pytest import mark, raises

import phenoplier.config
from phenoplier.commands.utils import load_settings_files, create_settings_files, remove_settings_files

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
    os.environ["ENV_FOR_DYNACONF"] = "test_conf"
    with (raises(Exception)):
        load_settings_files(directory)
    os.environ["ENV_FOR_DYNACONF"] = "test"


def test_load_settings_files():
    os.environ["ENV_FOR_DYNACONF"] = "test_conf"
    # Create the settings files
    directory = Path(_TEST_OUTPUT_DIR, test_load_settings_files.__name__)
    remove_settings_files(directory)
    # Before loading the settings files, the following settings should not be present
    unloaded_settings = ['_TEST_SETTINGS0', "_TEST_SETTINGS0A", "TEST2._ATTR"]
    for s in unloaded_settings:
        assert not hasattr(phenoplier.config.settings, s)
    # Now create the default settings
    create_settings_files(directory)
    # Now add additional testing configs
    more_settings_files = [Path("./test_load_settings0.toml"), Path("./test_load_settings1.toml")]
    for s in more_settings_files:
        src = Path(__file__).resolve().parent / s
        dst = directory / s
        print(src, dst)
        shutil.copy2(src, dst)
    load_settings_files(directory, more_settings_files)
    # Check that previous unloaded settings files were loaded
    try:
        for s in unloaded_settings:
            assert hasattr(phenoplier.config.settings, s)
    finally:
        # Clean up
        shutil.rmtree(directory)
        os.environ["ENV_FOR_DYNACONF"] = "test"

