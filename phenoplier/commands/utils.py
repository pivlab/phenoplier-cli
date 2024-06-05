import shutil
from pathlib import Path
from typing import List

import typer

from phenoplier.config import settings, SETTINGS_FILES


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
            raise typer.BadParameter(f"Config file {str(file_name)} does not exist at {directory}. Please run 'phenoplier init' first.")


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
