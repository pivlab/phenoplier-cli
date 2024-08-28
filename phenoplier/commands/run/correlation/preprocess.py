from pathlib import Path
from typing import Annotated

import pandas as pd
import numpy as np
import typer
import pickle
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from phenoplier.config import settings as conf
from phenoplier.entity import Gene
from phenoplier.commands.util.utils import load_settings_files, get_model_tissue_names
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.arg import Corr_Preprocess_Args as Args


# Todo: Validate reference_panel, check if folder exists. Or change it to a path argument?
def preprocess(
        cohort:                     Annotated[Cohort, Args.COHORT_NAME.value],
        reference_panel:            Annotated[RefPanel, Args.REFERENCE_PANEL.value],
        eqtl_model:                 Annotated[EqtlModel, Args.EQTL_MODEL.value],
        gwas_file:                  Annotated[Path, Args.GWAS_FILE.value],
        spredixcan_folder:          Annotated[Path, Args.SPREDIXCAN_FOLDER.value],
        spredixcan_file_pattern:    Annotated[str, Args.SPREDIXCAN_FILE_PATTERN.value],
        smultixcan_file:            Annotated[Path, Args.SMULTIXCAN_FILE.value],
        multiplier_z_path:          Annotated[Path, Args.MULTIPLIER_Z.value] = None,
        project_dir:                Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
        output_dir:                 Annotated[Path, Args.OUTPUT_DIR.value] = None,
):
    """
    Compiles information about the GWAS and TWAS for a particular cohort. For example, the set of GWAS variants, variance of predicted expression of genes, etc.
    """

    load_settings_files(project_dir)

    print(Text("[--- Info ---]", style="blue"))

    # Cohort name processing
    cohort = cohort.lower()
    print(f"Cohort name: {cohort}")

    # Reference panel processing
    reference_panel = reference_panel.lower()
    print(f"Reference panel: {reference_panel}")

    # GWAS file processing
    gwas_file_path = gwas_file.resolve()
    if not gwas_file_path.exists():
        raise typer.BadParameter(f"GWAS file does not exist: {gwas_file_path}")
    print(f"GWAS file path: {gwas_file_path}")

    # S-PrediXcan folder processing
    spredixcan_folder_path = spredixcan_folder.resolve()
    if not spredixcan_folder_path.exists():
        raise typer.BadParameter(f"S-PrediXcan folder does not exist: {spredixcan_folder_path}")
    print(f"S-PrediXcan folder path: {spredixcan_folder_path}")

    # S-PrediXcan file pattern processing
    if "{tissue}" not in spredixcan_file_pattern:
        raise typer.BadParameter("S-PrediXcan file pattern must have a '{tissue}' placeholder")
    print(f"S-PrediXcan file template: {spredixcan_file_pattern}")

    # S-MultiXcan file processing
    smultixcan_file_path = smultixcan_file.resolve()
    if not smultixcan_file_path.exists():
        raise typer.BadParameter(f"S-MultiXcan result file does not exist: {smultixcan_file_path}")
    print(f"S-MultiXcan file path: {smultixcan_file_path}")

    # EQTL model processing
    eqtl_model = eqtl_model.value
    print(f"eQTL model: {eqtl_model}")

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

    # Data Loading
    print(Text("[--- Data Loading ---]", style="blue"))
    # Load MultiPLIER Z genes
    multiplier_z = pd.read_pickle(multiplier_z_path or conf.GENE_MODULE_MODEL["MODEL_Z_MATRIX_FILE"])
    # multiplier_z = pd.DataFrame.from_dict(multiplier_z['data'])
    print(f"Loading MultiPLIER Z genes from: {conf.GENE_MODULE_MODEL['MODEL_Z_MATRIX_FILE']}")
    multiplier_z_genes = multiplier_z.index.tolist()
    if len(multiplier_z_genes) != len(set(multiplier_z_genes)):
        raise ValueError("MultiPLIER Z genes have duplicates.")
    print(f"Done. Number of MultiPLIER Z genes: {len(multiplier_z_genes)}")

    # GWAS data processing
    print(f"Loading GWAS data from: {gwas_file_path}")
    gwas_data = pd.read_csv(
        gwas_file_path,
        sep="\t",
        usecols=["panel_variant_id", "pvalue", "zscore"],
    ).dropna()  # remove SNPs with no results
    # Save GWAS variants
    gwas_variants_ids_set = frozenset(gwas_data["panel_variant_id"])
    output_file = output_dir_base / "gwas_variant_ids.pkl.gz"

    import gzip
    with gzip.open(output_file, "wb") as handle:
        pickle.dump(gwas_variants_ids_set, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"GWAS variant IDs saved to: {output_file}")

    # TWAS data processing
    # obtain tissue information
    prediction_model_tissues = get_model_tissue_names(eqtl_model)
    print(f"Loading smultixcan file: {smultixcan_file_path}")
    # read S-MultiXcan results
    smultixcan_results = pd.read_csv(
        smultixcan_file_path, sep="\t", usecols=["gene", "gene_name", "pvalue", "n", "n_indep"]
    ).dropna().assign(gene_id=lambda x: x["gene"].apply(lambda g: g.split(".")[0]))
    print("Done.")

    # Data Processing
    # global spredixcan_genes_models
    # global spredixcan_gene_obj

    print(Text("[--- Data Processing ---]", style="blue"))
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task(description="Processing gene information...", total=None)
        # Process gene information
        common_genes = set(multiplier_z_genes).intersection(set(smultixcan_results["gene_name"]))
        multiplier_gene_obj = {gene_name: Gene(name=gene_name) for gene_name in common_genes if
                               gene_name in Gene.GENE_NAME_TO_ID_MAP()}

        assert multiplier_gene_obj["GAS6"].ensembl_id == "ENSG00000183087"

        _gene_obj = list(multiplier_gene_obj.values())
        genes_info = pd.DataFrame({
            "name": [g.name for g in _gene_obj],
            "id": [g.ensembl_id for g in _gene_obj],
            "chr": [g.chromosome for g in _gene_obj],
            "band": [g.band for g in _gene_obj],
            "start_position": [g.get_attribute("start_position") for g in _gene_obj],
            "end_position": [g.get_attribute("end_position") for g in _gene_obj],
        }).assign(gene_length=lambda x: x["end_position"] - x["start_position"]).dropna()

        genes_info["chr"] = genes_info["chr"].apply(pd.to_numeric, downcast="integer")
        genes_info["start_position"] = genes_info["start_position"].astype(int)
        genes_info["end_position"] = genes_info["end_position"].astype(int)
        genes_info["gene_length"] = genes_info["gene_length"].astype(int)

        # check correctness
        if not genes_info["name"].is_unique:
            raise ValueError("genes_info has duplicate names.")
        if not genes_info["id"].is_unique:
            raise ValueError("genes_info has duplicate ids.")

        # sort by chromosomes
        genes_info.sort_values("chr")
        # output results
        output_file = output_dir_base / "genes_info.pkl"
        genes_info.to_pickle(output_file)
    print(f"Done. Gene information saved in: {output_file}")

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task(description="Loading S-PrediXcan results...", total=None)
        # Load S-PrediXcan results
        spredixcan_result_files = {t: spredixcan_folder_path / spredixcan_file_pattern.format(tissue=t) for t in
                                   prediction_model_tissues}
        # check on input
        if not len(spredixcan_result_files) == len(prediction_model_tissues):
            raise ValueError("Length of spredixcan_result_files not equal to that of prediction_model_tissues.")

        spredixcan_dfs = pd.concat([
            pd.read_csv(f, usecols=["gene", "zscore", "pvalue", "n_snps_used", "n_snps_in_model"]).dropna(
                subset=["gene", "zscore", "pvalue"]).assign(tissue=t)
            for t, f in spredixcan_result_files.items()
        ])
        # check on dfs
        # if not len(spredixcan_dfs) == len(prediction_model_tissues):
            # raise ValueError()

        spredixcan_dfs = spredixcan_dfs.assign(gene_id=lambda x: x["gene"].apply(lambda g: g.split(".")[0]))
        # leave only common genes
        spredixcan_dfs = spredixcan_dfs[spredixcan_dfs["gene_id"].isin(set(genes_info["id"]))]
        spredixcan_genes_n_models = spredixcan_dfs.groupby("gene_id")["tissue"].nunique()

        # checks
        _tmp_smultixcan_results_n_models = (
            smultixcan_results.set_index("gene_id")["n"].astype(int).rename("tissue")
        )
        _cg = _tmp_smultixcan_results_n_models.index.intersection(
            spredixcan_genes_n_models.index
        )
        _tmp_smultixcan_results_n_models = _tmp_smultixcan_results_n_models.loc[_cg]
        _spredixcan = spredixcan_genes_n_models.loc[_cg]
        if not _spredixcan.shape[0] == _tmp_smultixcan_results_n_models.shape[0]:
            raise ValueError()
        if not _spredixcan.equals(_tmp_smultixcan_results_n_models.loc[_spredixcan.index]):
            raise ValueError()

        # get tissues available per gene
        spredixcan_genes_models = spredixcan_dfs.groupby("gene_id")["tissue"].apply(lambda x: frozenset(x.tolist()))
        # checks
        if not spredixcan_genes_n_models.shape[0] == spredixcan_genes_models.shape[0]:
            raise ValueError()
        if not spredixcan_genes_n_models.index.equals(spredixcan_genes_models.index):
            raise ValueError()
        if not (spredixcan_genes_models.apply(len) <= len(prediction_model_tissues)).all():
            raise ValueError()
        if not (spredixcan_genes_models.loc[spredixcan_genes_n_models.index]
                .apply(len).equals(spredixcan_genes_n_models)):
            raise ValueError()

        # Add gene name and set index
        spredixcan_genes_models = spredixcan_genes_models.to_frame().reset_index()
        spredixcan_genes_models = spredixcan_genes_models.assign(
            gene_name=spredixcan_genes_models["gene_id"].apply(lambda g: Gene.GENE_ID_TO_NAME_MAP()[g]))
        spredixcan_genes_models = spredixcan_genes_models[["gene_id", "gene_name", "tissue"]].set_index("gene_id")
        # Add number of tissues
        spredixcan_genes_models = spredixcan_genes_models.assign(n_tissues=spredixcan_genes_models["tissue"].apply(len))
        # check on output
        if not spredixcan_genes_models["gene_name"].is_unique:
            raise ValueError("spredixcan_genes_models has duplicate names.")
        if spredixcan_genes_models.isna().any().any():
            raise ValueError("spredixcan_genes_models has NaN values.")
        # save output
        spredixcan_genes_models.to_pickle(output_dir_base / "gene_tissues.pkl")

    print("Done")

    # Add this check
    if spredixcan_genes_models is None or spredixcan_genes_models.empty:
        raise ValueError("spredixcan_genes_models is None or empty. Check if it was properly initialized.")

    def _get_gene_pc_variance(gene_row):
        """
        Add genes' variance captured by principal components
        """
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

    # Add covariates based on S-PrediXcan results. This extends the previous file with more columns
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task(description="Adding covariates based on S-PrediXcan results (this step takes some time)...", total=None)
        # Get gene's objects
        spredixcan_gene_obj = {gene_id: Gene(ensembl_id=gene_id) for gene_id in spredixcan_genes_models.index}

        # Add genes' variance captured by principal components
        try:
            spredixcan_genes_tissues_pc_variance = spredixcan_genes_models.apply(_get_gene_pc_variance, axis=1)
        except Exception as e:
            print(f"Error occurred while applying _get_gene_pc_variance: {str(e)}")
            print(f"spredixcan_genes_models shape: {spredixcan_genes_models.shape}")
            print(f"spredixcan_genes_models columns: {spredixcan_genes_models.columns}")
            raise

        # add to spredixcan_genes_models
        spredixcan_genes_models = spredixcan_genes_models.join(
            spredixcan_genes_tissues_pc_variance.rename("tissues_pc_variances"))

        # Add gene variance per tissue
        spredixcan_genes_tissues_variance = spredixcan_genes_models.apply(_get_gene_variances, axis=1)
        # data validation
        if not spredixcan_genes_tissues_variance.loc["ENSG00000000419"]:
            raise ValueError()
        # add to spredixcan_genes_models
        spredixcan_genes_models = spredixcan_genes_models.join(
            spredixcan_genes_tissues_variance.rename("tissues_variances"))

        # Count number of SNPs predictors used across tissue models
        spredixcan_genes_sum_of_n_snps_used = spredixcan_dfs.groupby("gene_id")["n_snps_used"].sum().rename(
            "n_snps_used_sum")
        # add sum of snps used to spredixcan_genes_models
        spredixcan_genes_models = spredixcan_genes_models.join(
            spredixcan_genes_sum_of_n_snps_used
        )

        # Count number of SNPs predictors in models across tissue models
        spredixcan_genes_sum_of_n_snps_in_model = (
            spredixcan_dfs.groupby("gene_id")["n_snps_in_model"]
            .sum()
            .rename("n_snps_in_model_sum")
        )
        # add sum of snps in model to spredixcan_genes_models
        spredixcan_genes_models = spredixcan_genes_models.join(
            spredixcan_genes_sum_of_n_snps_in_model
        )
    print("Done")

    # Summarize prediction models for each gene
    def _summarize_gene_models(gene_id):
        """
        For a given gene ID, it returns a dataframe with predictor SNPs in rows and tissues in columns, where
        values are the weights of SNPs in those tissues.
        It can contain NaNs.
        """
        gene_obj = spredixcan_gene_obj[gene_id]
        gene_tissues = spredixcan_genes_models.loc[gene_id, "tissue"]

        gene_models = {}
        gene_unique_snps = set()
        for t in gene_tissues:
            gene_model = gene_obj.get_prediction_weights(tissue=t, model_type=eqtl_model)
            gene_models[t] = gene_model

            gene_unique_snps.update(set(gene_model.index))

        df = pd.DataFrame(
            data=np.nan, index=list(gene_unique_snps), columns=list(gene_tissues)
        )

        for t in df.columns:
            for snp in df.index:
                gene_model = gene_models[t]

                if snp in gene_model.index:
                    df.loc[snp, t] = gene_model.loc[snp]

        return df

    print(Text("[--- Result Generation ---]", style="blue"))
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task(description="Summarizing prediction models for each gene ...", total=None)

        gene_models = {}
        for gene_id in spredixcan_genes_models.index:
            gene_models[gene_id] = _summarize_gene_models(gene_id)
        # save results
        import gzip
        output_file = output_dir_base / "gene_tissues_models.pkl.gz"
        with gzip.GzipFile(output_file, "w") as f:
            pickle.dump(gene_models, f)
        # validate output
        with gzip.GzipFile(output_file, "r") as f:
            _tmp = pickle.load(f)
        if not len(gene_models) == len(_tmp):
            raise ValueError()
        if not gene_models["ENSG00000000419"].equals(_tmp["ENSG00000000419"]):
            raise ValueError()

    print(f"Done. Gene tissues models saved in: {output_file}")

    # Count number of unique SNPs predictors used and available across tissue models
    def _count_unique_snps(gene_id):
        """
        For a gene_id, it counts unique SNPs in all models and their intersection with GWAS SNPs (therefore, used by S-PrediXcan).
        """
        gene_tissues = spredixcan_genes_models.loc[gene_id, "tissue"]

        gene_unique_snps = set()
        for t in gene_tissues:
            t_snps = set(gene_models[gene_id].index)
            gene_unique_snps.update(t_snps)

        gene_unique_snps_in_gwas = gwas_variants_ids_set.intersection(gene_unique_snps)

        return pd.Series(
            {
                "unique_n_snps_in_model": len(gene_unique_snps),
                "unique_n_snps_used": len(gene_unique_snps_in_gwas),
            }
        )

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task(description="Counting number of unique SNPs predictors used and available across tissue "
                                      "models ...", total=None)

        # get unique snps for all genes
        spredixcan_genes_unique_n_snps = spredixcan_genes_models.groupby("gene_id").apply(
            lambda x: _count_unique_snps(x.name)
        )

        if not (
                spredixcan_genes_unique_n_snps["unique_n_snps_in_model"]
                >= spredixcan_genes_unique_n_snps["unique_n_snps_used"]
        ).all():
            raise ValueError(
                "Number of unique SNPs in the model must be greater than or equal to the number of unique SNPs used.")
        # add unique snps to spredixcan_genes_models
        spredixcan_genes_models = spredixcan_genes_models.join(spredixcan_genes_unique_n_snps)
        # save
        # this is important, other scripts depend on gene_name to be unique
        if not spredixcan_genes_models["gene_name"].is_unique:
            raise ValueError("Duplicate gene names found.")
        if spredixcan_genes_models.isna().any().any():
            raise ValueError("NaN values found")

        output_file = output_dir_base / "gene_tissues.pkl"
        spredixcan_genes_models.to_pickle(output_file)
    print(f"Done. Gene tissues saved in: {output_file}")
