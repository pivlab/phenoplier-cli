import os
import shutil
from pathlib import Path
from enum import Enum
from typing import List, Callable
from functools import wraps
from pathlib import Path

import typer

from phenoplier.config import settings, SETTINGS_FILES


class EnvMode(str, Enum):
    dev = "dev"
    test = "test"
    test_conf = "test_conf"  # Used for testing the configuration loading
    prod = "prod"


def get_env_mode() -> EnvMode:
    env_mode = os.getenv("ENV_FOR_DYNACONF")
    try:
        return EnvMode(env_mode)
    except ValueError:
        raise typer.BadParameter(
            f"Invalid environment mode: {env_mode}. Please set the ENV_FOR_DYNACONF environment variable to one of {list(EnvMode.__members__.keys())}"
        )


def is_in_dev_mode() -> bool:
    return get_env_mode() == EnvMode.dev


def is_in_test_mode() -> bool:
    return get_env_mode() == EnvMode.test


def remove_settings_files(directory: Path) -> None:
    for file_name in SETTINGS_FILES:
        settings_file = Path(directory) / file_name
        if settings_file.exists():
            settings_file.unlink()
            print(f"Config file {str(file_name)} removed from {directory}")


def check_settings_files(directory: Path) -> None:
    for file_name in SETTINGS_FILES:
        settings_file = Path(directory) / file_name
        if not settings_file.exists():
            raise typer.BadParameter(
                f"Config file {str(file_name)} does not exist at {directory}. Please run 'phenoplier init' first.")


def create_settings_files(directory: Path) -> None:
    Path(directory).mkdir(parents=True, exist_ok=True)
    for file_name in SETTINGS_FILES:
        settings_file = Path(directory) / file_name
        if settings_file.exists():
            typer.echo(f"Config file {str(file_name)} already exists at {directory}")
        else:
            template_file = Path(settings.TEMPLATE_DIR) / file_name
            shutil.copy2(template_file, settings_file)
            print(f"Config file {str(file_name)} created at {directory}")


def load_settings_files(directory: Path, more_files: List[Path] = []) -> None:
    """
    Load the settings files from the specified directory. The expected side effect is that after this function is called,
    settings defined in the toml config files will be available as attributes of the settings object.
    :param directory: The directory where the settings files are located.
    :param more_files: A list of settings files other than the default ones to load. Those files should be also in
    the same directory as the default settings file.
    """
    if is_in_dev_mode() or is_in_test_mode():  # In dev/test mode, the settings are loaded from the environment
        return

    # Check if the directory exists
    if not directory.exists():
        raise typer.BadParameter(f"Provided config directory does not exist: {directory}")
    # Check if the settings files exist in the directory
    check_settings_files(directory)
    # Load the default settings
    for file_name in SETTINGS_FILES:
        settings_file = directory / file_name
        if settings_file.exists():
            settings.load_file(settings_file)
            print(f"Config file {str(file_name)} loaded from {directory}")
        else:
            raise typer.BadParameter(f"Config file {str(file_name)} does not exist at {directory}.")
    # Load the additional settings
    for curr_dir_file in more_files:
        file = directory / curr_dir_file
        if not file.exists():
            raise typer.BadParameter(f"Config file {str(file)} does not exist at {directory}.")
        settings_file = directory / file
        settings.load_file(settings_file)
        print(f"Additional config file {str(file)} loaded from {directory}")


def load_settings_files_deco(directory: Path, more_files: List[Path] = []) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Call the settings loading function
            load_settings_files(directory, more_files)
            # Call the original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
