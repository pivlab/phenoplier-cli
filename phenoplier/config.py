import tempfile
import os
from pathlib import Path
from dynaconf import Dynaconf
from tomlkit import parse


pacakge_toml_file = Path(__file__).parent.parent.resolve() / "pyproject.toml"
with open(pacakge_toml_file) as f:
    package_toml = parse(f.read())
    _PACKAGE_NAME = package_toml["tool"]["poetry"]["name"]
    _PACKAGE_VERSION = package_toml["tool"]["poetry"]["version"]


# Config files
CONFIG_FOLDER = Path.home() / ("." + _PACKAGE_NAME)
CONFIG_FILE = CONFIG_FOLDER / "config.toml"
USER_SETTINGS_FILE = CONFIG_FOLDER / "user_settings.toml"

# The environment variables name supersede these settings
# Prefix the environment variables with `$_PACKAGE_NAME` to automatically load them
# E.g. `export {$_PACKAGE_NAME}_FOO=bar` will load `FOO=bar` in the settings

settings = Dynaconf(
    envvar_prefix="PHENOPLIER",
    # TODO: Append the curr_dir settings to override the default settings
    settings_files=["user_settings.toml", "internal_settings.toml"],

    APP_NAME=_PACKAGE_NAME,
    APP_VERSION=_PACKAGE_VERSION,
    CURRENT_DIR=os.getcwd(),

    # Specifies the main directory where all data and results generated are stored.
    # When setting up the environment for the first time, input data will be
    # automatically downloaded into a subfolder of ROOT_DIR. If not specified, it
    # defaults to the 'phenoplier' subfolder in the temporary directory of the
    # operating system (i.e. '/tmp/phenoplier' in Unix systems).
    #
    ROOT_DIR=str(Path(tempfile.gettempdir(), _PACKAGE_NAME).resolve()),
    # Directory contains the git repository
    CODE_DIR=str(Path(__file__).resolve().parent),
    # Directory contains the tests
    TEST_DIR=str(Path(__file__).resolve().parent.parent / "test"),
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
