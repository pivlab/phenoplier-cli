"""This module provides the command line interface for Phenoplier."""

import os
import typer
import tomlkit
from typing import Optional, Annotated, List
from pathlib import Path
from . import gls_cli
from .templates.user_settings import DEFAULT as DEFAULT_USER_SETTINGS
from .config import settings
from .config import USER_SETTINGS_FILE

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
def _version_callback(value: bool) -> None:
    """Callback for the --version option."""
    if value:
        typer.echo(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        raise typer.Exit()


@app.callback()
def main(
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
        verbose: bool = False,
        debug: bool = False
) -> None:
    """
    Phenopliler CLI

    \n PhenoPLIER is a flexible computational framework that combines gene-trait and gene-drug associations with gene
    modules expressed in specific contexts (see Figure above). The approach uses a latent representation (with latent
    variables or LVs representing gene modules) derived from a large gene expression compendium to integrate TWAS
    with drug-induced transcriptional responses for a joint analysis. The approach consists in three main components:

    \n
    1. an LV-based regression model to compute an association between an LV and a trait,
    2. a clustering framework to learn groups of traits with shared transcriptomic properties, and
    3. an LV-based drug repurposing approach that links diseases to potential treatments.

    \n For more details, check out our article in Nature Communications (https://doi.org/10.1038/s41467-023-41057-4)
    or our Manubot web version (https://greenelab.github.io/phenoplier_manuscript/). To cite PhenoPLIER,
    see 10.1038/s41467-023-41057-4:

    \n
    Projecting genetic associations through gene expression patterns highlights disease etiology and drug mechanisms
    Pividori, M., Lu, S., Li, B. et al.
    Nat Commun 14, 5562 (2023) https://doi.org/gspsxr
    DOI: 10.1038/s41467-023-41057-4

    \n Interested in using PhenoPLIER? Any questions? Check out our Discussions section (
    https://github.com/greenelab/phenoplier/discussions) and start a discussion by asking a question or sharing your
    thoughts. We are happy to help!
    """
    return


# TODO: Add a prompt to ask the user if they want to overwrite the existing settings file
@app.command()
def init(
        output_file: Annotated[
            str, typer.Option("--output-file", "-o", help="Path to the output user settings file")] = str(
            USER_SETTINGS_FILE),
):
    """
    Initialize a user settings file in the home directory in TOML format.
    """

    def create_user_settings():
        settings_file = USER_SETTINGS_FILE
        if not settings_file.exists():
            settings = DEFAULT_USER_SETTINGS
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            settings_file.write_text(tomlkit.dumps(settings))
            typer.echo("Config file created at " + str(settings_file) + ".")
        else:
            typer.echo("Config file already exists at " + str(settings_file) + ".")

    create_user_settings()


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


@cmd_group_run.command()
# @load_and_update_config
def gls(
        input_file: Annotated[str, typer.Option("--input-file", "-i", help="File path to S-MultiXcan result file (tab-separated and with at least columns 'gene' and 'pvalue")],
        output_file: Annotated[str, typer.Option("--output-file", "-o", help="File path where results will be written to")],
        # phenoplier_root_dir:            Annotated[str, typer.Option("--phenoplier-root-dir", envvar="PHENOPLIER_ROOT_DIR", help="Phenoplier root directory")],
        # phenoplier_metaxcan_base_dir:   Annotated[str, typer.Option("--phenoplier-metaxcan-base-dir", envvar="PHENOPLIER_METAXCAN_BASE_DIR", help="Phenoplier MetaXcan base directory")],
        gene_corr_file: Annotated[Optional[str], typer.Option("--gene-corr-file", help="Path to a gene correlations file or folder. It's is mandatory if running a GLS model, and not necessary for OLS")] = None,
        use_covars: Annotated[Optional[str], typer.Option("--covars", help="List of covariates to use")] = None,
        cohort_name: Annotated[Optional[str], typer.Option("--cohort-name", help="Cohort name")] = None,
        lv_list: Annotated[Optional[List[str]], typer.Option("--lv-list", help="List of LV (gene modules) identifiers on which an association will be computed. All the rest not in the list are ignored")] = None,
        debug_use_sub_corr: Annotated[bool, typer.Option("--debug-use-sub-gene-corr", help="Use an LV-specific submatrix of the gene correlation matrix")] = True,
        debug_use_ols: Annotated[bool, typer.Option("--debug-use-ols", help="Use a standard OLS model instead of GLS for debugging purpose")] = False,
        batch_id: Annotated[Optional[int], typer.Option("--batch-id", help="Batch ID")] = None,
        batch_n_splits: Annotated[ Optional[int], typer.Option("--batch-n-splits", help="Number of splits in the batch")] = None,
) -> None:
    """
    Run the Generalized Least Squares (GLS) model. Note that you need to run "phenoplier init" first to set up the environment.
    """

    # TODO: Put error messages in constants.messages as dict kv paris
    # Check if both "debug_use_ols" and "gene_corr_file" are None
    if debug_use_ols is False and gene_corr_file is None:
        raise typer.BadParameter("Either --debug-use-ols or --gene-corr-file <value> must be provided")
    # and they should not be both provided
    if debug_use_ols is True and gene_corr_file is not None:
        raise typer.BadParameter("Only one of --debug-use-ols or --gene-corr-file <value> can be provided")

    # Build command line arguments
    gene_corrs_args = f"--gene-corr-file {gene_corr_file}" if gene_corr_file else "--debug-use-ols"
    if debug_use_sub_corr:
        gene_corrs_args += " --debug-use-sub-gene-corr"
    # Build covars arguments
    covars_args = f"--covars {use_covars}" if use_covars else ""
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

    # Assemble and execute the final command
    GLS_PATH = Path(gls_cli.__file__).resolve()
    # TODO: remove gls_cli, call directly the function from the library, instead of use shell command. Otherwise,
    #  tests and exceptions handling tricky
    command = (f"python3 {GLS_PATH} "
               f"-i {input_file} "
               f"--duplicated-genes-action keep-first "
               f"-o {output_file} {gene_corrs_args} {covars_args} {cohort_args} {batch_args}")
    # TODO: Add pretty print for command. Should have indentation and new lines
    # typer.echo(f"Running command: {command}")
    # Execute Command
    os.system(command)


if __name__ == "__main__":
    app()
