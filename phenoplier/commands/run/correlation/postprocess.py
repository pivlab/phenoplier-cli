import typer
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.correlations import (
    check_pos_def,
    adjust_non_pos_def,
)

def validate_inputs(cohort_name, reference_panel, eqtl_model):
    assert cohort_name is not None and len(cohort_name) > 0, "A cohort name must be given"
    assert reference_panel is not None and len(reference_panel) > 0, "A reference panel must be given"
    assert eqtl_model is not None and len(eqtl_model) > 0, "A prediction/eQTL model must be given"
    return cohort_name.lower(), reference_panel, eqtl_model


def plot_distribution_and_heatmap(full_corr_matrix):
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
    plt.show()


def postprocess(
        cohort_name: str = typer.Option(..., help="Cohort name, e.g., UK_BIOBANK"),
        reference_panel: str = typer.Option(..., help="Reference panel, e.g., 1000G or GTEX_V8"),
        eqtl_model: str = typer.Option(..., help="Prediction/eQTL model, e.g., MASHR or ELASTIC_NET"),
):
    """
    Reads all gene correlations across all chromosomes and computes a single correlation matrix by assembling a big correlation matrix with all genes.
    """
    cohort_name, reference_panel, eqtl_model = validate_inputs(cohort_name, reference_panel, eqtl_model)

    output_dir_base = (
            conf.RESULTS["GLS"]
            / "gene_corrs"
            / "cohorts"
            / cohort_name
            / reference_panel.lower()
            / eqtl_model.lower()
    )
    output_dir_base.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Using output dir base: {output_dir_base}")

    input_dir = output_dir_base / "by_chr"
    typer.echo(f"Gene correlations input dir: {input_dir}")
    assert input_dir.exists()

    all_gene_corr_files = sorted(
        input_dir.glob("gene_corrs-chr*.pkl"), key=lambda x: int(x.name.split("-chr")[1].split(".pkl")[0])
    )
    assert len(all_gene_corr_files) == 22

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
        typer.echo(f"Processing {chr_corr_file.name}...")
        corr_data = pd.read_pickle(chr_corr_file)
        full_corr_matrix.loc[corr_data.index, corr_data.columns] = corr_data

        is_pos_def = check_pos_def(corr_data)
        if not is_pos_def:
            typer.echo("Fixing non-positive definite matrix...")
            corr_data = adjust_non_pos_def(corr_data)
            assert check_pos_def(corr_data), "Could not adjust gene correlation matrix"
            full_corr_matrix.loc[corr_data.index, corr_data.columns] = corr_data

    assert np.all(full_corr_matrix.to_numpy().diagonal() == 1.0)

    is_pos_def = check_pos_def(full_corr_matrix)
    if not is_pos_def:
        typer.echo("Fixing non-positive definite full correlation matrix...")
        full_corr_matrix = adjust_non_pos_def(full_corr_matrix)
        assert check_pos_def(full_corr_matrix), "Could not adjust full gene correlation matrix"

    output_file = output_dir_base / "gene_corrs-symbols.pkl"
    gene_corrs = full_corr_matrix.rename(index=Gene.GENE_ID_TO_NAME_MAP, columns=Gene.GENE_ID_TO_NAME_MAP)
    gene_corrs.to_pickle(output_file)

    typer.echo("Computation of gene correlations completed successfully.")

    plot_distribution_and_heatmap(full_corr_matrix)

