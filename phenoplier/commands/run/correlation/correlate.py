import traceback
import warnings
import logging
from typing import Annotated
from pathlib import Path

import pickle
from tqdm import tqdm
import pandas as pd
import numpy as np

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.cli import Corr_Correlate_Args as Args


logger = logging.getLogger(__name__)

def correlate(
        cohort:                         Annotated[Cohort, Args.COHORT_NAME.value],
        reference_panel:                Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model:                     Annotated[EqtlModel, Args.EQTL_MODEL.value],
        chromosome:                     Annotated[int, Args.CHROMOSOME.value],
        smultixcan_condition_number:    Annotated[int, Args.SMULTIXCAN_CONDITION_NUMBER.value] = 30,
        compute_within_distance:        Annotated[bool, Args.COMPUTE_WITHIN_DISTANCE.value] = False,
        debug_mode:                     Annotated[bool, Args.DEBUG_MODE.value] = False,
        input_dir:                      Annotated[Path, Args.INPUT_DIR.value] = None,
        output_dir:                     Annotated[Path, Args.OUTPUT_DIR.value] = None,
        project_dir:                    Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
):
    """
    Computes predicted expression correlations between all genes in the MultiPLIER models.
    """

    load_settings_files(project_dir)
    cohort = cohort.lower()
    eqtl_model = eqtl_model.value
    warnings.filterwarnings("error")

    if not 1 <= chromosome <= 22:
        raise ValueError("Chromosome number must be between 1 and 22")

    cohort = cohort.lower()
    eqtl_model_files_prefix = conf.TWAS["PREDICTION_MODELS"][f"{eqtl_model}_PREFIX"]

    # Output messages
    logger.info(f"Cohort name: {cohort}")
    logger.info(f"Reference panel: {reference_panel}")
    logger.info(f"eQTL model: {eqtl_model}) / {eqtl_model_files_prefix}")
    logger.info(f"Chromosome: {chromosome}")
    logger.info(f"S-MultiXcan condition number: {smultixcan_condition_number}")
    if compute_within_distance:
        logger.info("Compute correlations within distance")

    if not output_dir:
        output_dir_base = (
                Path(conf.RESULTS["GLS"])
                / "gene_corrs"
                / "cohorts"
                / cohort
                / reference_panel.lower()
                / eqtl_model.lower()
        )
    else:
        output_dir_base = output_dir
    output_dir_base.mkdir(parents=True, exist_ok=True)
    logger.info(f"Using output directory: {output_dir_base}")

    # Load previous matrix generation pipeline results
    pre_results_dir = output_dir_base if not input_dir else input_dir
    input_file = Path(pre_results_dir) / "gwas_variant_ids.pkl"
    if not input_file.exists():
        err_msg = f"Input file not found: {input_file}"
        logger.exception(err_msg)
        raise FileNotFoundError(err_msg)
    with open(input_file, "rb") as handle:
        gwas_variants_ids_set = pickle.load(handle)

    spredixcan_genes_models = pd.read_pickle(pre_results_dir / "gene_tissues.pkl")
    genes_info = pd.read_pickle(pre_results_dir / "genes_info.pkl")

    # Prepare output
    output_dir = output_dir_base / "by_chr"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_file = output_dir / f"gene_corrs-chr{chromosome}.pkl"

    all_chrs = genes_info["chr"].dropna().unique()
    assert all_chrs.shape[0] == 22 and chromosome in all_chrs

    genes_chr = genes_info[genes_info["chr"] == chromosome].sort_values("start_position")
    gene_chr_objs = [Gene(ensembl_id=gene_id) for gene_id in genes_chr["id"]]

    n = len(gene_chr_objs)
    n_comb = n + int(n * (n - 1) / 2.0)

    gene_corrs = []
    gene_corrs_data = np.full((n, n), np.nan, dtype=np.float64)

    with tqdm(ncols=100, total=n_comb) as pbar:
        for gene1_idx in range(0, len(gene_chr_objs)):
            gene1_obj = gene_chr_objs[gene1_idx]
            gene1_tissues = spredixcan_genes_models.loc[gene1_obj.ensembl_id, "tissue"]

            for gene2_idx in range(gene1_idx, len(gene_chr_objs)):
                gene2_obj = gene_chr_objs[gene2_idx]
                gene2_tissues = spredixcan_genes_models.loc[gene2_obj.ensembl_id, "tissue"]

                pbar.set_description(f"{gene1_obj.ensembl_id} / {gene2_obj.ensembl_id}")

                try:
                    r = gene1_obj.get_ssm_correlation(
                        other_gene=gene2_obj,
                        tissues=gene1_tissues,
                        other_tissues=gene2_tissues,
                        snps_subset=gwas_variants_ids_set,
                        condition_number=smultixcan_condition_number,
                        reference_panel=reference_panel,
                        model_type=eqtl_model,
                        use_within_distance=compute_within_distance,
                    )

                    if r is None:
                        r = 0.0

                    gene_corrs.append(r)
                    gene_corrs_data[gene1_idx, gene2_idx] = r
                    gene_corrs_data[gene2_idx, gene1_idx] = r
                except Warning as e:
                    if not debug_mode:
                        raise e

                    logger.info(
                        f"RuntimeWarning for genes {gene1_obj.ensembl_id} and {gene2_obj.ensembl_id}",
                        flush=True,
                    )
                    logger.info(traceback.format_exc(), flush=True)

                    gene_corrs.append(np.nan)
                except Exception as e:
                    if not debug_mode:
                        raise e

                    logger.info(
                        f"Exception for genes {gene1_obj.ensembl_id} and {gene2_obj.ensembl_id}",
                        flush=True,
                    )
                    logger.info(traceback.format_exc(), flush=True)

                    gene_corrs.append(np.nan)

                pbar.update(1)

    gene_corrs_flat = pd.Series(gene_corrs)
    gene_chr_ids = [g.ensembl_id for g in gene_chr_objs]
    gene_corrs_df = pd.DataFrame(
        data=gene_corrs_data,
        index=gene_chr_ids,
        columns=gene_chr_ids,
    )

    gene_corrs_df.to_pickle(output_file)

    try:
        chol_mat = np.linalg.cholesky(gene_corrs_df.to_numpy())
        cov_inv = np.linalg.inv(chol_mat)
        # logger.info("Works!")
    except Exception as e:
        logger.info(f"Cholesky decomposition failed: {str(e)}")

    try:
        cholsigmainv = np.linalg.cholesky(np.linalg.inv(gene_corrs_df.to_numpy())).T
        # logger.info("Works!")
    except Exception as e:
        logger.info(f"Cholesky decomposition failed (statsmodels.GLS): {str(e)}")
