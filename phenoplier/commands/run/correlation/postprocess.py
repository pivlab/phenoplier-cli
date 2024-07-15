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
from phenoplier.constants.cli import Corr_Postprocess_Args as Args
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.correlations import (
    check_pos_def,
    adjust_non_pos_def,
)


def validate_inputs(cohort_name, reference_panel, eqtl_model):
    assert cohort_name is not None and len(cohort_name) > 0, "A cohort name must be given"
    assert reference_panel is not None and len(reference_panel) > 0, "A reference panel must be given"
    assert eqtl_model is not None and len(eqtl_model) > 0, "A prediction/eQTL model must be given"
    return cohort_name.lower(), reference_panel, eqtl_model


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
        cohort_name: Annotated[Cohort, Args.COHORT_NAME.value],
        reference_panel: Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model: Annotated[EqtlModel, Args.EQTL_MODEL.value],
        plot_output_dir: Annotated[Path, Args.PLOT_OUTPUT_DIR.value] = None,
        project_dir: Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
):
    """
    Reads all gene correlations across all chromosomes and computes a single correlation matrix by assembling a big correlation matrix with all genes.
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
    output_dir_base.mkdir(parents=True, exist_ok=True)
    print(f"Using output dir base: {output_dir_base}")
    # Check input dir
    input_dir = output_dir_base / "by_chr"
    if not input_dir.exists():
        raise ValueError(f"Gene correlations input dir does not exist: {input_dir}")
    print(f"Gene correlations input dir: {input_dir}")
    # Check if all gene correlation files are present
    all_gene_corr_files = sorted(
        input_dir.glob("gene_corrs-chr*.pkl"), key=lambda x: int(x.name.split("-chr")[1].split(".pkl")[0])
    )
    if not len(all_gene_corr_files) == 22:
        raise ValueError(f"Expected 22 gene correlation files, found {len(all_gene_corr_files)}")

    gene_ids = set()
    for f in all_gene_corr_files:
        chr_genes = pd.read_pickle(f).index.tolist()
        gene_ids.update(chr_genes)

    genes_info = pd.read_pickle(output_dir_base / "genes_info.pkl")
    genes_info = genes_info[genes_info["id"].isin(gene_ids)]
    genes_info = genes_info.sort_values(["chr", "start_position"])

    full_corr_matrix = pd.DataFrame(
        np.zeros((genes_info.shape[0], genes_info.shape[0])),
        index=genes_info["id"].tolist(),
        columns=genes_info["id"].tolist(),
    )

    for chr_corr_file in all_gene_corr_files:
        print(f"Processing {chr_corr_file.name}...")
        corr_data = pd.read_pickle(chr_corr_file)
        full_corr_matrix.loc[corr_data.index, corr_data.columns] = corr_data

        is_pos_def = check_pos_def(corr_data)
        if not is_pos_def:
            print("Fixing non-positive definite matrix...")
            corr_data = adjust_non_pos_def(corr_data)
            if not check_pos_def(corr_data):
                raise ValueError("Could not adjust gene correlation matrix")
            full_corr_matrix.loc[corr_data.index, corr_data.columns] = corr_data

    print("Checking if diagonal elements are zero...")
    if not np.all(np.isclose(full_corr_matrix.to_numpy().diagonal(), 1.0)):
        raise ValueError("Diagonal elements are not 1.0")

    is_pos_def = check_pos_def(full_corr_matrix)
    if not is_pos_def:
        print("Fixing non-positive definite full correlation matrix...")
        full_corr_matrix = adjust_non_pos_def(full_corr_matrix)
        if not check_pos_def(full_corr_matrix):
            raise ValueError("Could not adjust full gene correlation matrix")

    # TODO: Add output name to template, sharing across commands
    output_file = output_dir_base / "gene_corrs-symbols.pkl"
    gene_corrs = full_corr_matrix.rename(index=Gene.GENE_ID_TO_NAME_MAP(), columns=Gene.GENE_ID_TO_NAME_MAP())
    gene_corrs.to_pickle(output_file)

    print(f"Computation of gene correlations completed successfully. Output file: {output_file}")

    if plot_output_dir is not None:
        plot_distribution_and_heatmap(full_corr_matrix)
