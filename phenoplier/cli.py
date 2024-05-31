"""This module provides the command line interface for Phenoplier."""
import sys
import shutil
import logging
from typing import Optional, Annotated, List
from pathlib import Path
from enum import Enum

import typer
import pandas as pd
import numpy as np

from phenoplier.gls import GLSPhenoplier
from phenoplier.config import settings, SETTINGS_FILES
from phenoplier.cli_constants import RUN_GLS_ARGS, RUN_GLS_DEFAULTS, CLI, INIT


LOG_FORMAT = "%(levelname)s: %(message)s"

h1 = logging.StreamHandler(stream=sys.stdout)
h1.setLevel(logging.INFO)
h1.addFilter(lambda record: record.levelno <= logging.INFO)
h2 = logging.StreamHandler()
h2.setLevel(logging.WARNING)

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, handlers=[h1, h2])
logger = logging.getLogger("root")


# Define the main CLI program/command
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=True
)
# Define the subcommands
cmd_group_run = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Execute a specific Phenoplier pipeline."
)
cmd_group_gene_corr = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Execute a specific Phenoplier pipeline for gene-gene correlation matrix generation."
)
cmd_group_run.add_typer(cmd_group_gene_corr, name="gene-corr")
app.add_typer(cmd_group_run, name="run")


# Callbacks in Typer allows us to create "--" options for the main program/command
def version_callback(value: bool) -> None:
    """Callback for the --version option."""
    if value:
        typer.echo(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        raise typer.Exit()


@app.callback()
def main(
        version: Annotated[bool, typer.Option("--version", "-v", help=CLI["version"], callback=version_callback)] = False
        # verbose: bool = False,
        # debug: bool = False
) -> None:
    """
    Phenopliler CLI

    \n
    PhenoPLIER is a flexible computational framework that combines gene-trait and gene-drug associations with gene\n
    modules expressed in specific contexts (see Figure above). The approach uses a latent representation (with latent\n
    variables or LVs representing gene modules) derived from a large gene expression compendium to integrate TWAS\n
    with drug-induced transcriptional responses for a joint analysis. The approach consists in three main components:

    \n
    1. an LV-based regression model to compute an association between an LV and a trait,\n
    2. a clustering framework to learn groups of traits with shared transcriptomic properties, and\n
    3. an LV-based drug repurposing approach that links diseases to potential treatments.\n

    \n
    For more details, check out our article in Nature Communications (https://doi.org/10.1038/s41467-023-41057-4)\n
    or our Manubot web version (https://greenelab.github.io/phenoplier_manuscript/). To cite PhenoPLIER,\n
    see 10.1038/s41467-023-41057-4:

    \n
    Projecting genetic associations through gene expression patterns highlights disease etiology and drug mechanisms\n
    Pividori, M., Lu, S., Li, B. et al.\n
    Nat Commun 14, 5562 (2023) https://doi.org/gspsxr\n
    DOI: 10.1038/s41467-023-41057-4\n

    \n
    Interested in using PhenoPLIER? Any questions? Check out our Discussions section (\n
    https://github.com/greenelab/phenoplier/discussions) and start a discussion by asking a question or sharing your\n
    thoughts. We are happy to help!
    """
    return


def create_settings_files(directory: Path) -> None:
    Path(directory).mkdir(parents=True, exist_ok=True)
    for file_name in SETTINGS_FILES:
        settings_file = Path(directory) / file_name
        if settings_file.exists():
            typer.echo(f"Config file {str(file_name)} already exists at {directory}")
        else:
            template_file = Path(__file__).parent / "templates" / file_name
            shutil.copy2(template_file, settings_file)
            print(f"Config file {str(file_name)} created at {directory}")


def remove_settings_files(directory: Path) -> None:
    for file_name in SETTINGS_FILES:
        settings_file = Path(directory) / file_name
        if settings_file.exists():
            settings_file.unlink()
            print(f"Config file {str(file_name)} removed from {directory}")


def check_settings_files(directory: Path) -> None:
    for file_name in SETTINGS_FILES:
        settings_file = Path(directory) / file_name
        if not settings_file.exists():
            raise typer.BadParameter(f"Config file {str(file_name)} does not exist at {directory}. Please run 'phenoplier init' first.")


def load_settings_files(directory: Path, more_files: List[Path] = []) -> None:
    """
    Load the settings files from the specified directory. The expected side effect is that after this function is called,
    settings defined in the toml config files will be available as attributes of the settings object.
    :param directory: The directory where the settings files are located.
    :param more_files: A list of settings files other than the default ones to load. Those files should be also in
    the same directory as the default settings file.
    """

    # Check if the directory exists
    if not directory.exists():
        raise typer.BadParameter(f"Provided config directory does not exist: {directory}")
    # Check if the settings files exist in the directory
    check_settings_files(directory)
    # Load the default settings
    for file_name in SETTINGS_FILES:
        settings_file = directory / file_name
        if settings_file.exists():
            settings.load_file(settings_file)
            print(f"Config file {str(file_name)} loaded from {directory}")
        else:
            raise typer.BadParameter(f"Config file {str(file_name)} does not exist at {directory}.")
    # Load the additional settings
    for curr_dir_file in more_files:
        file = directory / curr_dir_file
        if not file.exists():
            raise typer.BadParameter(f"Config file {str(file)} does not exist at {directory}.")
        settings_file = directory / file
        settings.load_file(settings_file)
        print(f"Additional config file {str(file)} loaded from {directory}")


# TODO: Add a prompt to ask the user if they want to overwrite the existing settings file
@app.command()
def init(
        project_dir: Annotated[str, typer.Option("--project-dir", "-p", help=INIT["project_dir"])] = settings.CURRENT_DIR
):
    """
    Initialize settings file and necessary data in the specified directory.
    """
    create_settings_files(Path(project_dir))


# TODO: use Enum istesad of callbakcs for typer
def run_gls_model_callback(model: str) -> None:
    """
    Callback for the --model option.
    """
    if model not in ["gls", "ols"]:
        raise typer.BadParameter("Model must be either 'gls' or 'ols'")
    return


def run_gls_gene_corr_mode_callback(mode: str) -> None:
    """
    Callback for the --mode option.
    """
    if mode not in ["sub", "full"]:
        raise typer.BadParameter("Mode must be either 'sub' or 'full'")
    return


COVAR_OPTIONS = [
    "all",
    "gene_size",
    "gene_size_log",
    "gene_density",
    "gene_density_log",
    "gene_n_snps_used",
    "gene_n_snps_used_log",
    "gene_n_snps_used_density",
    "gene_n_snps_used_density_log",
]

COVAR_OPTIONS_DEFAULT = [
    "gene_size",
    "gene_size_log",
    "gene_density",
    "gene_density_log",
]

# Subset of covariates taht need SNP-level information
SNPLEVEL_COVAR_OPTIONS_PREFIXES = [
    "gene_n_snps_used",
    "gene_n_snps_used_density",
]

class DUP_GENE_ACTIONS(str, Enum):
    keep_first = "keep-first"
    keep_last = "keep-last"
    remove_all = "remove-all"

class REGRESSION_MODEL(str, Enum):
    gls = "gls"
    ols = "ols"

class GENE_CORREALATION_MODE(str, Enum):
    sub = "sub"
    full = "full"

def check_config_files(dir: str) -> None:
    for file_name in SETTINGS_FILES:
        settings_file = Path(dir) / file_name
        if not settings_file.exists():
            raise typer.BadParameter(f"Config file {str(file_name)} does not exist at {dir}. Please run 'phenoplier init' first.")


@cmd_group_run.command()
def regression(
        input_file:             Annotated[Path, typer.Option("--input-file", "-i", help=RUN_GLS_ARGS["input_file"])],
        output_file:            Annotated[Path, typer.Option("--output-file", "-o", help=RUN_GLS_ARGS["output_file"])],
        project_dir:            Annotated[str, typer.Option("--project-dir", "-p", help=RUN_GLS_ARGS["project_dir"])] = settings.CURRENT_DIR,
        model:                  Annotated[REGRESSION_MODEL, typer.Option("--model", help=RUN_GLS_ARGS["model"])] = REGRESSION_MODEL.gls,
        gene_corr_file:         Annotated[Optional[Path], typer.Option("--gene-corr-file", "-f", help=RUN_GLS_ARGS["gene_corr_file"])] = None,
        gene_corr_mode:         Annotated[GENE_CORREALATION_MODE, typer.Option("--gene-corr-mode", "-m", help=RUN_GLS_ARGS["debug_use_sub_corr"])] = GENE_CORREALATION_MODE.sub,
        dup_genes_action:       Annotated[DUP_GENE_ACTIONS, typer.Option("--dup-genes-action", help=RUN_GLS_ARGS["dup_genes_action"])] = DUP_GENE_ACTIONS.keep_first,
        covars:                 Annotated[Optional[str], typer.Option("--covars", "-c", help=RUN_GLS_ARGS["covars"])] = None,
        cohort_metadata_dir:    Annotated[Optional[str], typer.Option("--cohort-name", "-n", help=RUN_GLS_ARGS["cohort_metadata_dir"])] = None,
        lv_list:                Annotated[Optional[List[str]], typer.Option("--lv-list", help=RUN_GLS_ARGS["lv_list"])] = None,
        lv_model_file:          Annotated[Optional[Path], typer.Option("--lv-model-file", help=RUN_GLS_ARGS["lv_model_file"])] = None,
        batch_id:               Annotated[Optional[int], typer.Option("--batch-id", help=RUN_GLS_ARGS["batch_id"])] = None,
        batch_n_splits:         Annotated[Optional[int], typer.Option("--batch-n-splits", help=RUN_GLS_ARGS["batch_n_splits"])] = None,
) -> None:
    """
    Run the Generalized Least Squares (GLS) model by default. Note that you need to run "phenoplier init" first to set up the environment.
    """
    def check_batch_args():
        if lv_list and (batch_id is not None or batch_n_splits is not None):
            raise typer.BadParameter("Incompatible parameters: LV list and batches cannot be used together")
        
        if (batch_id is not None and batch_n_splits is None) or (
            batch_id is None and batch_n_splits is not None
        ):
            raise typer.BadParameter(
                "Both --batch-id and --batch-n-splits have to be provided (not only one of them)"
            )

        if batch_id is not None and batch_id < 1:
            raise typer.BadParameter("--batch-id must be >= 1")

        if (
            batch_id is not None
            and batch_n_splits is not None
            and batch_id > batch_n_splits
        ):
            typer.BadParameter("--batch-id must be <= --batch-n-splits")

    def check_output_file():
        if output_file.exists():
            typer.BadParameter(f"Skipping, output file exists: {str(output_file)}")

        if not output_file.parent.exists():
            typer.BadParameter(
                f"Parent directory of output file does not exist: {str(output_file.parent)}"
            )
            
    def read_input():
        data = pd.read_csv(input_file, sep="\t")
        logger.info(f"Input file has {data.shape[0]} genes")

        if "gene_name" not in data.columns:
            logger.error("Mandatory columns not present in data 'gene_name'")
            sys.exit(1)

        if "pvalue" not in data.columns:
            logger.error("Mandatory columns not present in data 'pvalue'")
            sys.exit(1)

        data = data.set_index("gene_name")
        return data
    
    def remove_dup_gene_entries(input_data):
        if dup_genes_action.startswith("keep"):
            keep_action = dup_genes_action.split("-")[1]
        elif dup_genes_action == "remove-all":
            keep_action = False
        else:
            raise ValueError("Wrong --dup-gene-action value")
        logger.info(
            f"Removed duplicated genes symbols using '{dup_genes_action}'. "
            f"Data now has {input_data.shape[0]} genes"
        )
        return input_data.loc[~input_data.index.duplicated(keep=keep_action)], keep_action

    # Check arguments
    check_batch_args()
    check_output_file()

    # Load config files
    load_settings_files(Path(project_dir))

    # TODO: Put error messages in constants.messages as dict kv paris
    # Check if both "debug_use_ols" and "gene_corr_file" are None
    if model != "ols" and gene_corr_file is None:
        raise typer.BadParameter("When not using --model=ols, option '--gene-corr-file <value>' must be provided")
    # and they should not be both provided
    if model == "ols" and gene_corr_file is not None:
        # Todo: can print a message to tell the user that the gene_corr_file will be ignored
        raise typer.BadParameter("When using '--model=ols', option '--gene-corr-file <value>' should not be provided")

    # Print out useful information
    covars_info = (
        f"Using DEFAULT covariates: {RUN_GLS_DEFAULTS["covars"]}" if covars == "default"
        else f"Using covariates {covars}" if covars
        else f"Running {model} without covariates."
    )
    print("[blue][Info]: " + covars_info)

    data = read_input()
    data, keep_action = remove_dup_gene_entries(data)
    # unique index (gene names)
    if not data.index.is_unique:
        logger.error(
            "Duplicated genes in input data. Use option --dup-gene-action "
            "if you want to skip them."
        )
        sys.exit(1)

    # pvalues statistics
    _data_pvalues = data["pvalue"]
    n_missing = _data_pvalues.isna().sum()
    n = _data_pvalues.shape[0]
    min_pval = _data_pvalues.min()
    mean_pval = _data_pvalues.mean()
    max_pval = _data_pvalues.max()

    logger.info(
        f"p-values statistics: min={min_pval:.1e} | mean={mean_pval:.1e} | max={max_pval:.1e} | # missing={n_missing} ({(n_missing / n) * 100:.1f}%)"
    )

    if min_pval < 0.0:
        logger.warning("Some p-values are smaller than 0.0")

    if max_pval > 1.0:
        logger.warning("Some p-values are greater than 1.0")

    final_data = data.loc[:, ["pvalue"]].rename(
        columns={
            "pvalue": "y",
        }
    )
    
    # add covariates (if specified)
    if covars is not None:
        covars_selected = str.split(covars, " ")
        print("Covars selected: ", covars)

        if "all" in covars_selected:
            covars_selected = [c for c in COVAR_OPTIONS if c != "all"]

        if "default" in covars_selected:
            covars_selected = COVAR_OPTIONS_DEFAULT

        covars_selected = sorted(covars_selected)

        logger.info(f"Using covariates: {covars_selected}")

        # get necessary columns from results
        covars = data[["pvalue", "n", "n_indep"]]
        covars = covars.rename(
            columns={
                "n_indep": "gene_size",
            }
        )

        if "gene_density" in covars_selected:
            covars = covars.assign(
                gene_density=covars.apply(lambda x: x["gene_size"] / x["n"], axis=1)
            )

        # process snp-level covariates
        if any(
            c.startswith(snplevel_c)
            for c in covars_selected
            for snplevel_c in SNPLEVEL_COVAR_OPTIONS_PREFIXES
        ):
            # first load the cohort metadata gene tissues file
            if cohort_metadata_dir is None:
                logger.error(
                    "To use SNP-level covariates, a cohort metadata folder must "
                    "be provided (--cohort-metadata-dir)"
                )
                sys.exit(1)

            cohort_metadata_dir = Path(cohort_metadata_dir).resolve()
            cohort_gene_tissues_filepath = cohort_metadata_dir / "gene_tissues.pkl"
            if not cohort_gene_tissues_filepath.exists():
                cohort_gene_tissues_filepath = cohort_gene_tissues_filepath.with_suffix(
                    ".pkl.gz"
                )
                assert cohort_gene_tissues_filepath.exists(), (
                    f"No gene_tissues.pkl[.gz] exists in cohort metadata folder: "
                    f"{cohort_metadata_dir}"
                )

            logger.info(f"Loading cohort metadata: {str(cohort_gene_tissues_filepath)}")
            cohort_gene_tissues = pd.read_pickle(
                cohort_gene_tissues_filepath
            ).set_index("gene_name")
            # remove duplicated gene names
            if not cohort_gene_tissues.index.is_unique:
                if dup_genes_action is None:
                    logger.error(
                        "There are duplicated gene names in cohort metadat files, --dup-gene-action must be specified"
                    )
                    sys.exit(1)

                cohort_gene_tissues = cohort_gene_tissues.loc[
                    ~cohort_gene_tissues.index.duplicated(keep=keep_action)
                ]

            common_genes = final_data.index.intersection(cohort_gene_tissues.index)
            cohort_gene_tissues = cohort_gene_tissues.loc[common_genes]

            # check individual covariates
            if "gene_n_snps_used" in covars_selected:
                covars = covars.assign(
                    gene_n_snps_used=cohort_gene_tissues["n_snps_used_sum"]
                )

            if "gene_n_snps_used_density" in covars_selected:
                covars = covars.assign(
                    gene_n_snps_used_density=cohort_gene_tissues.apply(
                        lambda x: x["n_snps_used_sum"] / x["unique_n_snps_used"],
                        axis=1,
                    )
                )

        # add log versions of covariates (if specified)
        for c in covars_selected:
            if c.endswith("_log"):
                c_prefix = c.split("_log")[0]

                if c_prefix not in covars.columns:
                    logger.error(
                        f"If log version of covar is selected, covar has to be "
                        f"selected as well ({c_prefix} not present)"
                    )
                    sys.exit(1)

                covars[c] = np.log(covars[c_prefix])
                if "density" in c_prefix:
                    covars[c] = -1 * covars[c]

        final_data = pd.concat([final_data, covars[covars_selected]], axis=1)

    # convert p-values
    logger.info("Replacing zero p-values by nonzero minimum divided by 10")
    min_nonzero_pvalue = final_data[final_data["y"] > 0]["y"].min() / 10.0
    final_data["y"] = final_data["y"].replace(0, min_nonzero_pvalue)

    logger.info("Using -log10(pvalue)")
    final_data["y"] = -np.log10(final_data["y"])

    if final_data.shape[1] == 1:
        final_data = final_data.squeeze().rename(input_file.stem)

    if model == "ols" and gene_corr_file is not None:
        logger.error(
            "Incompatible arguments: you cannot specify both "
            "--gene-corr-file and --debug-use-ols"
        )
        sys.exit(1)

    if gene_corr_file is not None:
        logger.info(f"Using gene correlation file: {gene_corr_file}")

    if lv_model_file is not None:
        lv_model_file = Path(lv_model_file)
        logger.info(f"Reading LV model file: {str(lv_model_file)}")
        full_lvs_list = GLSPhenoplier._get_lv_weights(lv_model_file).columns.tolist()
    else:
        full_lvs_list = GLSPhenoplier._get_lv_weights().columns.tolist()

    if batch_n_splits is not None and batch_n_splits > len(full_lvs_list):
        logger.error(
            f"--batch-n-splits cannot be greater than LVs in the model "
            f"({len(full_lvs_list)} LVs)"
        )
        sys.exit(2)

    full_lvs_set = set(full_lvs_list)
    logger.info(f"{len(full_lvs_set)} LVs (gene modules) were found in LV model")

    if lv_list:
        selected_lvs = [lv for lv in lv_list if lv in full_lvs_set]
        logger.info(
            f"A list of {len(lv_list)} LVs was provided, and {len(selected_lvs)} "
            f"are present in LV models"
        )
    else:
        selected_lvs = full_lvs_list
        logger.info("All LVs in models will be used")

    if batch_id is not None and batch_n_splits is not None:
        selected_lvs_chunks = [
            ar.tolist() for ar in np.array_split(selected_lvs, batch_n_splits)
        ]
        selected_lvs = selected_lvs_chunks[batch_id - 1]
        logger.info(
            f"Using batch {batch_id} out of {batch_n_splits} ({len(selected_lvs)} LVs selected)"
        )

    if len(selected_lvs) == 0:
        logger.error("No LVs were selected")
        sys.exit(1)

    # create model object
    model = GLSPhenoplier(
        gene_corrs_file_path=gene_corr_file,
        debug_use_ols=True if model == "ols" else False,
        debug_use_sub_gene_corr=True if gene_corr_mode == "sub" else False,
        use_own_implementation=True,
        logger=logger,
    )

    results = []

    # compute an association between each LV and the gene-trait associations
    for lv_idx, lv_code in enumerate(selected_lvs):
        logger.info(f"Computing for {lv_code}")

        # show warnings or logs only in the first run
        if lv_idx == 0:
            model.set_logger(logger)
        elif lv_idx == 1:
            model.set_logger(None)

        model.fit_named(lv_code, final_data)

        res = model.results

        results.append(
            {
                "lv": lv_code,
                "beta": res.params.loc["lv"],
                "beta_se": res.bse.loc["lv"],
                "t": res.tvalues.loc["lv"],
                "pvalue_twosided": res.pvalues.loc["lv"],
                "pvalue_onesided": res.pvalues_onesided.loc["lv"],
            }
        )

    # create final dataframe and save
    results = pd.DataFrame(results).set_index("lv").sort_values("pvalue_onesided")
    logger.info(f"Writing results to {str(output_file)}")
    results.to_csv(output_file, sep="\t", na_rep="NA")


# SECTION BEGINS
# Gene-Gene Correlation Matrix
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

@cmd_group_gene_corr.command()
def cov4chr(
    reference_panel: str = typer.Option(..., help="Reference panel such as 1000G or GTEX_V8"),
    eqtl_model: str = typer.Option(..., help="Prediction models such as MASHR or ELASTIC_NET"),
    covariance_matrix_dtype: str = typer.Option("float64", help="The numpy dtype used for the covariance matrix, either float64 or float32")
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

# SECTION ENDS


@cmd_group_gene_corr.command()
def preprocess(
    cohort_name: str,
    reference_panel: str,
    eqtl_model: str,
    gwas_file: str,
    spredixcan_folder: str,
    spredixcan_file_pattern: str,
    smultixcan_file: str,
):
    """
    Compiles information about the GWAS and TWAS for a particular cohort. For example, the set of GWAS variants, variance of predicted expression of genes, etc.
    """
    
    # Cohort name processing
    cohort_name = cohort_name.lower()
    typer.echo(f"Cohort name: {cohort_name}")

    # Reference panel processing
    typer.echo(f"Reference panel: {reference_panel}")

    # GWAS file processing
    gwas_file_path = Path(gwas_file).resolve()
    if not gwas_file_path.exists():
        raise typer.BadParameter(f"GWAS file does not exist: {gwas_file_path}")
    typer.echo(f"GWAS file path: {gwas_file_path}")

    # S-PrediXcan folder processing
    spredixcan_folder_path = Path(spredixcan_folder).resolve()
    if not spredixcan_folder_path.exists():
        raise typer.BadParameter(f"S-PrediXcan folder does not exist: {spredixcan_folder_path}")
    typer.echo(f"S-PrediXcan folder path: {spredixcan_folder_path}")

    # S-PrediXcan file pattern processing
    if "{tissue}" not in spredixcan_file_pattern:
        raise typer.BadParameter("S-PrediXcan file pattern must have a '{tissue}' placeholder")
    typer.echo(f"S-PrediXcan file template: {spredixcan_file_pattern}")

    # S-MultiXcan file processing
    smultixcan_file_path = Path(smultixcan_file).resolve()
    if not smultixcan_file_path.exists():
        raise typer.BadParameter(f"S-MultiXcan result file does not exist: {smultixcan_file_path}")
    typer.echo(f"S-MultiXcan file path: {smultixcan_file_path}")

    # EQTL model processing
    typer.echo(f"eQTL model: {eqtl_model}")

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

    # Load MultiPLIER Z genes
    multiplier_z_genes = pd.read_pickle(conf.MULTIPLIER["MODEL_Z_MATRIX_FILE"]).index.tolist()
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

    # TWAS data processing
    prediction_model_tissues = conf.PHENOMEXCAN["PREDICTION_MODELS"][f"{eqtl_model}_TISSUES"].split(" ")

    smultixcan_results = pd.read_csv(
        smultixcan_file_path, sep="\t", usecols=["gene", "gene_name", "pvalue", "n", "n_indep"]
    ).dropna().assign(gene_id=lambda x: x["gene"].apply(lambda g: g.split(".")[0]))

    common_genes = set(multiplier_z_genes).intersection(set(smultixcan_results["gene_name"]))
    multiplier_gene_obj = {gene_name: Gene(name=gene_name) for gene_name in common_genes if gene_name in Gene.GENE_NAME_TO_ID_MAP}

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

    spredixcan_result_files = {t: spredixcan_folder_path / spredixcan_file_pattern.format(tissue=t) for t in prediction_model_tissues}
    spredixcan_dfs = pd.concat([
        pd.read_csv(f, usecols=["gene", "zscore", "pvalue", "n_snps_used", "n_snps_in_model"]).dropna(subset=["gene", "zscore", "pvalue"]).assign(tissue=t)
        for t, f in spredixcan_result_files.items()
    ])
    spredixcan_dfs = spredixcan_dfs.assign(gene_id=lambda x: x["gene"].apply(lambda g: g.split(".")[0]))
    spredixcan_dfs = spredixcan_dfs[spredixcan_dfs["gene_id"].isin(set(genes_info["id"]))]

    spredixcan_genes_n_models = spredixcan_dfs.groupby("gene_id")["tissue"].nunique()
    spredixcan_genes_models = spredixcan_dfs.groupby("gene_id")["tissue"].apply(lambda x: frozenset(x.tolist()))
    spredixcan_genes_models = spredixcan_genes_models.to_frame().reset_index()
    spredixcan_genes_models = spredixcan_genes_models.assign(gene_name=spredixcan_genes_models["gene_id"].apply(lambda g: Gene.GENE_ID_TO_NAME_MAP[g]))
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
    spredixcan_genes_models = spredixcan_genes_models.join(spredixcan_genes_tissues_pc_variance.rename("tissues_pc_variances"))

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
    spredixcan_genes_models = spredixcan_genes_models.join(spredixcan_genes_tissues_variance.rename("tissues_variances"))

    spredixcan_genes_sum_of_n_snps_used = spredixcan_dfs.groupby("gene_id")["n_snps_used"].sum().rename("n_snps_used_sum")
    spredixcan_genes_models = spredixcan_genes_models.join(spredixcan_genes_sum_of_n_snps_used)

    spredixcan_genes_sum_of_n_snps_in_model = spredixcan_dfs.groupby("gene_id")["n_snps_in_model"].sum().rename("n_snps_in_model_sum")
    spredixcan_genes_models = spredixcan_genes_models.join(spredixcan_genes_sum_of_n_snps_in_model)

    spredixcan_genes_models.to_pickle(output_dir_base / "spredixcan_tissues_variances.pkl")


## SECTION BEGINS
## Gene Expression Correlation
@cmd_group_gene_corr.command()
def correlate(
    cohort_name: str = typer.Option(..., help="Cohort name (e.g., UK_BIOBANK)"),
    reference_panel: str = typer.Option(..., help="Reference panel such as 1000G or GTEX_V8"),
    eqtl_model: str = typer.Option(..., help="Prediction/eQTL model such as MASHR or ELASTIC_NET"),
    smultixcan_condition_number: int = typer.Option(30, help="S-MultiXcan condition number"),
    chromosome: int = typer.Option(..., help="Chromosome number (1-22)"),
    compute_correlations_within_distance: bool = typer.Option(False, help="Compute correlations within distance"),
    debug_mode: bool = typer.Option(False, help="Debug mode")
):
    """
    Computes predicted expression correlations between all genes in the MultiPLIER models.
    """
    
    warnings.filterwarnings("error")
    
    assert cohort_name and reference_panel and eqtl_model, "All input parameters must be provided"
    assert 1 <= chromosome <= 22, "Chromosome must be between 1 and 22"
    
    cohort_name = cohort_name.lower()
    eqtl_model_files_prefix = conf.PHENOMEXCAN["PREDICTION_MODELS"][f"{eqtl_model}_PREFIX"]
    
    output_dir_base = (
        conf.RESULTS["GLS"]
        / "gene_corrs"
        / "cohorts"
        / cohort_name
        / reference_panel.lower()
        / eqtl_model.lower()
    )
    output_dir_base.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir_base / "gwas_variant_ids.pkl", "rb") as handle:
        gwas_variants_ids_set = pickle.load(handle)

    spredixcan_genes_models = pd.read_pickle(output_dir_base / "gene_tissues.pkl")
    genes_info = pd.read_pickle(output_dir_base / "genes_info.pkl")
    
    output_dir = output_dir_base / "by_chr"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_file = output_dir / f"gene_corrs-chr{chromosome}.pkl"
    
    all_chrs = genes_info["chr"].dropna().unique()
    assert all_chrs.shape[0] == 22 and chromosome in all_chrs
    
    genes_chr = genes_info[genes_info["chr"] == chromosome].sort_values("start_position")
    gene_chr_objs = [Gene(ensembl_id=gene_id) for gene_id in genes_chr["id"]]
    
    n = len(gene_chr_objs)
    n_comb = n + int(n * (n - 1) / 2.0)
    
    gene_corrs = []
    gene_corrs_data = np.full((n, n), np.nan, dtype=np.float64)

    with tqdm(ncols=100, total=n_comb) as pbar:
        for gene1_idx in range(0, len(gene_chr_objs)):
            gene1_obj = gene_chr_objs[gene1_idx]
            gene1_tissues = spredixcan_genes_models.loc[gene1_obj.ensembl_id, "tissue"]

            for gene2_idx in range(gene1_idx, len(gene_chr_objs)):
                gene2_obj = gene_chr_objs[gene2_idx]
                gene2_tissues = spredixcan_genes_models.loc[gene2_obj.ensembl_id, "tissue"]

                pbar.set_description(f"{gene1_obj.ensembl_id} / {gene2_obj.ensembl_id}")

                try:
                    r = gene1_obj.get_ssm_correlation(
                        other_gene=gene2_obj,
                        tissues=gene1_tissues,
                        other_tissues=gene2_tissues,
                        snps_subset=gwas_variants_ids_set,
                        condition_number=smultixcan_condition_number,
                        reference_panel=reference_panel,
                        model_type=eqtl_model,
                        use_within_distance=compute_correlations_within_distance,
                    )

                    if r is None:
                        r = 0.0

                    gene_corrs.append(r)
                    gene_corrs_data[gene1_idx, gene2_idx] = r
                    gene_corrs_data[gene2_idx, gene1_idx] = r
                except Warning as e:
                    if not debug_mode:
                        raise e

                    print(
                        f"RuntimeWarning for genes {gene1_obj.ensembl_id} and {gene2_obj.ensembl_id}",
                        flush=True,
                    )
                    print(traceback.format_exc(), flush=True)

                    gene_corrs.append(np.nan)
                except Exception as e:
                    if not debug_mode:
                        raise e

                    print(
                        f"Exception for genes {gene1_obj.ensembl_id} and {gene2_obj.ensembl_id}",
                        flush=True,
                    )
                    print(traceback.format_exc(), flush=True)

                    gene_corrs.append(np.nan)

                pbar.update(1)

    gene_corrs_flat = pd.Series(gene_corrs)
    gene_chr_ids = [g.ensembl_id for g in gene_chr_objs]
    gene_corrs_df = pd.DataFrame(
        data=gene_corrs_data,
        index=gene_chr_ids,
        columns=gene_chr_ids,
    )

    gene_corrs_df.to_pickle(output_file)

    try:
        chol_mat = np.linalg.cholesky(gene_corrs_df.to_numpy())
        cov_inv = np.linalg.inv(chol_mat)
        print("Works!")
    except Exception as e:
        print(f"Cholesky decomposition failed: {str(e)}")

    try:
        cholsigmainv = np.linalg.cholesky(np.linalg.inv(gene_corrs_df.to_numpy())).T
        print("Works!")
    except Exception as e:
        print(f"Cholesky decomposition failed (statsmodels.GLS): {str(e)}")


def validate_inputs(cohort_name, reference_panel, eqtl_model):
    assert cohort_name is not None and len(cohort_name) > 0, "A cohort name must be given"
    assert reference_panel is not None and len(reference_panel) > 0, "A reference panel must be given"
    assert eqtl_model is not None and len(eqtl_model) > 0, "A prediction/eQTL model must be given"
    return cohort_name.lower(), reference_panel, eqtl_model

@cmd_group_gene_corr.command()
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


@cmd_group_gene_corr.command()
def filter(
    cohort_name: str = typer.Option(..., help="Cohort name, e.g., UK_BIOBANK"),
    reference_panel: str = typer.Option(..., help="Reference panel, e.g., 1000G or GTEX_V8"),
    eqtl_model: str = typer.Option(..., help="Prediction/eQTL model, e.g., MASHR or ELASTIC_NET"),
    distances: list[float] = typer.Option([10, 5, 2], help="List of distances to generate correlation matrices for")
):
    """
    Reads the correlation matrix generated and creates new matrices with different "within distances" across genes.
    For example, it generates a new correlation matrix with only genes within a distance of 10mb.
    """
    def validate_inputs(cohort_name, reference_panel, eqtl_model):
        assert cohort_name is not None and len(cohort_name) > 0, "A cohort name must be given"
        assert reference_panel is not None and len(reference_panel) > 0, "A reference panel must be given"
        assert eqtl_model is not None and len(eqtl_model) > 0, "A prediction/eQTL model must be given"
        return cohort_name.lower(), reference_panel, eqtl_model

    cohort_name, reference_panel, eqtl_model = validate_inputs(cohort_name, reference_panel, eqtl_model)
    
    output_dir_base = (
        conf.RESULTS["GLS"]
        / "gene_corrs"
        / "cohorts"
        / cohort_name
        / reference_panel.lower()
        / eqtl_model.lower()
    )
    assert output_dir_base.exists(), f"Output directory {output_dir_base} does not exist"
    typer.echo(f"Using output dir base: {output_dir_base}")

    gene_corrs = pd.read_pickle(output_dir_base / "gene_corrs-symbols.pkl")
    gene_objs = [Gene(name=gene_name) for gene_name in gene_corrs.index]

    for full_distance in distances:
        distance = full_distance / 2.0
        typer.echo(f"Using within distance: {distance}")

        genes_within_distance = np.eye(len(gene_objs)).astype(bool)
        for g0_idx in range(len(gene_objs) - 1):
            g0_obj = gene_objs[g0_idx]
            for g1_idx in range(g0_idx + 1, len(gene_objs)):
                g1_obj = gene_objs[g1_idx]
                genes_within_distance[g0_idx, g1_idx] = g0_obj.within_distance(g1_obj, distance * 1e6)
                genes_within_distance[g1_idx, g0_idx] = genes_within_distance[g0_idx, g1_idx]

        genes_within_distance = pd.DataFrame(
            genes_within_distance, index=gene_corrs.index.copy(), columns=gene_corrs.columns.copy()
        )

        gene_corrs_within_distance = gene_corrs[genes_within_distance].fillna(0.0)

        is_pos_def = check_pos_def(gene_corrs_within_distance)
        if not is_pos_def:
            typer.echo("Fixing non-positive definite matrix...")
            gene_corrs_within_distance = adjust_non_pos_def(gene_corrs_within_distance)
            assert check_pos_def(gene_corrs_within_distance), "Could not adjust gene correlation matrix"

        gene_corrs_within_distance.to_pickle(
            output_dir_base / f"gene_corrs-symbols-within_distance_{int(full_distance)}mb.pkl"
        )

        genes_corrs_sum = gene_corrs_within_distance.sum()
        n_genes_included = genes_corrs_sum[genes_corrs_sum > 1.0].shape[0]
        genes_corrs_nonzero_sum = (gene_corrs_within_distance > 0.0).astype(int).sum().sum()

        typer.echo(f"Number of genes with correlations with other genes: {n_genes_included}")
        typer.echo(f"Number of nonzero cells: {genes_corrs_nonzero_sum}")

        corr_matrix_flat = gene_corrs_within_distance.mask(
            np.triu(np.ones(gene_corrs_within_distance.shape)).astype(bool)
        ).stack()
        typer.echo(corr_matrix_flat.describe().apply(str))


@cmd_group_gene_corr.command()
def generate(
    cohort_name: str = typer.Option(..., help="Cohort name, e.g., UK_BIOBANK"),
    reference_panel: str = typer.Option(..., help="Reference panel, e.g., 1000G or GTEX_V8"),
    eqtl_model: str = typer.Option(..., help="Prediction/eQTL model, e.g., MASHR or ELASTIC_NET"),
    lv_code: str = typer.Option(..., help="The code of the latent variable (LV) to compute the correlation matrix for"),
    lv_percentile: float = typer.Option(None, help="A number from 0.0 to 1.0 indicating the top percentile of the genes in the LV to keep")
):
    """
    Computes an LV-specific correlation matrix by using the top genes in that LV only.
    """
    def validate_inputs(cohort_name, reference_panel, eqtl_model, lv_code, lv_percentile):
        assert cohort_name is not None and len(cohort_name) > 0, "A cohort name must be given"
        assert reference_panel is not None and len(reference_panel) > 0, "A reference panel must be given"
        assert eqtl_model is not None and len(eqtl_model) > 0, "A prediction/eQTL model must be given"
        assert lv_code is not None and len(lv_code) > 0, "An LV code must be given"
        if lv_percentile is not None:
            lv_percentile = float(lv_percentile)
        return cohort_name.lower(), reference_panel.lower(), eqtl_model.lower(), lv_code, lv_percentile

    cohort_name, reference_panel, eqtl_model, lv_code, lv_percentile = validate_inputs(cohort_name, reference_panel, eqtl_model, lv_code, lv_percentile)

    OUTPUT_DIR_BASE = conf.RESULTS["GLS"] / "gene_corrs" / "cohorts" / cohort_name / reference_panel / eqtl_model
    gene_corrs_dict = {f.name: pd.read_pickle(f) for f in OUTPUT_DIR_BASE.glob("gene_corrs-symbols*.pkl")}

    def exists_df(output_dir, base_filename):
        full_filepath = output_dir / (base_filename + ".npz")
        return full_filepath.exists()

    def store_df(output_dir, nparray, base_filename):
        if base_filename in ("metadata", "gene_names"):
            np.savez_compressed(output_dir / (base_filename + ".npz"), data=nparray)
        else:
            sparse.save_npz(output_dir / (base_filename + ".npz"), sparse.csc_matrix(nparray), compressed=False)

    def get_output_dir(gene_corr_filename):
        path = OUTPUT_DIR_BASE / gene_corr_filename
        assert path.exists()
        return path.with_suffix(".per_lv")

    def compute_chol_inv(lv_code):
        for gene_corr_filename, gene_corrs in gene_corrs_dict.items():
            output_dir = get_output_dir(gene_corr_filename)
            output_dir.mkdir(parents=True, exist_ok=True)

            lv_data = multiplier_z[lv_code]
            corr_mat_sub = GLSPhenoplier.get_sub_mat(gene_corrs, lv_data, lv_percentile)
            store_df(output_dir, corr_mat_sub.to_numpy(), f"{lv_code}_corr_mat")

            chol_mat = np.linalg.cholesky(corr_mat_sub)
            chol_inv = np.linalg.inv(chol_mat)
            store_df(output_dir, chol_inv, lv_code)

            if not exists_df(output_dir, "metadata"):
                metadata = np.array([reference_panel, eqtl_model])
                store_df(output_dir, metadata, "metadata")

            if not exists_df(output_dir, "gene_names"):
                gene_names = np.array(gene_corrs.index.tolist())
                store_df(output_dir, gene_names, "gene_names")

    lvs_chunks = [[lv_code]]

    with ProcessPoolExecutor(max_workers=1) as executor, tqdm(total=len(lvs_chunks), ncols=100) as pbar:
        tasks = [executor.submit(compute_chol_inv, chunk) for chunk in lvs_chunks]
        for future in as_completed(tasks):
            res = future.result()
            pbar.update(1)

if __name__ == "__main__":
    app()
