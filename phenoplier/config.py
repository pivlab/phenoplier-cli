"""This module provides the metadata for Phenoplier."""

from importlib.metadata import distribution
from pathlib import Path

# Package metadata
dist = distribution("phenoplier")
APP_NAME = dist.metadata["name"]
APP_VERSION = dist.version
APP_CODE_DIR = Path(__file__).parent.resolve()
APP_TEST_DIR = APP_CODE_DIR / "test"

# Config files
CONFIG_FOLDER = Path.home() / ("." + APP_NAME)
CONFIG_FILE = CONFIG_FOLDER / "config.toml"
USER_SETTINGS_FILE = CONFIG_FOLDER / "user_settings.toml"