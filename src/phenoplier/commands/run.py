"""This module contains the logic for the "run" sub commmand"""
import typer
from typing import Annotated

app = typer.Typer()

@app.command()
def gls(
    input_file: Annotated[str, typer.Option("--input-file", "-i", help="Path to the input file")],
    output_file: Annotated[str, typer.Option("--output-file", "-o", help="Path to the output file")],
    debug_use_ols: Annotated[bool, typer.Option("--debug-use-ols", help="Use OLS instead of GLS for debugging")] = None,
    gene_corr_file: Annotated[str, typer.Option("--gene-corr-file", help="Path to the gene correlation file")] = None,
) -> None:
    """
    Run the Generalized Least Squares (GLS) model
    """
    
    # Check if both "debug_use_ols" and "gene_corr_file" are None
    if debug_use_ols is None and gene_corr_file is None:
        # If neither option is provided, print an error and exit.
        typer.echo("Error: either --debug-use-ols or --gene-corr-file <value> must be provided", err=True)
        raise typer.Exit(code=1)
    
    # Normal processing logic goes here
    if debug_use_ols is not None:
        typer.echo("Debugging with OLS")
    if gene_corr_file is not None:
        typer.echo(f"Using gene correlation file: {gene_corr_file}")
        
if __name__ == "__main__":
    app()