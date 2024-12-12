"""
This module is a sub-command of the main CLI. It projects input data into the specified representation space.
"""
import phenoplier.multiplier as multiplier

from pathlib import Path
from typing import Annotated

from phenoplier.commands.util.utils import load_settings_files
from phenoplier.constants.arg import Common_Args
from phenoplier.constants.arg import Project_Args as args
from phenoplier.config import settings as conf
from phenoplier.utils import read_rds


def to_multiplier(
    input_file:  Annotated[Path, args.INPUT_FILE.value],
    output_file: Annotated[Path, args.OUTPUT_FILE.value] = None,
    project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = conf.CURRENT_DIR
):
    """
    Projects new data into the MultiPLIER latent space.
    """
    load_settings_files(project_dir)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Generate default output filename if not provided
    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}_projected_to_m.pkl"
    
    rds_data = read_rds(input_file)
    proj_data = multiplier.transform(rds_data)
    # save the projected data as pd.DataFrame
    proj_data.to_pickle(output_file)
