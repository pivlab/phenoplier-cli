from pathlib import Path
from typing import Annotated

import pandas as pd
import typer
import pickle

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.utils import load_settings_files, get_model_tissue_names
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.cli import Corr_Preprocess_Args as Args


def preprocess(
        cohort_name:                Annotated[Cohort, Args.COHORT_NAME.value],
        gwas_file:                  Annotated[Path, Args.GWAS_FILE.value],
        spredixcan_folder:          Annotated[Path, Args.SPREDIXCAN_FOLDER.value],
        spredixcan_file_pattern:    Annotated[str, Args.SPREDIXCAN_FILE_PATTERN.value],
        smultixcan_file:            Annotated[Path, Args.SMULTIXCAN_FILE.value],
        reference_panel:            Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model:                 Annotated[EqtlModel, Args.EQTL_MODEL.value],
        project_dir:                Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
):
    """
    Compiles information about the GWAS and TWAS for a particular cohort. For example, the set of GWAS variants, variance of predicted expression of genes, etc.
    """

    load_settings_files(project_dir)

    # Cohort name processing
    cohort_name = cohort_name.lower()
    typer.echo(f"Cohort name: {cohort_name}")

    # Reference panel processing
    reference_panel = reference_panel.lower()
    typer.echo(f"Reference panel: {reference_panel}")

    # GWAS file processing
    gwas_file_path = gwas_file.resolve()
    if not gwas_file_path.exists():
        raise typer.BadParameter(f"GWAS file does not exist: {gwas_file_path}")
    typer.echo(f"GWAS file path: {gwas_file_path}")

    # S-PrediXcan folder processing
    spredixcan_folder_path = spredixcan_folder.resolve()
    if not spredixcan_folder_path.exists():
        raise typer.BadParameter(f"S-PrediXcan folder does not exist: {spredixcan_folder_path}")
    typer.echo(f"S-PrediXcan folder path: {spredixcan_folder_path}")

    # S-PrediXcan file pattern processing
    if "{tissue}" not in spredixcan_file_pattern:
        raise typer.BadParameter("S-PrediXcan file pattern must have a '{tissue}' placeholder")
    typer.echo(f"S-PrediXcan file template: {spredixcan_file_pattern}")

    # S-MultiXcan file processing
    smultixcan_file_path = smultixcan_file.resolve()
    if not smultixcan_file_path.exists():
        raise typer.BadParameter(f"S-MultiXcan result file does not exist: {smultixcan_file_path}")
    typer.echo(f"S-MultiXcan file path: {smultixcan_file_path}")

    # EQTL model processing
    eqtl_model = eqtl_model.value
    typer.echo(f"eQTL model: {eqtl_model}")

    output_dir_base = (
            Path(conf.RESULTS["GLS"])
            / "gene_corrs"
            / "cohorts"
            / cohort_name
            / reference_panel.lower()
            / eqtl_model.lower()
    )
    output_dir_base.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Using output dir base: {output_dir_base}")

    # Load MultiPLIER Z genes
    multiplier_z_genes = pd.read_pickle(conf.GENE_MODULE_MODEL["MODEL_Z_MATRIX_FILE"]).index.tolist()
    assert len(multiplier_z_genes) == len(set(multiplier_z_genes))

    # GWAS data processing
    gwas_data = pd.read_csv(
        gwas_file_path,
        sep="\t",
        usecols=["panel_variant_id", "pvalue", "zscore"],
    ).dropna()
    gwas_variants_ids_set = frozenset(gwas_data["panel_variant_id"])
    with open(output_dir_base / "gwas_variant_ids.pkl", "wb") as handle:
        pickle.dump(gwas_variants_ids_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Obtain tissue information
    prediction_model_tissues = get_model_tissue_names(eqtl_model)

    smultixcan_results = pd.read_csv(
        smultixcan_file_path, sep="\t", usecols=["gene", "gene_name", "pvalue", "n", "n_indep"]
    ).dropna().assign(gene_id=lambda x: x["gene"].apply(lambda g: g.split(".")[0]))

    common_genes = set(multiplier_z_genes).intersection(set(smultixcan_results["gene_name"]))
    multiplier_gene_obj = {gene_name: Gene(name=gene_name) for gene_name in common_genes if
                           gene_name in Gene.GENE_NAME_TO_ID_MAP()}

    genes_info = pd.DataFrame({
        "name": [g.name for g in multiplier_gene_obj.values()],
        "id": [g.ensembl_id for g in multiplier_gene_obj.values()],
        "chr": [g.chromosome for g in multiplier_gene_obj.values()],
        "band": [g.band for g in multiplier_gene_obj.values()],
        "start_position": [g.get_attribute("start_position") for g in multiplier_gene_obj.values()],
        "end_position": [g.get_attribute("end_position") for g in multiplier_gene_obj.values()],
    }).assign(gene_length=lambda x: x["end_position"] - x["start_position"]).dropna()

    genes_info["chr"] = genes_info["chr"].apply(pd.to_numeric, downcast="integer")
    genes_info["start_position"] = genes_info["start_position"].astype(int)
    genes_info["end_position"] = genes_info["end_position"].astype(int)
    genes_info["gene_length"] = genes_info["gene_length"].astype(int)
    genes_info.to_pickle(output_dir_base / "genes_info.pkl")

    spredixcan_result_files = {t: spredixcan_folder_path / spredixcan_file_pattern.format(tissue=t) for t in
                               prediction_model_tissues}
    # print(spredixcan_result_files)
    spredixcan_dfs = pd.concat([
        pd.read_csv(f, usecols=["gene", "zscore", "pvalue", "n_snps_used", "n_snps_in_model"]).dropna(
            subset=["gene", "zscore", "pvalue"]).assign(tissue=t)
        for t, f in spredixcan_result_files.items()
    ])
    spredixcan_dfs = spredixcan_dfs.assign(gene_id=lambda x: x["gene"].apply(lambda g: g.split(".")[0]))
    spredixcan_dfs = spredixcan_dfs[spredixcan_dfs["gene_id"].isin(set(genes_info["id"]))]

    spredixcan_genes_n_models = spredixcan_dfs.groupby("gene_id")["tissue"].nunique()
    spredixcan_genes_models = spredixcan_dfs.groupby("gene_id")["tissue"].apply(lambda x: frozenset(x.tolist()))
    spredixcan_genes_models = spredixcan_genes_models.to_frame().reset_index()
    spredixcan_genes_models = spredixcan_genes_models.assign(
        gene_name=spredixcan_genes_models["gene_id"].apply(lambda g: Gene.GENE_ID_TO_NAME_MAP()[g]))
    spredixcan_genes_models = spredixcan_genes_models[["gene_id", "gene_name", "tissue"]].set_index("gene_id")
    spredixcan_genes_models = spredixcan_genes_models.assign(n_tissues=spredixcan_genes_models["tissue"].apply(len))
    spredixcan_genes_models.to_pickle(output_dir_base / "gene_tissues.pkl")

    spredixcan_gene_obj = {gene_id: Gene(ensembl_id=gene_id) for gene_id in spredixcan_genes_models.index}

    def _get_gene_pc_variance(gene_row):
        gene_id = gene_row.name
        gene_tissues = gene_row["tissue"]
        gene_obj = spredixcan_gene_obj[gene_id]
        u, s, vt = gene_obj.get_tissues_correlations_svd(
            tissues=gene_tissues,
            snps_subset=gwas_variants_ids_set,
            reference_panel=reference_panel,
            model_type=eqtl_model,
        )
        return s

    spredixcan_genes_tissues_pc_variance = spredixcan_genes_models.apply(_get_gene_pc_variance, axis=1)
    spredixcan_genes_models = spredixcan_genes_models.join(
        spredixcan_genes_tissues_pc_variance.rename("tissues_pc_variances"))

    def _get_gene_variances(gene_row):
        gene_id = gene_row.name
        gene_tissues = gene_row["tissue"]
        tissue_variances = {}
        gene_obj = spredixcan_gene_obj[gene_id]
        for tissue in gene_tissues:
            tissue_var = gene_obj.get_pred_expression_variance(
                tissue=tissue,
                reference_panel=reference_panel,
                model_type=eqtl_model,
                snps_subset=gwas_variants_ids_set,
            )
            if tissue_var is not None:
                tissue_variances[tissue] = tissue_var
        return tissue_variances

    spredixcan_genes_tissues_variance = spredixcan_genes_models.apply(_get_gene_variances, axis=1)
    spredixcan_genes_models = spredixcan_genes_models.join(
        spredixcan_genes_tissues_variance.rename("tissues_variances"))

    spredixcan_genes_sum_of_n_snps_used = spredixcan_dfs.groupby("gene_id")["n_snps_used"].sum().rename(
        "n_snps_used_sum")
    spredixcan_genes_models = spredixcan_genes_models.join(spredixcan_genes_sum_of_n_snps_used)

    spredixcan_genes_sum_of_n_snps_in_model = spredixcan_dfs.groupby("gene_id")["n_snps_in_model"].sum().rename(
        "n_snps_in_model_sum")
    spredixcan_genes_models = spredixcan_genes_models.join(spredixcan_genes_sum_of_n_snps_in_model)

    spredixcan_genes_models.to_pickle(output_dir_base / "spredixcan_tissues_variances.pkl")
