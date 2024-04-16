"""This module provides the command line interface for Phenoplier."""

from typing import Optional
import typer

from phenoplier.constants.metadata import APP_NAME, APP_VERSION

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=True
)

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{APP_NAME} v{APP_VERSION}")
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

    \n
    PhenoPLIER is a flexible computational framework that combines gene-trait and gene-drug associations with gene modules expressed in specific contexts (see Figure above). The approach uses a latent representation (with latent variables or LVs representing gene modules) derived from a large gene expression compendium to integrate TWAS with drug-induced transcriptional responses for a joint analysis. The approach consists in three main components:

    \n
    1. an LV-based regression model to compute an association between an LV and a trait,
    2. a clustering framework to learn groups of traits with shared transcriptomic properties, and
    3. an LV-based drug repurposing approach that links diseases to potential treatments.

    \n
    For more details, check out our article in Nature Communications (https://doi.org/10.1038/s41467-023-41057-4) or our Manubot web version (https://greenelab.github.io/phenoplier_manuscript/). To cite PhenoPLIER, see 10.1038/s41467-023-41057-4:

    \n
    Projecting genetic associations through gene expression patterns highlights disease etiology and drug mechanisms
    Pividori, M., Lu, S., Li, B. et al.
    Nat Commun 14, 5562 (2023) https://doi.org/gspsxr
    DOI: 10.1038/s41467-023-41057-4

    \n
    Interested in using PhenoPLIER? Any questions? Check out our Discussions section (https://github.com/greenelab/phenoplier/discussions) and start a discussion by asking a question or sharing your thoughts. We are happy to help!
    """
    return