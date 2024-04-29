"""
This file implements the "init" command for the Phenoplier CLI

The "init" command initializes the Phenoplier project by creating the necessary configuration files
at the user's home directory.
"""
from typing import Annotated

import typer
from pathlib import Path
import tomlkit
from functools import wraps
from phenoplier.constants.metadata import CONFIG_FILE, USER_SETTINGS_FILE
from phenoplier.constants.templates import USER_SETTINGS


def create_user_config():
    config_file = CONFIG_FILE
    if not CONFIG_FILE.exists():
        config = USER_SETTINGS
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(tomlkit.dumps(config))
        typer.echo("Config file created at " + str(config_file) + ".")
    else:
        typer.echo("Config file already exists at " + str(config_file) + ".")


def init_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        config_file = CONFIG_FILE
        if not config_file.exists():
            typer.echo("Config file does not exist. Please run the init command first.")
            raise typer.Exit()
        # Optionally, read config here if needed for the function
        with open(config_file, "r") as f:
            config = tomlkit.loads(f.read())  # Using tomlkit.loads to read TOML data from file
        return function(*args, **kwargs)

    return wrapper

# TODO: Add a prompt to ask the user if they want to overwrite the existing config file
def init(
    output_file: Annotated[str, typer.Option("--output-file", "-o", help="Path to the output user settings file")] = str(USER_SETTINGS_FILE),
):
    """
    Initialize the user config file in the home directory in TOML format.
    """
    create_user_config()


@init_required
def hello():
    """
    Example command that requires a config file.
    """
    typer.echo("Hello, the config file exists!")
