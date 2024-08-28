import os
import gzip
import pickle
from typing import Annotated, List
from pathlib import Path

import pandas as pd
import numpy as np
from rich import print

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.arg import Corr_Filter_Args as Args
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.correlations import (
    check_pos_def,
    adjust_non_pos_def,
    compare_matrices,
)


def filter(
        cohort:             Annotated[Cohort, Args.COHORT_NAME.value],
        reference_panel:    Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model:         Annotated[EqtlModel, Args.EQTL_MODEL.value],
        distances:          Annotated[List[float], Args.DISTANCES.value] = [5],
        genes_symbols:      Annotated[Path, Args.GENES_SYMBOLS.value] = None,
        output_dir:         Annotated[Path, Args.OUTPUT_DIR.value] = None,
        project_dir:        Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
):
    """
    Reads the correlation matrix generated and creates new matrices with different "within distances" across genes.
    For example, it generates a new correlation matrix with only genes within a distance of 10mb.
    """
    load_settings_files(project_dir)
    cohort = cohort.value

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
    print(f"Using output dir base: {output_dir_base}")
    # Read the gene correlation symbols
    gene_corrs_file = output_dir_base / "gene_corrs-symbols.pkl" if genes_symbols is None else genes_symbols
    gene_corrs = pd.read_pickle(gene_corrs_file)
    print(f"Shape of gene correlation matrix: {gene_corrs.shape}")
    print(f"First 5 rows of gene correlation matrix: {os.linesep} {gene_corrs.head()}")
    genes_corrs_nonzero_sum = (gene_corrs > 0.0).astype(int).sum().sum()
    print(f"Number of nonzero cells: {genes_corrs_nonzero_sum}")

    # Get gene objects
    gene_objs = [Gene(name=gene_name) for gene_name in gene_corrs.index]
    print(f"Length of gene objects: {len(gene_objs)}")

    # Subset full correlation matrix using difference "within distances" across genes
    for full_distance in distances:
        print(f"Using within distance: {full_distance}")
        distance = full_distance / 2.0

        genes_within_distance = np.eye(len(gene_objs)).astype(bool)
        for g0_idx in range(len(gene_objs) - 1):
            g0_obj = gene_objs[g0_idx]
            for g1_idx in range(g0_idx + 1, len(gene_objs)):
                g1_obj = gene_objs[g1_idx]

                g0_g1_wd = g0_obj.within_distance(g1_obj, distance * 1e6)

                genes_within_distance[g0_idx, g1_idx] = g0_g1_wd
                genes_within_distance[g1_idx, g0_idx] = g0_g1_wd

        genes_within_distance = pd.DataFrame(
            genes_within_distance,
            index=gene_corrs.index.copy(),
            columns=gene_corrs.columns.copy()
        )

        # subset full correlation matrix
        gene_corrs_within_distance = gene_corrs[genes_within_distance].fillna(0.0)
        if gene_corrs_within_distance.equals(gene_corrs):
            raise ValueError("Error subsetting gene correlation matrix")
        if np.allclose(gene_corrs_within_distance.to_numpy(), gene_corrs.to_numpy()):
            raise ValueError("Error subsetting gene correlation matrix")
        print(f"First 5 rows of gene correlation matrix within distance: {os.linesep} {gene_corrs_within_distance.head()}")

        # Check if the matrix is positive definite
        is_pos_def = check_pos_def(gene_corrs_within_distance)
        if is_pos_def:
            print("All good.", flush=True, end="\n")
        else:
            print("Not positive definite, fixing... ", flush=True, end="")
            corr_data_adjusted = adjust_non_pos_def(gene_corrs_within_distance)

            is_pos_def = check_pos_def(corr_data_adjusted)
            assert is_pos_def, "Could not adjust gene correlation matrix"

            print("Fixed! comparing...", flush=True, end="\n")
            compare_matrices(gene_corrs_within_distance, corr_data_adjusted)

            # save
            gene_corrs_within_distance = corr_data_adjusted

        # Checks
        if gene_corrs_within_distance.isna().any().any():
            raise ValueError("NaNs in the gene correlation matrix within distance")
        if np.isinf(gene_corrs_within_distance.to_numpy()).any():
            raise ValueError("Infs in the gene correlation matrix within distance")
        if np.iscomplex(gene_corrs_within_distance.to_numpy()).any():
            raise ValueError("Complex numbers in the gene correlation matrix within distance")

        # Show some stats
        genes_corrs_sum = gene_corrs_within_distance.sum()
        n_genes_included = genes_corrs_sum[genes_corrs_sum > 1.0].shape[0]
        genes_corrs_nonzero_sum = (gene_corrs_within_distance > 0.0).astype(int).sum().sum()

        print(f"Number of genes with correlations with other genes: {n_genes_included}")
        print(f"Number of nonzero cells: {genes_corrs_nonzero_sum}")

        corr_matrix_flat = gene_corrs_within_distance.mask(
            np.triu(np.ones(gene_corrs_within_distance.shape)).astype(bool)
        ).stack()
        print(corr_matrix_flat.describe().apply(str))

        # Save the new matrix
        output_file = output_dir_base / f"gene_corrs-symbols-within_distance_{int(full_distance)}mb.pkl.gz"
        gene_corrs_within_distance.to_pickle(output_file)
        with gzip.GzipFile(output_file, "w") as f:
            pickle.dump(gene_corrs_within_distance, f)
        print(f"Done. Saved to {output_file}")
        print()
