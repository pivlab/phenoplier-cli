import os
import traceback
import warnings
import logging
from typing import Annotated
from pathlib import Path

import pandas as pd
import numpy as np
from tqdm import tqdm
from rich.text import Text

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.utils import load_settings_files, load_pickle_or_gz_pickle
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.arg import Corr_Correlate_Args as Args

logger = logging.getLogger(__name__)


def correlate(
        cohort: Annotated[Cohort, Args.COHORT_NAME.value],
        reference_panel: Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model: Annotated[EqtlModel, Args.EQTL_MODEL.value],
        chromosome: Annotated[int, Args.CHROMOSOME.value],
        smultixcan_condition_number: Annotated[int, Args.SMULTIXCAN_CONDITION_NUMBER.value] = 30,
        compute_within_distance: Annotated[bool, Args.COMPUTE_WITHIN_DISTANCE.value] = False,
        debug_mode: Annotated[bool, Args.DEBUG_MODE.value] = False,
        input_dir: Annotated[Path, Args.INPUT_DIR.value] = None,
        output_dir: Annotated[Path, Args.OUTPUT_DIR.value] = None,
        project_dir: Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
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
        input_file = Path(pre_results_dir) / "gwas_variant_ids.pkl.gz"
    if not input_file.exists():
        err_msg = f"Input file not found: {input_file}"
        logger.exception(err_msg)
        raise FileNotFoundError(err_msg)

    gwas_variants_ids_set = load_pickle_or_gz_pickle(input_file)
    print(f"Length of input gwas_variant_ids.pkl file: {len(gwas_variants_ids_set)}")
    print(f"First 5 elements of input gwas_variant_ids.pkl file: {list(gwas_variants_ids_set)[:5]}")

    spredixcan_genes_models = pd.read_pickle(pre_results_dir / "gene_tissues.pkl")
    print(f"Shape of input gene_tissues.pkl file: {spredixcan_genes_models.shape}")
    print(f"First 5 elements of input gene_tissues.pkl file: {spredixcan_genes_models.head()}")
    if not spredixcan_genes_models.index.is_unique:
        raise ValueError("Index in spredixcan_genes_models must be unique")

    genes_info = pd.read_pickle(pre_results_dir / "genes_info.pkl")
    print(f"Shape of input genes_info.pkl file: {genes_info.shape}")
    print(f"First 5 elements of input genes_info.pkl file: {genes_info.head()}")

    # Compute correlations
    print(Text("[--- Computing correlations ---]", style="blue"))
    output_dir = output_dir_base / "by_chr"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_file = output_dir / f"gene_corrs-chr{chromosome}.pkl"
    print(f"Output file: {output_file}")

    all_chrs = genes_info["chr"].dropna().unique()
    if not all_chrs.shape[0] == 22:
        raise ValueError("Chromosome information is missing for some genes")
    if chromosome not in all_chrs:
        raise ValueError(f"Chromosome {chromosome} is missing in the genes information")

    # run only on the chromosome specified
    genes_chr = genes_info[genes_info["chr"] == chromosome]
    print(f"Number of genes in chromosome {chromosome}: {genes_chr.shape[0]}")
    # sort genes by starting position to make visualizations better later
    genes_chr = genes_chr.sort_values("start_position")
    gene_chr_objs = [Gene(ensembl_id=gene_id) for gene_id in genes_chr["id"]]

    n = len(gene_chr_objs)
    n_comb = n + int(n * (n - 1) / 2.0)
    print(f"Number of gene combinations: {n_comb}")

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
                        # if r is None, it's very likely because:
                        #  * one of the genes has no prediction models
                        #  * all the SNPs predictors for the gene are not present in the reference panel
                        r = 0.0

                    gene_corrs.append(r)
                    gene_corrs_data[gene1_idx, gene2_idx] = r
                    gene_corrs_data[gene2_idx, gene1_idx] = r

                except Warning as e:
                    if not debug_mode:
                        raise e
                    print(f"RuntimeWarning for genes {gene1_obj.ensembl_id} and {gene2_obj.ensembl_id}")
                    print(traceback.format_exc())
                    gene_corrs.append(np.nan)

                except Exception as e:
                    if not debug_mode:
                        raise e
                    print(f"Exception for genes {gene1_obj.ensembl_id} and {gene2_obj.ensembl_id}",)
                    print(traceback.format_exc())
                    gene_corrs.append(np.nan)

                pbar.update(1)

    gene_corrs_flat = pd.Series(gene_corrs)
    gene_chr_ids = [g.ensembl_id for g in gene_chr_objs]
    gene_corrs_df = pd.DataFrame(
        data=gene_corrs_data,
        index=gene_chr_ids,
        columns=gene_chr_ids,
    )

    # Standard checks and stats
    if gene_corrs_df.isna().any().any():
        raise ValueError("There are NaN values in the gene_corrs_df")
    _min_val = gene_corrs_df.min().min()
    if not _min_val >= -0.05:
        raise ValueError(f"Minimum value in gene_corrs_df is {_min_val}, expected at least -0.05")
    _max_val = gene_corrs_df.max().max()  # this captures the diagonal
    if not _max_val <= 1.05:
        raise ValueError(f"Maximum value in gene_corrs_df is {_max_val}, expected at most 1.05")
    print(f"Descriptive statistics of gene_corrs_df: {os.linesep} {gene_corrs_df.describe()}")

    gene_corrs_quantiles = gene_corrs_flat.quantile(np.arange(0, 1, 0.05))
    print(f"Quantiles of gene_corrs_flat: {os.linesep} {gene_corrs_quantiles}")

    # Positive definiteness
    # print negative eigenvalues
    eigs = np.linalg.eigvals(gene_corrs_df.to_numpy())
    print(f"Number of negative eigenvalues {len(eigs[eigs < 0])}")
    print(eigs[eigs < 0])

    # Output
    gene_corrs_df.to_pickle(output_file)

    # Info
    print(f"Shape of gene_corrs_df: {gene_corrs_df.shape}")

    # Ad-hoc tests
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

    # Todo: add plots here
