"""
This module contains utility functions used by the CLI commands.
"""
import gzip
import os
import pickle
import shutil
from enum import Enum
from typing import Tuple, List, Callable
from functools import wraps
from pathlib import Path

import typer
import tomlkit
from rich import print

from phenoplier.config import SETTINGS_FILES
from phenoplier.config import settings as conf


class EnvMode(str, Enum):
    dev = "dev"
    test = "test"
    test_conf = "test_conf"  # Used for testing the configuration loading
    prod = "prod"


def get_env_mode() -> EnvMode:
    env_mode = os.getenv("ENV_FOR_DYNACONF")
    # Default to production mode
    if env_mode is None:
        return EnvMode.prod
    else:
        return EnvMode(env_mode)


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


def create_settings_files(directory: Path, init: bool = False) -> None:
    """
    Create internal settings files in the specified directory
    :param directory: The directory where the settings files will be created.
    :param init: Whether this function is used by the "init" command so that certain fields need to be updated
    """

    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)

    for file_name in SETTINGS_FILES:
        settings_file = Path(directory) / file_name
        if settings_file.exists():
            print(f"[yellow]Config file {str(file_name)} already exists at {directory}. No actions taken.")
        else:
            template_file_path = Path(conf.TEMPLATE_DIR) / file_name
            shutil.copy2(template_file_path, settings_file)
            # when called by the "init" command, update fields
            if init:
                # Read the existing content
                with open(settings_file, "r") as f:
                    config = tomlkit.load(f)
                # Update config.ROOT_DIR to "directory"
                config["ROOT_DIR"] = str(directory)
                # Write the updated content back to the file
                with open(settings_file, "w") as f:
                    tomlkit.dump(config, f)
            print(f"Config file {str(file_name)} created at {directory}")


def load_settings_files(directory: Path, more_files: Tuple[Path, ...] = ()) -> None:
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
            conf.load_file(settings_file)
            print(f"Config file {str(file_name)} loaded from {directory}")
        else:
            raise typer.BadParameter(f"Config file {str(file_name)} does not exist at {directory}.")
    # Load the additional settings
    if more_files is None:
        return
    for curr_dir_file in more_files:
        file = directory / curr_dir_file
        if not file.exists():
            raise typer.BadParameter(f"Config file {str(file)} does not exist at {directory}.")
        settings_file = directory / file
        conf.load_file(settings_file)
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


def get_model_tissue_names(eqtl_model: str) -> List[str]:
    # TWAS data processing
    # Define the directory containing the prediction model tissue files
    prediction_model_tissues_dir = Path(conf.TWAS["PREDICTION_MODELS"][f"{eqtl_model}"])
    # Define the prefix to be removed from the file names
    prefix = conf.TWAS["PREDICTION_MODELS"][f"{eqtl_model}_PREFIX"]
    # Extract tissue names by removing the prefix and the ".db" extension, then join them with spaces
    prediction_model_tissues = []
    for tissue_file in prediction_model_tissues_dir.glob("*.db"):
        tissue_name = tissue_file.name.replace(prefix, "").replace(".db", "")
        prediction_model_tissues.append(tissue_name)
    return prediction_model_tissues


def load_pickle_or_gz_pickle(file_path):
    if file_path.suffix == '.gz':
        with gzip.open(file_path, 'rb') as f:
            return pickle.load(f)
    else:
        with open(file_path, 'rb') as f:
            return pickle.load(f)