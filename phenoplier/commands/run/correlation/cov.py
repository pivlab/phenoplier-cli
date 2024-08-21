import gc
import sqlite3
from pathlib import Path
from typing import Annotated

import pandas as pd
import numpy as np
import typer
from tqdm import tqdm
from rich import print
import os

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.commands.util.enums import MatrixDtype, RefPanel, EqtlModel
from phenoplier.constants.cli import Corr_Cov_Args as Args


def get_reference_panel_file(directory: Path, file_pattern: str) -> Path:
    print()
    print(f"Looking for reference panel file in {str(directory)} with pattern {file_pattern}")
    files = list(directory.glob(f"*{file_pattern}*.parquet"))
    if len(files) != 1:
        raise ValueError(f"Only ONE reference panel file is expected, but {len(files)} were found: {files}")
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
        reference_panel:            Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model:                 Annotated[EqtlModel, Args.EQTL_MODEL.value],
        multiplier_z_path:          Annotated[Path, Args.MULTIPLIER_Z.value] = None,
        covariance_matrix_dtype:    Annotated[MatrixDtype, Args.COVARIANCE_MATRIX_DTYPE.value] = MatrixDtype.f64,
        project_dir:                Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
        output_dir:                 Annotated[Path, Args.OUTPUT_DIR.value] = None,
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
    if not output_dir:
        output_dir_base = (
                Path(conf.RESULTS["GLS"])
                / "gene_corrs"
                / "reference_panels"
                / reference_panel.lower()
                / eqtl_model.lower()
        )
    else:
        output_dir_base = output_dir
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
    
    # Gett SNPs in predictions models
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
    print(f"Gene SNPs shape:{os.linesep}{all_gene_snps.shape}")
    print(f"First 5 rows of gene SNPs:{os.linesep}{all_gene_snps.head()}")
    all_snps_in_models = set(all_gene_snps["varID"].unique())

    # MultiPLIER Z
    multiplier_z = pd.read_pickle(multiplier_z_path or conf.GENE_MODULE_MODEL["MODEL_Z_MATRIX_FILE"])
    print(f"Using multiplier z:{os.linesep}{conf.GENE_MODULE_MODEL["MODEL_Z_MATRIX_FILE"]}")
    print(f"Model Z shape:{os.linesep}{multiplier_z.shape}")
    print(f"First 5 rows of model Z:{os.linesep}{multiplier_z.head()}")

    # Reference panel variants metadata
    ref_panel_input = get_reference_panel_file(reference_panel_dir, "_metadata")
    print(f"Reading reference panel metadata from: {ref_panel_input}")
    variants_metadata = pd.read_parquet(ref_panel_input, columns=["id"])
    print(f"Variants metadata shape:{os.linesep}{variants_metadata.shape}")
    print(f"First 5 rows of variants metadata:{os.linesep}{variants_metadata.head()}")
    variants_ids_with_genotype = set(variants_metadata["id"])
    print(f"Number of variants in reference panel:{os.linesep}{len(variants_ids_with_genotype)}")
    print(f"First 10 variants in reference panel:{os.linesep}{list(variants_ids_with_genotype)[:10]}")

    # How many variants in predictions models are present in the reference panel?
    n_snps_in_models = len(all_snps_in_models)
    n_snps_in_ref_panel = len(all_snps_in_models.intersection(variants_ids_with_genotype))
    print(f"Number of SNPs in models: {n_snps_in_models}")
    print(f"Number of SNPs in reference panel: {n_snps_in_ref_panel}")
    print(f"Fraction of SNPs in reference panel: {n_snps_in_ref_panel / n_snps_in_models}")

    # Get final list of genes in MultiPLIER
    genes_in_z = [
        Gene(name=gene_name).ensembl_id
        for gene_name in multiplier_z.index
        if gene_name in Gene.GENE_NAME_TO_ID_MAP()
    ]
    print(f"First 5 genes in the MultiPLIER Z model:{os.linesep}{genes_in_z[:5]}")
    print(f"Number of genes in the MultiPLIER Z model:{os.linesep}{len(genes_in_z)}")
    genes_in_z = set(genes_in_z)
    # keep genes in MultiPLIER only
    print(f"All gene SNPs shape:{os.linesep}{all_gene_snps.shape}")
    all_gene_snps = all_gene_snps[all_gene_snps["gene"].isin(genes_in_z)]
    print(f"Keeping only genes in MultiPLIER Z model:{os.linesep}{all_gene_snps.shape}")

    # (For MultiPLIER genes): How many variants in predictions models are present in the reference panel?
    all_snps_in_models_multiplier = set(all_gene_snps["varID"])
    n_snps_in_models = len(all_snps_in_models_multiplier)
    n_snps_in_ref_panel = len(all_snps_in_models_multiplier.intersection(variants_ids_with_genotype))
    print(f"Number of SNPs in models (MultiPLIER genes): {n_snps_in_models}")
    print(f"Number of SNPs in reference panel (MultiPLIER genes): {n_snps_in_ref_panel}")
    print(f"Fraction of SNPs in reference panel (MultiPLIER genes): {n_snps_in_ref_panel / n_snps_in_models}")

    # Preprocess SNPs data
    variants_ld_block_df = all_gene_snps[["varID"]].drop_duplicates()
    variants_info = variants_ld_block_df["varID"].str.split("_", expand=True)
    print(f"Variants info (raw) shape:{os.linesep}{variants_info.shape}")
    # validate data
    if not variants_ld_block_df.shape[0] == variants_info.shape[0]:
        raise ValueError("Dataframes do not have the same number of rows")
    variants_ld_block_df = variants_ld_block_df.join(variants_info)[["varID", 0, 1, 2, 3]]
    # validate data again
    if not variants_ld_block_df.shape[0] == variants_info.shape[0]:
        raise ValueError("Dataframes do not have the same number of rows")
    print(f"First 5 rows of variants info (raw):{os.linesep}{variants_info.head()}")

    variants_ld_block_df = variants_ld_block_df.rename(
        columns={
            0: "chr",
            1: "position",
            2: "ref_allele",
            3: "eff_allele",
        }
    )
    variants_ld_block_df["chr"] = variants_ld_block_df["chr"].apply(lambda x: int(x[3:]))
    print(f"Variants info (processed) shape:{os.linesep}{variants_info.shape}")
    variants_ld_block_df["position"] = variants_ld_block_df["position"].astype(int)
    print(f"First 5 rows of variants info (processed):{os.linesep}{variants_ld_block_df.head()}")

    # Compute covariance for each chromosome block
    # ad-hoc tests
    _tmp_snps = variants_ld_block_df[variants_ld_block_df["chr"] == 22]
    if not _tmp_snps.shape[0] > 0:
        raise ValueError("No SNPs for chromosome 22")
    n_expected = len(set(_tmp_snps["varID"]).intersection(variants_ids_with_genotype))
    _tmp = compute_snps_cov(_tmp_snps, reference_panel_dir, variants_ids_with_genotype, cov_dtype)
    if not _tmp.shape == (n_expected, n_expected):
        raise ValueError("Unexpected shape")
    if _tmp.isna().any().any():
        raise ValueError("Unexpected NA values")
    del _tmp, _tmp_snps

    output_file_name_template = f"{conf.TWAS["LD_BLOCKS"]["OUTPUT_FILE_NAME"]}"
    output_file = output_dir_base / output_file_name_template.format(prefix="", suffix="")
    print(f"Output file: {output_file}")

    # Compute covariance and save
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
    if not _tmp.shape[0] > 0:
        raise ValueError("No SNPs for chromosome 1")
    n_expected = len(set(_tmp["varID"]).intersection(variants_ids_with_genotype))
    if not n_expected > 0:
        raise ValueError("No SNPs for chromosome 1")

    with pd.HDFStore(output_file, mode="r") as store:
        df = store["chr1"]
        if not df.shape == (n_expected, n_expected):
            raise ValueError("Unexpected shape")
        if df.isna().any().any():
            raise ValueError("Unexpected NA values")
 