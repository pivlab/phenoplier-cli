"""
This file implements the "init" command for the Phenoplier CLI

The "init" command initializes the Phenoplier project by creating the necessary configuration files
at the user's home directory.
"""

import typer
from pathlib import Path
import tomlkit
from functools import wraps
from phenoplier.constants.metadata import CONFIG_FILE

app = typer.Typer()


def create_user_config():
    config_path = Path.home() / CONFIG_FILE
    if not config_path.exists():
        config = {"example_key": "example_value"}
        with open(config_path, "w") as f:
            f.write(tomlkit.dumps(config))  # Using tomlkit.dumps to convert dict to TOML string
        typer.echo("Config file created.")
    else:
        typer.echo("Config file already exists.")


def config_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        config_path = Path.home() / CONFIG_FILE
        if not config_path.exists():
            typer.echo("Config file does not exist. Please run the init command first.")
            raise typer.Exit()
        # Optionally, read config here if needed for the function
        with open(config_path, "r") as f:
            config = tomlkit.loads(f.read())  # Using tomlkit.loads to read TOML data from file
        return function(*args, **kwargs)

    return wrapper


@app.command()
def init():
    """
    Initialize the user config file in the home directory in TOML format.
    """
    create_user_config()


@app.command()
@config_required
def hello():
    """
    Example command that requires a config file.
    """
    typer.echo("Hello, the config file exists!")


if __name__ == "__main__":
    app()
