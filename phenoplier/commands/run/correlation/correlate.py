import traceback
import warnings
from typing import Annotated
from pathlib import Path
from enum import Enum

import typer
import pickle
from tqdm import tqdm
import pandas as pd
import numpy as np

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.cli import Corr_Correlate_Args as Args


def correlate(
        cohort_name:                    Annotated[Cohort, Args.COHORT_NAME.value],
        reference_panel:                Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model:                     Annotated[EqtlModel, Args.EQTL_MODEL.value],
        chromosome:                     Annotated[int, Args.CHROMOSOME.value],
        smultixcan_condition_number:    Annotated[int, Args.SMULTIXCAN_CONDITION_NUMBER.value],
        project_dir:                    Annotated[Path, Args.PROJECT_DIR.value],
        compute_within_distance:        Annotated[bool, Args.COMPUTE_WITHIN_DISTANCE.value] = False,
        debug_mode:                     Annotated[bool, Args.DEBUG_MODE.value] = False,
):
    """
    Computes predicted expression correlations between all genes in the MultiPLIER models.
    """

    load_settings_files(project_dir)
    cohort_name = cohort_name.lower()
    eqtl_model = eqtl_model.value
    warnings.filterwarnings("error")

    if not 1 <= chromosome <= 22:
        raise ValueError("Chromosome number must be between 1 and 22")

    cohort_name = cohort_name.lower()
    eqtl_model_files_prefix = conf.TWAS["PREDICTION_MODELS"][f"{eqtl_model}_PREFIX"]

    # Output messages
    print(f"Cohort name: {cohort_name}")
    print(f"Reference panel: {reference_panel}")
    print(f"eQTL model: {eqtl_model}) / {eqtl_model_files_prefix}")
    print(f"Chromosome: {chromosome}")
    print(f"S-MultiXcan condition number: {smultixcan_condition_number}")
    if compute_within_distance:
        print("Compute correlations within distance")

    output_dir_base = (
            Path(conf.RESULTS["GLS"])
            / "gene_corrs"
            / "cohorts"
            / cohort_name
            / reference_panel.lower()
            / eqtl_model.lower()
    )
    output_dir_base.mkdir(parents=True, exist_ok=True)
    print(f"Using output directory: {output_dir_base}")

    with open(output_dir_base / "gwas_variant_ids.pkl", "rb") as handle:
        gwas_variants_ids_set = pickle.load(handle)

    spredixcan_genes_models = pd.read_pickle(output_dir_base / "gene_tissues.pkl")
    genes_info = pd.read_pickle(output_dir_base / "genes_info.pkl")

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

                    print(
                        f"RuntimeWarning for genes {gene1_obj.ensembl_id} and {gene2_obj.ensembl_id}",
                        flush=True,
                    )
                    print(traceback.format_exc(), flush=True)

                    gene_corrs.append(np.nan)
                except Exception as e:
                    if not debug_mode:
                        raise e

                    print(
                        f"Exception for genes {gene1_obj.ensembl_id} and {gene2_obj.ensembl_id}",
                        flush=True,
                    )
                    print(traceback.format_exc(), flush=True)

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
        print("Works!")
    except Exception as e:
        print(f"Cholesky decomposition failed: {str(e)}")

    try:
        cholsigmainv = np.linalg.cholesky(np.linalg.inv(gene_corrs_df.to_numpy())).T
        print("Works!")
    except Exception as e:
        print(f"Cholesky decomposition failed (statsmodels.GLS): {str(e)}")
