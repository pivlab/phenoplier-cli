from functools import wraps
import typer

from phenoplier.constants.metadata import USER_SETTINGS_FILE, APP_CODE_DIR
from phenoplier.libs.settings import update as update_settings
from pathlib import Path
import os


def load_and_update_config(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        settings_file = USER_SETTINGS_FILE
        if not settings_file.exists():
            typer.echo("User settings file does not exist. Please run the init command first.")
            raise typer.Exit()
        # Optionally, read settings here if needed for the function
        update_settings()
        # eval "python3 src/phenoplier/libs/conf.py
        os.system(f"python3 {(APP_CODE_DIR / 'src/phenoplier/libs/conf.py').resolve()}")
        return function(*args, **kwargs)

    return wrapper
