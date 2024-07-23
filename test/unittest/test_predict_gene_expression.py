import sqlite3
import warnings
import time
import os
from pathlib import Path

import pandas as pd
from fastparquet import ParquetFile
from pytest import mark, fixture

from phenoplier.config import settings as conf


IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

@fixture
def gene_data():
    gene0_id = "ENSG00000134871"
    gene0_tissue_name = "Artery_Coronary"
    gene1_id = "ENSG00000187498"
    gene1_tissue_name = "Artery_Aorta"
    snps_subset = None

    # get gene prediction weights
    base_prediction_model_dir = Path(conf.TWAS["PREDICTION_MODELS"]["MASHR"])

    input_db_file = base_prediction_model_dir / f"mashr_{gene0_tissue_name}.db"
    with sqlite3.connect(input_db_file) as cnx:
        gene0 = pd.read_sql_query(
            f'select * from weights where gene like "{gene0_id}.%"', cnx
        )

    input_db_file = base_prediction_model_dir / f"mashr_{gene1_tissue_name}.db"
    with sqlite3.connect(input_db_file) as cnx:
        gene1 = pd.read_sql_query(
            f'select * from weights where gene like "{gene1_id}.%"', cnx
        )

    return gene0, gene1, snps_subset, gene0_id, gene0_tissue_name, gene1_id, gene1_tissue_name


@mark.skipif(IN_GITHUB_ACTIONS, reason="Slow and computationally expensive test, skip in GitHub Actions")
def test_gene_correlation(gene_data):
    gene0, gene1, snps_subset, gene0_id, gene0_tissue_name, gene1_id, gene1_tissue_name = gene_data

    # get genes' chromosomes
    gene0_chr = gene0["varID"].str.split("_", n=1, expand=True)[0].unique()
    assert len(gene0_chr) == 1
    gene0_chr = gene0_chr[0]

    gene1_chr = gene1["varID"].str.split("_", n=1, expand=True)[0].unique()
    assert len(gene1_chr) == 1
    gene1_chr = gene1_chr[0]

    assert gene0_chr == gene1_chr

    # get gene variants
    gene_variants = gene0["varID"].tolist() + gene1["varID"].tolist()
    assert len(gene_variants) == len(set(gene_variants))
    if snps_subset is not None:
        if len(snps_subset.intersection(gene_variants)) >= len(gene_variants):
            warnings.warn(
                "snps_subsets is not removing any variants from predictions models. WAITING 5 seconds"
            )
            time.sleep(5)

        # keep only variants in snps_subset
        gene_variants = list(snps_subset.intersection(gene_variants))

    # get intersection of gene variants with variants in parquet file
    base_reference_panel_dir = Path(conf.TWAS["LD_BLOCKS"]["1000G_GENOTYPE_DIR"])

    pf = ParquetFile(str(base_reference_panel_dir / f"{gene0_chr}.variants.parquet"))
    pf_variants = set(pf.columns)

    if snps_subset is not None:
        if len(snps_subset.intersection(pf_variants)) != len(snps_subset):
            warnings.warn(
                "Some SNPs in snps_subset are not present in genotype data. WAITING 5 seconds"
            )
            time.sleep(5)

    gene_variants = [gv for gv in gene_variants if gv in pf_variants]

    gene0 = gene0[gene0["varID"].isin(gene_variants)]
    gene1 = gene1[gene1["varID"].isin(gene_variants)]

    # get individual level data
    ind_data = pd.read_parquet(
        base_reference_panel_dir / f"{gene0_chr}.variants.parquet",
        columns=["individual"] + gene_variants,
    )

    # predict expression for the two genes
    def _predict_expression(gene_data):
        gene_expr = (
            ind_data[["individual"] + gene_data["varID"].tolist()].set_index("individual")
            @ gene_data[["varID", "weight"]].set_index("varID")
        ).squeeze()

        assert gene_expr.min() < gene_expr.max()

        return gene_expr

    gene0_pred_expr = _predict_expression(gene0)
    gene1_pred_expr = _predict_expression(gene1)

    # compute the real correlation
    gene_corr = gene0_pred_expr.corr(gene1_pred_expr)
    print(
        f"\n{gene0_id} ({gene0_tissue_name}) / {gene1_id} ({gene1_tissue_name}): {gene_corr}"
    )

    assert gene_corr is not None
    assert gene_corr > 0  # Assuming a positive correlation is expected

