import tempfile
import os
from pathlib import Path
from importlib.metadata import distribution
from dynaconf import Dynaconf

_APP_NAME = "phenoplier"
dist = distribution(_APP_NAME)
_APP_VERSION = dist.version

# Config files
CONFIG_FOLDER = Path.home() / ("." + _APP_NAME)
CONFIG_FILE = CONFIG_FOLDER / "config.toml"
USER_SETTINGS_FILE = CONFIG_FOLDER / "user_settings.toml"

# The environment variables name supersede these settings
# Prefix the environment variables with `$_APP_NAME` to automatically load them
# E.g. `export {$_APP_NAME}_FOO=bar` will load `FOO=bar` in the settings

settings = Dynaconf(
    envvar_prefix=_APP_NAME.upper(),
    # TODO: Append the curr_dir settings to override the default settings
    settings_files=["user_settings.toml", "internal_settings.toml"],

    APP_NAME=_APP_NAME,
    APP_VERSION=_APP_VERSION,
    CURRENT_DIR=os.getcwd(),

    # Specifies the main directory where all data and results generated are stored.
    # When setting up the environment for the first time, input data will be
    # automatically downloaded into a subfolder of ROOT_DIR. If not specified, it
    # defaults to the 'phenoplier' subfolder in the temporary directory of the
    # operating system (i.e. '/tmp/phenoplier' in Unix systems).
    #
    ROOT_DIR=str(Path(tempfile.gettempdir(), _APP_NAME).resolve()),
    # Directory contains the git repository
    CODE_DIR=str(Path(__file__).resolve().parent),
    # Directory contains the tests
    TESTS_DIR=str(Path(__file__).resolve().parent / "test"),
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
