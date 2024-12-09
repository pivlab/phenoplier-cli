"""
This module provides the command line interface for Phenoplier.
"""

from typing import Annotated
from pathlib import Path

import typer
from typer.core import TyperGroup
from click import Context

from phenoplier.config import settings
from phenoplier.constants.arg import Common_Args, Cli, Init_Args
from phenoplier.commands.util.utils import create_settings_files
from phenoplier.commands.get import get
from phenoplier.commands.run.regression import regression
from phenoplier.commands.run.correlation.pipeline import pipeline
from phenoplier.commands.run.correlation.cov import cov
from phenoplier.commands.run.correlation.preprocess import preprocess
from phenoplier.commands.run.correlation.correlate import correlate
from phenoplier.commands.run.correlation.postprocess import postprocess
from phenoplier.commands.run.correlation.filter import filter
from phenoplier.commands.run.correlation.generate import generate
from phenoplier.commands.util.enums import DownloadAction
from phenoplier.commands.get import ActionMap
from phenoplier.commands.project import multiplier
from phenoplier.data import Downloader


# This class is used to group the commands in the order they appear in the code
class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)    # get commands using self.commands


# Define the main CLI program/command
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=True
)

# Define the subcommands
# "run" command group
cmd_group_run = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Run a specific Phenoplier functionality."
)
cmd_group_run.command()(regression)
# "gene-corr" command group
cmd_group_gene_corr = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Execute a specific Phenoplier functionality for the gene-gene correlation matrix generation. Except for the" 
    "'pipeline' command, all the other commands are organized sequentially in text. For example, you need to run the"
    "'cov' command before the 'preprocess' command, and so on.",
    cls=OrderCommands
)
cmd_group_gene_corr.command()(pipeline)
cmd_group_gene_corr.command()(cov)
cmd_group_gene_corr.command()(preprocess)
cmd_group_gene_corr.command()(correlate)
cmd_group_gene_corr.command()(postprocess)
cmd_group_gene_corr.command()(filter)
cmd_group_gene_corr.command()(generate)
# Add the "gene-corr" command group to the "run" command group
cmd_group_run.add_typer(cmd_group_gene_corr, name="gene-corr")
# "project" command group
cmd_group_project = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="projects input data into the specified representation space."
)
cmd_group_project.command()(multiplier)

# Register commands and command groups
# Add the command group "run" to the main program
app.add_typer(cmd_group_run, name="run")
app.add_typer(cmd_group_project, name="project")
app.command()(get)


# Callbacks in Typer allows us to create "--" options for the main program/command
def version_callback(value: bool) -> None:
    """Callback for the --version option."""
    if value:
        typer.echo(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        raise typer.Exit()


@app.callback()
def main(
        version: Annotated[bool, typer.Option("--version", "-v", help=Cli.VERSION.value, callback=version_callback)] = False,
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
        project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = settings.CURRENT_DIR,
        download_action: Annotated[DownloadAction, Init_Args.DOWNLOAD_ACTION.value] = None,
        # navigate_to_project_dir: bool = typer.Option(False, "--navigate", "-n", help=Init_Args.NAVIGATE.value)
):
    """
    Initialize settings file and necessary data in the specified directory.
    """
    create_settings_files(project_dir.resolve(), True)
    print()
    if download_action:
        actions = ActionMap[download_action]
        downloader = Downloader()
        downloader.setup_data(actions=actions)
    return


if __name__ == "__main__":
    app()
