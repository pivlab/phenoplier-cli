"""
This file implements the "init" command for the Phenoplier CLI

The "init" command initializes the Phenoplier project by creating the necessary settingsuration files
at the user's home directory.
"""
from typing import Annotated

import typer
from pathlib import Path
import tomlkit
from functools import wraps
from phenoplier.constants.metadata import CONFIG_FILE, USER_SETTINGS_FILE
from phenoplier.constants.templates import USER_SETTINGS


def create_user_settings():
    settings_file = USER_SETTINGS_FILE
    if not settings_file.exists():
        settings = USER_SETTINGS
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        settings_file.write_text(tomlkit.dumps(settings))
        typer.echo("Config file created at " + str(settings_file) + ".")
    else:
        typer.echo("Config file already exists at " + str(settings_file) + ".")


def init_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        settings_file = CONFIG_FILE
        if not settings_file.exists():
            typer.echo("Config file does not exist. Please run the init command first.")
            raise typer.Exit()
        # Optionally, read settings here if needed for the function
        with open(settings_file, "r") as f:
            settings = tomlkit.loads(f.read())  # Using tomlkit.loads to read TOML data from file
        return function(*args, **kwargs)

    return wrapper

# TODO: Add a prompt to ask the user if they want to overwrite the existing settings file
def init(
    output_file: Annotated[str, typer.Option("--output-file", "-o", help="Path to the output user settings file")] = str(USER_SETTINGS_FILE),
):
    """
    Initialize the user settings file in the home directory in TOML format.
    """
    create_user_settings()


@init_required
def hello():
    """
    Example command that requires a settings file.
    """
    typer.echo("Hello, the settings file exists!")
