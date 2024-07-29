import logging
import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Annotated
from pathlib import Path

import pandas as pd
import numpy as np
from scipy import sparse
from tqdm import tqdm

from phenoplier.config import settings as conf
from phenoplier.gls import GLSPhenoplier
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
# from phenoplier.constants.cli import Corr_Generate_Args as Args
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.constants.cli import Common_Args, Corr_Preprocess_Args, Corr_Pipeline_Args
from phenoplier.commands.invoker import invoke_corr_preprocess

logger = logging.getLogger(__name__)


def save_checkpoint():
    raise NotImplementedError()


def load_checkpoint():
    raise NotImplementedError()


# Get the current timestamp
now = datetime.datetime.now()
timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
pipeline_res_dir = Path(conf.CURRENT_DIR) / "pipeline_results" / timestamp_str


def pipeline(
        cohort_name: Annotated[Cohort, Common_Args.COHORT_NAME.value],
        reference_panel: Annotated[RefPanel, Common_Args.REFERENCE_PANEL.value],
        eqtl_model: Annotated[EqtlModel, Common_Args.EQTL_MODEL.value],
        gwas_file: Annotated[Path, Corr_Preprocess_Args.GWAS_FILE.value],
        spredixcan_folder: Annotated[Path, Corr_Preprocess_Args.SPREDIXCAN_FOLDER.value],
        spredixcan_file_pattern: Annotated[str, Corr_Preprocess_Args.SPREDIXCAN_FILE_PATTERN.value],
        smultixcan_file: Annotated[Path, Corr_Preprocess_Args.SMULTIXCAN_FILE.value],
        project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
        output_dir: Annotated[Path, Corr_Pipeline_Args.OUTPUT_DIR.value] = pipeline_res_dir,
):
    """
    This command integrated all other commands to compute the final gene-gene correlation matrix, and is recommended
    to be used in a cluster environment. Checkpoints will be created during the computation, so it can be resumed if
    interrupted. For finer-grained control, use the other commands below.
    """
    logger.info("Running subroutine <preprocess>...")
    suc, msg = invoke_corr_preprocess(cohort_name,
                                      gwas_file,
                                      spredixcan_folder,
                                      spredixcan_file_pattern,
                                      smultixcan_file,
                                      reference_panel,
                                      eqtl_model,
                                      project_dir)
    if suc:
        logger.info("Subroutine <preprocess> finished successfully.")
    else:
        logger.error("Subroutine <preprocess> failed.")
        logger.error(msg)
        return


    return
