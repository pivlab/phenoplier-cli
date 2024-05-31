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

@cmd_group_run.command()
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

if __name__ == "__main__":
    app()
