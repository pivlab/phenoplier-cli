"""
This module is a sub-command of the main CLI. It provides functionality to export Phenoplier's settings.
"""

from pathlib import Path
from typing import Annotated

from phenoplier.commands.util.utils import load_settings_files
from phenoplier.constants.arg import Common_Args
from phenoplier.config import settings as conf


def env_vars(
    project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = conf.CURRENT_DIR
):
    """
    Export phenoplier's settings as environment variables.
    """
    from pathlib import PurePath

    def print_conf(conf_dict):
        for var_name, var_value in conf_dict.items():
            if var_value is None:
                continue
            if isinstance(var_value, (str, int, PurePath)):
                print(f'export PHENOPLIER_{var_name}="{str(var_value)}"')
            elif isinstance(var_value, dict):
                new_dict = {f"{var_name}_{k}": v for k, v in var_value.items()}
                print_conf(new_dict)
            else:
                raise ValueError(f"Configuration type not understood: {var_name}")
    
    load_settings_files(project_dir)
    app_settings = conf.as_dict()
    
    print_conf(app_settings)
