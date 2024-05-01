"""This file implements the "activate" command for the Phenoplier CLI"""

"""The "activate" command activates the Phenoplier project by exporting the necessary environment variables derived from the user's setting file"""

from typing import Annotated
import os

import typer
from pathlib import Path
import tomlkit
from functools import wraps
from phenoplier.constants.metadata import APP_CODE_DIR, USER_SETTINGS_FILE
from phenoplier.constants.templates import USER_SETTINGS
from pathlib import Path
from phenoplier.libs.settings import update as update_settings


def create_user_settings():
    settings_file = USER_SETTINGS_FILE
    if not settings_file.exists():
        settings = USER_SETTINGS
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        settings_file.write_text(tomlkit.dumps(settings))
        typer.echo("Config file created at " + str(settings_file) + ".")
    else:
        typer.echo("Config file already exists at " + str(settings_file) + ".")


def activate(
    user_settings: Annotated[str, typer.Option("--user-settings", "-s", help="Path to the local user settings file")] = str(USER_SETTINGS_FILE),
):
    """
    Export the necessary environment variables derived from the user's setting file.
    """
    settings = Path(user_settings)
    if not settings.exists():
        raise typer.BadParameter("User settings file does not exist at default location or not provided. Please run the init command first.")
    # Optionally, read settings here if needed for the function
    update_settings()
    # eval "python3 src/phenoplier/libs/conf.py
    os.system(f"python3 {(APP_CODE_DIR / 'src/phenoplier/libs/conf.py').resolve()}")
