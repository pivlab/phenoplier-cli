import gc
import sqlite3
from pathlib import Path
from enum import Enum
from typing import Annotated

import pandas as pd
import numpy as np
import typer
from tqdm import tqdm
from rich import print

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.utils import load_settings_files


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


class RefPanel(str, Enum):
    _1000g = "1000G"
    gtex_v8 = "GTEX_V8"


class EqtlModel(str, Enum):
    mashr = "MASHR"
    elastic_net = "ELASTIC_NET"


class MatrixDtype(str, Enum):
    f32 = "float32"
    f64 = "float64"


def cov(
        reference_panel: Annotated[RefPanel, typer.Option("--reference-panel", "-r", help="Reference panel such as 1000G or GTEX_V8")],
        eqtl_model: Annotated[EqtlModel, typer.Option("--eqtl-model", "-m", help="Prediction models such as MASHR or ELASTIC_NET")],
        covariance_matrix_dtype: Annotated[MatrixDtype, typer.Option("--covariance-matrix-dtype", "-t", help="The numpy dtype used for the covariance matrix.")] = "float64",
        project_dir: Annotated[
            Path, typer.Option("--project-dir", "-p", help="Project directory")] = conf.CURRENT_DIR,
):
    """
    Computes the covariance for each chromosome of all variants present in prediction models.
    """
    # Check project directory
    load_settings_files(project_dir)
    reference_panel = reference_panel.value
    eqtl_model = eqtl_model.value
    covariance_matrix_dtype = covariance_matrix_dtype.value

    # Check reference panel folder
    reference_panel_dir = Path(conf.TWAS["LD_BLOCKS"][f"{reference_panel}_GENOTYPE_DIR"])
    if not reference_panel_dir.exists():
        raise typer.BadParameter(f"Reference panel folder does not exist: {str(reference_panel_dir)}")
    print(f"Using reference panel folder: {str(reference_panel_dir)}")
    # Process eQTL model input
    eqtl_model_files_prefix = conf.TWAS["PREDICTION_MODELS"][f"{eqtl_model}_PREFIX"]
    print(f"Using eQTL model: {eqtl_model} / {eqtl_model_files_prefix}")
    # Set up output directory
    output_dir_base = (
            Path(conf.RESULTS["GLS"])
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

    mashr_models_db_files = list(Path(conf.TWAS["PREDICTION_MODELS"][eqtl_model]).glob("*.db"))
    # Check number of MASHR models
    NUM_MAX_FILES = 49
    if len(mashr_models_db_files) != NUM_MAX_FILES:
        raise ValueError(f"Number of MASHR models is not {NUM_MAX_FILES}: {len(mashr_models_db_files)}")
    

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

    multiplier_z = pd.read_pickle(conf.GENE_MODULE_MODEL["MODEL_Z_MATRIX_FILE"])
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
        if gene_name in Gene.GENE_NAME_TO_ID_MAP()
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

    # output_file_name_template = conf.TWAS["LD_BLOCKS"]["GENE_CORRS_FILE_NAME_TEMPLATES"]["SNPS_COVARIANCE"]
    # TODO: Ask Milton what is "GENE_CORRS_FILE_NAME_TEMPLATES"
    output_file_name_template = f"{conf.TWAS["LD_BLOCKS"]["BASE_DIR"]}/test/"
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

    # Ad-hot tests
    _tmp = variants_ld_block_df[variants_ld_block_df["chr"] == 1]
    assert _tmp.shape[0] > 0
    n_expected = len(set(_tmp["varID"]).intersection(variants_ids_with_genotype))
    assert n_expected > 0
    
    with pd.HDFStore(output_file, mode="r") as store:
        df = store["chr1"]
        assert df.shape == (n_expected, n_expected)
        assert not df.isna().any().any()