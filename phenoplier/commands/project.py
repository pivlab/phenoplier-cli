"""
This module is a sub-command of the main CLI. It projects input data into the specified representation space.
"""

from enum import Enum
from pathlib import Path
from typing import Annotated
import typer
from phenoplier.data import Downloader
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.constants.arg import Common_Args
from phenoplier.config import settings as conf


def multiplier(
    project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = conf.CURRENT_DIR
):
    """
    Projects new data into the MultiPLIER latent space.
    """
    load_settings_files(project_dir)
