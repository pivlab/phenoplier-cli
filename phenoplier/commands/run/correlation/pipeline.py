import logging
import datetime
import concurrent.futures
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
from phenoplier.constants.arg import (
    Common_Args,
    Corr_Preprocess_Args,
    Corr_Correlate_Args,
    Corr_Pipeline_Args
)

from phenoplier.commands.invoker import (
    invoke_corr_preprocess,
    invoke_corr_correlate,
    invoke_corr_postprocess)

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
        # Common arguments
        cohort: Annotated[Cohort, Common_Args.COHORT_NAME.value],
        reference_panel: Annotated[RefPanel, Common_Args.REFERENCE_PANEL.value],
        eqtl_model: Annotated[EqtlModel, Common_Args.EQTL_MODEL.value],
        # Preprocess arguments
        gwas_file: Annotated[Path, Corr_Preprocess_Args.GWAS_FILE.value],
        spredixcan_folder: Annotated[Path, Corr_Preprocess_Args.SPREDIXCAN_FOLDER.value],
        spredixcan_file_pattern: Annotated[str, Corr_Preprocess_Args.SPREDIXCAN_FILE_PATTERN.value],
        smultixcan_file: Annotated[Path, Corr_Preprocess_Args.SMULTIXCAN_FILE.value],
        # Correlate arguments
        # chromosome: Annotated[int, Corr_Correlate_Args.CHROMOSOME.value] = None,
        smultixcan_condition_number: Annotated[int, Corr_Correlate_Args.SMULTIXCAN_CONDITION_NUMBER.value] = 30,
        compute_within_distance: Annotated[bool, Corr_Correlate_Args.COMPUTE_WITHIN_DISTANCE.value] = False,
        correlate_debug_mode: Annotated[bool, Corr_Correlate_Args.DEBUG_MODE.value] = False,
        # Common arguments with default values
        project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
        output_dir: Annotated[Path, Corr_Pipeline_Args.OUTPUT_DIR.value] = pipeline_res_dir,
):
    """
    This command integrated all other commands to compute the final gene-gene correlation matrix, and is recommended
    to be used in a cluster environment. Checkpoints will be created during the computation, so it can be resumed if
    interrupted. For finer-grained control, use the other commands below.
    """
    # logger.info("Running subroutine <preprocess>...")
    # suc, msg = invoke_corr_preprocess(
    #     cohort=cohort,
    #     gwas_file=gwas_file,
    #     spredixcan_folder=spredixcan_folder,
    #     spredixcan_file_pattern=spredixcan_file_pattern,
    #     smultixcan_file=smultixcan_file,
    #     reference_panel=reference_panel,
    #     eqtl_model=eqtl_model,
    #     project_dir=project_dir,
    #     output_dir=output_dir,
    # )
    # if suc:
    #     logger.info("Subroutine <preprocess> finished successfully.")
    # else:
    #     logger.error("Subroutine <preprocess> failed.")
    #     logger.error(msg)
    #     exit(1)
    #

    logger.info("Running subroutine <correlate>...")

    def run_correlate(chromosome):
        suc, msg = invoke_corr_correlate(
            cohort=cohort,
            reference_panel=reference_panel,
            eqtl_model=eqtl_model,
            chromosome=chromosome,
            smultixcan_condition_number=smultixcan_condition_number,
            compute_within_distance=compute_within_distance,
            debug_mode=correlate_debug_mode,
            output_dir=output_dir,
            project_dir=project_dir,
        )
        if suc:
            logger.info(f"Subroutine <correlate> for chromosome {chromosome} finished successfully.")
        else:
            logger.error(f"Subroutine <correlate> for chromosome {chromosome} failed.")
            logger.error(msg)
            exit(1)
        return suc

    chromosomes = [1]
    # Use ThreadPoolExecutor for multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the operations and mark each future with its chromosome
        future_to_chromosome = {executor.submit(run_correlate, chromosome): chromosome for chromosome in chromosomes}

        for future in concurrent.futures.as_completed(future_to_chromosome):
            chromosome = future_to_chromosome[future]
            try:
                future.result()
            except Exception as exc:
                logger.error(f"Subroutine <correlate> for chromosome {chromosome} generated an exception: {exc}")
                exit(1)
    logger.info("Subroutine <correlate> finished successfully.")

    # logger.info("Running subroutine <postprocess>...")
    # postprocess_input_dir = output_dir / "by_chr"
    # postprocess_genes_info_file = output_dir / "genes_info.pkl"
    # suc, msg = invoke_corr_postprocess(
    #     cohort=cohort,
    #     reference_panel=reference_panel,
    #     eqtl_model=eqtl_model,
    #     input_dir=postprocess_input_dir,
    #     genes_info=postprocess_genes_info_file,
    #     output_dir=output_dir,
    #     project_dir=project_dir,
    # )
    # if suc:
    #     logger.info("Subroutine <postprocess> finished successfully.")
    # else:
    #     logger.error("Subroutine <postprocess> failed.")
    #     logger.error(msg)
    #     exit(1)

    return
