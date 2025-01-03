"""
This module is a sub-command of the main CLI. It provides functionality to export Phenoplier's settings.
"""

import os
from pathlib import Path, PurePath
from typing import Annotated

from phenoplier.commands.util.utils import load_settings_files
from phenoplier.constants.arg import Common_Args
from phenoplier.config import settings as conf

def print_conf(conf_dict, export: bool = False):
    for var_name, var_value in conf_dict.items():
        if var_value is None:
            continue
        if isinstance(var_value, (str, int, PurePath)):
            if export:
                print(f'export PHENOPLIER_{var_name}="{str(var_value)}"')
                # Add the variable to the environment
                os.environ[f'PHENOPLIER_{var_name}'] = str(var_value)
            else:
                print(f'PHENOPLIER_{var_name}="{str(var_value)}"')
        elif isinstance(var_value, dict):
            new_dict = {f"{var_name}_{k}": v for k, v in var_value.items()}
            print_conf(new_dict, export)
        else:
            raise ValueError(f"Configuration type not understood: {var_name}")

def export(
    project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = conf.CURRENT_DIR
):
    """
    Export phenoplier's settings as environment variables.
    """
    load_settings_files(project_dir)
    app_settings = conf.as_dict()
    print_conf(app_settings, True)


def show(
    project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = conf.CURRENT_DIR
):
    """
    list internal phenoplier's settings.
    """
    load_settings_files(project_dir)
    app_settings = conf.as_dict()
    print_conf(app_settings)
