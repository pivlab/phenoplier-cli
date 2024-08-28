import os
from pathlib import Path
from typing import Annotated

from rich import print
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.arg import Corr_Postprocess_Args as Args
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.correlations import (
    check_pos_def,
    adjust_non_pos_def,
    compare_matrices,
)


def validate_inputs(cohort, reference_panel, eqtl_model):
    assert cohort is not None and len(cohort) > 0, "A cohort name must be given"
    assert reference_panel is not None and len(reference_panel) > 0, "A reference panel must be given"
    assert eqtl_model is not None and len(eqtl_model) > 0, "A prediction/eQTL model must be given"
    return cohort.lower(), reference_panel, eqtl_model


def plot_distribution_and_heatmap(full_corr_matrix, output_dir: Path):
    full_corr_matrix_flat = full_corr_matrix.mask(
        np.triu(np.ones(full_corr_matrix.shape)).astype(bool)
    ).stack()

    with sns.plotting_context("paper", font_scale=1.5):
        g = sns.displot(full_corr_matrix_flat, kde=True, height=7)
        g.ax.set_title("Distribution of gene correlation values in all chromosomes")

    vmin_val = 0.0
    vmax_val = max(0.05, full_corr_matrix_flat.quantile(0.99))
    f, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(
        full_corr_matrix,
        xticklabels=False,
        yticklabels=False,
        square=True,
        vmin=vmin_val,
        vmax=vmax_val,
        cmap="rocket_r",
        ax=ax,
    )
    ax.set_title("Gene correlations in all chromosomes")
    # save the plot
    plt.savefig(output_dir / "gene_corrs_heatmap.png")


def postprocess(
        cohort:        Annotated[Cohort, Args.COHORT_NAME.value],
        reference_panel:    Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model:         Annotated[EqtlModel, Args.EQTL_MODEL.value],
        plot_output_dir:    Annotated[Path, Args.PLOT_OUTPUT_DIR.value] = None,
        project_dir:        Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
        input_dir:          Annotated[Path, Args.INPUT_DIR.value] = None,
        genes_info:         Annotated[Path, Args.GENES_INFO.value] = None,
        output_dir:         Annotated[Path, Args.OUTPUT_DIR.value] = None,
):
    """
    Reads all gene correlations across all chromosomes and computes a single correlation matrix by assembling a big
    correlation matrix with all genes.
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
    # Check input dir
    input_dir_ = input_dir or output_dir_base / "by_chr"
    if not input_dir_.exists():
        raise ValueError(f"Gene correlations input dir does not exist: {input_dir_}")
    print(f"Gene correlations input dir: {input_dir_}")
    # sort by chromosome
    all_gene_corr_files = sorted(
        input_dir_.glob("gene_corrs-chr*.pkl"), key=lambda x: int(x.name.split("-chr")[1].split(".pkl")[0])
    )
    # Check if all gene correlation files are present
    if not len(all_gene_corr_files) == 22:
        raise ValueError(f"Expected 22 gene correlation files, found {len(all_gene_corr_files)}")
    print("All gene correlation files being used:")
    print(all_gene_corr_files)

    # Get common genes
    gene_ids = set()
    for f in all_gene_corr_files:
        chr_genes = pd.read_pickle(f).index.tolist()
        gene_ids.update(chr_genes)
    print(f"Lenght of common genes: {len(gene_ids)}")
    print(f"Fist 5 common genes: {os.linesep} {list(gene_ids)[:5]}")

    # Gene info
    genes_info_path = input_dir_.parent / "genes_info.pkl" if genes_info is None else genes_info
    if not genes_info_path.exists():
        raise ValueError(f"Genes info file does not exist: {genes_info_path}")
    genes_info = pd.read_pickle(genes_info_path)
    print(f"Using genes info file: {genes_info_path}")
    print(f"Shape of genes info: {genes_info.shape}")
    print(f"First 5 genes info: {os.linesep} {genes_info.head()}")
    # keep genes in correlation matrices only
    genes_info = genes_info[genes_info["id"].isin(gene_ids)]
    genes_info = genes_info.sort_values(["chr", "start_position"])
    if genes_info.isna().any().any():
        raise ValueError("There are missing values in the genes info")
    print("Processed genes info (keep genes in correlation matrices only):")
    print(f"Shape of the processed genes info: {genes_info.shape}")
    print(f"Fist 5 processed genes info: {os.linesep} {genes_info.head()}")

    # Create full correlation matrix
    full_corr_matrix = pd.DataFrame(
        np.zeros((genes_info.shape[0], genes_info.shape[0])),
        index=genes_info["id"].tolist(),
        columns=genes_info["id"].tolist(),
    )
    if not full_corr_matrix.index.is_unique and full_corr_matrix.columns.is_unique:
        raise ValueError("Gene IDs are not unique")

    for chr_corr_file in all_gene_corr_files:
        print(f"Processing {chr_corr_file.name}...")
        # get correlation matrix for this chromosome
        corr_data = pd.read_pickle(chr_corr_file)
        # save gene correlation matrix
        full_corr_matrix.loc[corr_data.index, corr_data.columns] = corr_data

        # save inverse of Cholesky decomposition of gene correlation matrix
        # first, adjust correlation matrix if it is not positive definite
        is_pos_def = check_pos_def(corr_data)
        if is_pos_def:
            print("All good.")
            print()
        else:
            print("Fixing non-positive definite matrix...")
            corr_data = adjust_non_pos_def(corr_data)
            if not check_pos_def(corr_data):
                raise ValueError("Could not adjust gene correlation matrix")
            # save
            full_corr_matrix.loc[corr_data.index, corr_data.columns] = corr_data
    print()

    # Checks
    print("Checking if diagonal elements are zero...")
    if not np.all(np.isclose(full_corr_matrix.to_numpy().diagonal(), 1.0)):
        raise ValueError("Diagonal elements are not 1.0")
    # In some cases, even if the submatrices are adjusted, the whole one is not.
    # So here check that again.
    is_pos_def = check_pos_def(full_corr_matrix)
    if is_pos_def:
        print("All good.", flush=True, end="\n")
    else:
        print("Not positive definite, fixing... ", flush=True, end="")
        corr_data_adjusted = adjust_non_pos_def(full_corr_matrix)

        is_pos_def = check_pos_def(corr_data_adjusted)
        assert is_pos_def, "Could not adjust gene correlation matrix"

        print("Fixed! comparing...", flush=True, end="\n")
        compare_matrices(full_corr_matrix, corr_data_adjusted)

        full_corr_matrix = corr_data_adjusted

    # TODO: Add output name to template, sharing across commands
    output_file = output_dir_base / "gene_corrs-symbols.pkl"
    gene_corrs = full_corr_matrix.rename(index=Gene.GENE_ID_TO_NAME_MAP(), columns=Gene.GENE_ID_TO_NAME_MAP())
    gene_corrs.to_pickle(output_file)

    print(f"Computation of gene correlations completed successfully. Output file: {output_file}")

    if plot_output_dir is not None:
        plot_distribution_and_heatmap(full_corr_matrix)
