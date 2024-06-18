from typing import Annotated, List
from pathlib import Path

import pandas as pd
import numpy as np
from rich import print

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.cli import Corr_Filter_Args as Args
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.correlations import (
    check_pos_def,
    adjust_non_pos_def,
)

def filter(
        cohort_name:        Annotated[Cohort, Args.COHORT_NAME.value],
        reference_panel:    Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model:         Annotated[EqtlModel, Args.EQTL_MODEL.value],
        distances:          Annotated[List[float], Args.DISTANCES.value] = [10, 5, 2],
        project_dir:        Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
):
    """
    Reads the correlation matrix generated and creates new matrices with different "within distances" across genes.
    For example, it generates a new correlation matrix with only genes within a distance of 10mb.
    """
    load_settings_files(project_dir)
    cohort_name = cohort_name.value

    output_dir_base = (
            Path(conf.RESULTS["GLS"])
            / "gene_corrs"
            / "cohorts"
            / cohort_name
            / reference_panel.lower()
            / eqtl_model.lower()
    )
    assert output_dir_base.exists(), f"Output directory {output_dir_base} does not exist"
    print(f"Using output dir base: {output_dir_base}")

    gene_corrs = pd.read_pickle(output_dir_base / "gene_corrs-symbols.pkl")
    gene_objs = [Gene(name=gene_name) for gene_name in gene_corrs.index]

    for full_distance in distances:
        distance = full_distance / 2.0
        print(f"Using within distance: {distance}")

        genes_within_distance = np.eye(len(gene_objs)).astype(bool)
        for g0_idx in range(len(gene_objs) - 1):
            g0_obj = gene_objs[g0_idx]
            for g1_idx in range(g0_idx + 1, len(gene_objs)):
                g1_obj = gene_objs[g1_idx]
                genes_within_distance[g0_idx, g1_idx] = g0_obj.within_distance(g1_obj, distance * 1e6)
                genes_within_distance[g1_idx, g0_idx] = genes_within_distance[g0_idx, g1_idx]

        genes_within_distance = pd.DataFrame(
            genes_within_distance, index=gene_corrs.index.copy(), columns=gene_corrs.columns.copy()
        )

        gene_corrs_within_distance = gene_corrs[genes_within_distance].fillna(0.0)

        is_pos_def = check_pos_def(gene_corrs_within_distance)
        if not is_pos_def:
            print("Fixing non-positive definite matrix...")
            gene_corrs_within_distance = adjust_non_pos_def(gene_corrs_within_distance)
            assert check_pos_def(gene_corrs_within_distance), "Could not adjust gene correlation matrix"

        gene_corrs_within_distance.to_pickle(
            output_dir_base / f"gene_corrs-symbols-within_distance_{int(full_distance)}mb.pkl"
        )

        genes_corrs_sum = gene_corrs_within_distance.sum()
        n_genes_included = genes_corrs_sum[genes_corrs_sum > 1.0].shape[0]
        genes_corrs_nonzero_sum = (gene_corrs_within_distance > 0.0).astype(int).sum().sum()

        print(f"Number of genes with correlations with other genes: {n_genes_included}")
        print(f"Number of nonzero cells: {genes_corrs_nonzero_sum}")

        corr_matrix_flat = gene_corrs_within_distance.mask(
            np.triu(np.ones(gene_corrs_within_distance.shape)).astype(bool)
        ).stack()
        print(corr_matrix_flat.describe().apply(str))