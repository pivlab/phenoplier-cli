import gc
import sqlite3
from pathlib import Path

import pandas as pd
import numpy as np
import typer
from tqdm import tqdm

from phenoplier.config import settings as conf
from phenoplier.entity import Gene

def get_reference_panel_file(directory: Path, file_pattern: str) -> Path:
    files = list(directory.glob(f"*{file_pattern}*.parquet"))
    assert len(files) == 1, f"More than one file was found: {files}"
    return files[0]


def covariance(df, dtype):
    n = df.shape[0]
    df = df.sub(df.mean(), axis=1).astype(dtype)
    return df.T.dot(df) / (n - 1)


def compute_snps_cov(snps_df, reference_panel_dir, variants_ids_with_genotype, cov_dtype):
    assert snps_df["chr"].unique().shape[0] == 1
    chromosome = snps_df["chr"].unique()[0]

    snps_ids = list(set(snps_df["varID"]).intersection(variants_ids_with_genotype))
    chromosome_file = get_reference_panel_file(reference_panel_dir, f"chr{chromosome}.variants")
    snps_genotypes = pd.read_parquet(chromosome_file, columns=snps_ids)

    return covariance(snps_genotypes, cov_dtype)


def cov(
        reference_panel: str = typer.Option(..., help="Reference panel such as 1000G or GTEX_V8"),
        eqtl_model: str = typer.Option(..., help="Prediction models such as MASHR or ELASTIC_NET"),
        covariance_matrix_dtype: str = typer.Option("float64",
                                                    help="The numpy dtype used for the covariance matrix, either float64 or float32")
):
    """
    Computes the covariance for each chromosome of all variants present in prediction models.
    """

    assert reference_panel is not None and len(reference_panel) > 0, "A reference panel must be given"
    print(f"Reference panel: {reference_panel}")

    reference_panel_dir = conf.PHENOMEXCAN["LD_BLOCKS"][f"{reference_panel}_GENOTYPE_DIR"]
    print(f"Using reference panel folder: {str(reference_panel_dir)}")
    assert reference_panel_dir.exists(), "Reference panel folder does not exist"

    assert eqtl_model is not None and len(eqtl_model) > 0, "A prediction/eQTL model must be given"
    eqtl_model_files_prefix = conf.PHENOMEXCAN["PREDICTION_MODELS"][f"{eqtl_model}_PREFIX"]
    print(f"Using eQTL model: {eqtl_model} / {eqtl_model_files_prefix}")

    output_dir_base = (
            conf.RESULTS["GLS"]
            / "gene_corrs"
            / "reference_panels"
            / reference_panel.lower()
            / eqtl_model.lower()
    )
    output_dir_base.mkdir(parents=True, exist_ok=True)
    print(f"Using output dir base: {output_dir_base}")

    cov_dtype_dict = {
        "float32": np.float32,
        "float64": np.float64,
    }

    cov_dtype = cov_dtype_dict.get(covariance_matrix_dtype, np.float64)
    print(f"Covariance matrix dtype used: {str(cov_dtype)}")

    mashr_models_db_files = list(conf.PHENOMEXCAN["PREDICTION_MODELS"][eqtl_model].glob("*.db"))
    assert len(mashr_models_db_files) == 49

    all_variants_ids = []

    for m in mashr_models_db_files:
        print(f"Processing {m.name}")
        tissue = m.name.split(eqtl_model_files_prefix)[1].split(".db")[0]

        with sqlite3.connect(m) as conn:
            df = pd.read_sql("select gene, varID from weights", conn)
            df["gene"] = df["gene"].apply(lambda x: x.split(".")[0])
            df = df.assign(tissue=tissue)

            all_variants_ids.append(df)

    all_gene_snps = pd.concat(all_variants_ids, ignore_index=True)
    all_snps_in_models = set(all_gene_snps["varID"].unique())

    multiplier_z = pd.read_pickle(conf.MULTIPLIER["MODEL_Z_MATRIX_FILE"])
    variants_metadata = pd.read_parquet(get_reference_panel_file(reference_panel_dir, "_metadata"), columns=["id"])
    variants_ids_with_genotype = set(variants_metadata["id"])

    n_snps_in_models = len(all_snps_in_models)
    n_snps_in_ref_panel = len(all_snps_in_models.intersection(variants_ids_with_genotype))
    print(f"Number of SNPs in models: {n_snps_in_models}")
    print(f"Number of SNPs in reference panel: {n_snps_in_ref_panel}")
    print(f"Fraction of SNPs in reference panel: {n_snps_in_ref_panel / n_snps_in_models}")

    genes_in_z = [
        Gene(name=gene_name).ensembl_id
        for gene_name in multiplier_z.index
        if gene_name in Gene.GENE_NAME_TO_ID_MAP
    ]
    genes_in_z = set(genes_in_z)
    all_gene_snps = all_gene_snps[all_gene_snps["gene"].isin(genes_in_z)]

    all_snps_in_models_multiplier = set(all_gene_snps["varID"])
    n_snps_in_models = len(all_snps_in_models_multiplier)
    n_snps_in_ref_panel = len(all_snps_in_models_multiplier.intersection(variants_ids_with_genotype))
    print(f"Number of SNPs in models (MultiPLIER genes): {n_snps_in_models}")
    print(f"Number of SNPs in reference panel (MultiPLIER genes): {n_snps_in_ref_panel}")
    print(f"Fraction of SNPs in reference panel (MultiPLIER genes): {n_snps_in_ref_panel / n_snps_in_models}")

    variants_ld_block_df = all_gene_snps[["varID"]].drop_duplicates()
    variants_info = variants_ld_block_df["varID"].str.split("_", expand=True)
    variants_ld_block_df = variants_ld_block_df.join(variants_info)[["varID", 0, 1, 2, 3]]
    variants_ld_block_df = variants_ld_block_df.rename(
        columns={
            0: "chr",
            1: "position",
            2: "ref_allele",
            3: "eff_allele",
        }
    )
    variants_ld_block_df["chr"] = variants_ld_block_df["chr"].apply(lambda x: int(x[3:]))
    variants_ld_block_df["position"] = variants_ld_block_df["position"].astype(int)

    output_file_name_template = conf.PHENOMEXCAN["LD_BLOCKS"]["GENE_CORRS_FILE_NAME_TEMPLATES"]["SNPS_COVARIANCE"]
    output_file = output_dir_base / output_file_name_template.format(prefix="", suffix="")
    print(f"Output file: {output_file}")

    with pd.HDFStore(output_file, mode="w", complevel=4) as store:
        pbar = tqdm(
            variants_ld_block_df.groupby("chr"),
            ncols=100,
            total=variants_ld_block_df["chr"].unique().shape[0],
        )

        store["metadata"] = variants_ld_block_df

        for grp_name, grp_data in pbar:
            pbar.set_description(f"{grp_name} {grp_data.shape}")
            snps_cov = compute_snps_cov(grp_data, reference_panel_dir, variants_ids_with_genotype, cov_dtype)
            assert not snps_cov.isna().any().any()
            store[f"chr{grp_name}"] = snps_cov

            del snps_cov
            store.flush()

            gc.collect()