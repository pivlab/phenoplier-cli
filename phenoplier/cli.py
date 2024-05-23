"""This module provides the command line interface for Phenoplier."""

import os
import sys
import typer
from enum import Enum
from typing import Optional, Annotated, List
from pathlib import Path
from rich import print
import pandas as pd
from . import gls_cli
from .config import settings
from .config import USER_SETTINGS_FILE
from .constants import RUN_GLS_ARGS, RUN_GLS_DEFAULTS, CLI
import logging


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


# TODO: Add a prompt to ask the user if they want to overwrite the existing settings file
@app.command()
def init(
        output_file: Annotated[
            str, typer.Option("--output-file", "-o",
             help="Path to output the initialized project files. Default to current shell directory.")] = settings.CURRENT_DIR
):
    """
    Initialize a user settings file in the home directory in TOML format.
    """
    raise NotImplementedError("This function is not implemented yet.")
    # def create_user_settings():
    #     settings_file = USER_SETTINGS_FILE
    #     if not settings_file.exists():
    #         settings = DEFAULT_USER_SETTINGS
    #         settings_file.parent.mkdir(parents=True, exist_ok=True)
    #         settings_file.write_text(tomlkit.dumps(settings))
    #         typer.echo("Config file created at " + str(settings_file) + ".")
    #     else:
    #         typer.echo("Config file already exists at " + str(settings_file) + ".")
    #
    # create_user_settings()


def activate(
        user_settings: Annotated[
            str, typer.Option("--user-settings", "-s", help="Path to the local user settings file")] = str(
            USER_SETTINGS_FILE),
):
    """
    Export the necessary environment variables derived from the user's setting file.
    """
    settings = Path(user_settings)
    if not settings.exists():
        raise typer.BadParameter(
            "User settings file does not exist at default location or not provided. Please run the init command first.")
    # Optionally, read settings here if needed for the function
    raise NotImplementedError("This function is not implemented yet.")


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


class DupGeneActions(str, Enum):
    keep_first = "keep-first"
    keep_last = "keep-last"
    remove_all = "remove-all"

@cmd_group_run.command()
def regression(
        input_file:         Annotated[str, typer.Option("--input-file", "-i", help=RUN_GLS_ARGS["input_file"])],
        output_file:        Annotated[str, typer.Option("--output-file", "-o", help=RUN_GLS_ARGS["output_file"])],
        model:              Annotated[str, typer.Option("--model", help=RUN_GLS_ARGS["model"], callback=run_gls_model_callback)] = "gls",
        gene_corr_file:     Annotated[Optional[str], typer.Option("--gene-corr-file", "-f", help=RUN_GLS_ARGS["gene_corr_file"])] = None,
        gene_corr_mode:     Annotated[str, typer.Option("--gene-corr-mode", "-m", help=RUN_GLS_ARGS["debug_use_sub_corr"])]       = "sub",
        dup_genes_action:   Annotated[DupGeneActions, typer.Option("--dup-genes-action", help=RUN_GLS_ARGS["duplicated_genes_action"])] = DupGeneActions.keep_first,
        covars:             Annotated[Optional[str], typer.Option("--covars", "-c", help=RUN_GLS_ARGS["covars"])]                 = None,
        cohort_name:        Annotated[Optional[str], typer.Option("--cohort-name", "-n", help=RUN_GLS_ARGS["cohort_name"])]       = None,
        lv_list:            Annotated[Optional[List[str]], typer.Option("--lv-list", help=RUN_GLS_ARGS["lv_list"])]                             = None,
        lv_model_file:      Annotated[Optional[str], typer.Option("--lv-model-file", help=RUN_GLS_ARGS["lv_model_file"])]                       = None,
        batch_id:           Annotated[Optional[int], typer.Option("--batch-id", help=RUN_GLS_ARGS["batch_id"])]                                 = None,
        batch_n_splits:     Annotated[ Optional[int], typer.Option("--batch-n-splits", help=RUN_GLS_ARGS["batch_n_splits"])]                    = None,
) -> None:
    """
    Run the Generalized Least Squares (GLS) model by default. Note that you need to run "phenoplier init" first to set up the environment.
    """
    def check_batch_args():
        if len(lv_list) > 0 and (batch_id is not None or batch_n_splits is not None):
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
        output_file = Path(output_file)
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
    
    def remove_dup_gene_entries(data):
        if dup_genes_action.startswith("keep"):
            keep_action = dup_genes_action.split("-")[1]
        elif dup_genes_action == "remove-all":
            keep_action = False
        else:
            raise ValueError("Wrong --duplicated-genes-action value")
        logger.info(
            f"Removed duplicated genes symbols using '{args.duplicated_genes_action}'. "
            f"Data now has {data.shape[0]} genes"
        )
        return data.loc[~data.index.duplicated(keep=keep_action)]

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
    data = remove_dup_gene_entries(data)
    # unique index (gene names)
    if not data.index.is_unique:
        logger.error(
            "Duplicated genes in input data. Use option --duplicated-genes-action "
            "if you want to skip them."
        )
    sys.exit(1)


    # Build command line arguments
    gene_corrs_args = f"--gene-corr-file {gene_corr_file}" if gene_corr_file else "--debug-use-ols"
    if gene_corr_mode == "sub":
        gene_corrs_args += " --debug-use-sub-gene-corr"
    # Build covars arguments
    covars_args = (
        f"--covars {RUN_GLS_DEFAULTS["covars"]}" if covars == "default"
        else f"--covars {covars}" if covars
        else ""
    )
    # Build cohort arguments
    cohort_args = ""
    if cohort_name:
        # FIXME: hardcoded
        cohort_metadata_dir = f"{os.getenv('PHENOPLIER_RESULTS_GLS')}/gene_corrs/cohorts/{cohort_name}/gtex_v8/mashr/"
        cohort_args = f"--cohort-metadata-dir {cohort_metadata_dir}"
    # Build batch arguments
    batch_args = ""
    if batch_id and batch_n_splits:
        batch_args = f"--batch-id {batch_id} --batch-n-splits {batch_n_splits}"
    elif lv_list:
        batch_args = f"--lv-list {','.join(lv_list)}"
    # Build lv model file arguments
    lv_model_args = f"--lv-model-file {lv_model_file}" if lv_model_file else ""
    # Assemble and execute the final command
    GLS_PATH = Path(gls_cli.__file__).resolve()
    # TODO: remove gls_cli, call directly the function from the library, instead of use shell command. Otherwise,
    #  tests and exceptions handling tricky
    command = (f"python3 {GLS_PATH} "
               f"-i {input_file} "
               f"--duplicated-genes-action keep-first "
               f"-o {output_file} {gene_corrs_args} {covars_args} {cohort_args} {batch_args} {lv_model_args}")
    # TODO: Add pretty print for command. Should have indentation and new lines
    # typer.echo(f"Running command: {command}")
    # Execute Command
    os.system(command)


if __name__ == "__main__":
    app()
