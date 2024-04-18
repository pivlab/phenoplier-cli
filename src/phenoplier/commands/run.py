import typer
import os
from typing import Optional, List

app = typer.Typer()

@app.command()
def gls(
    input_file: str = typer.Option(..., "--input-file", "-i", help="Path to the input file"),
    output_file: str = typer.Option(..., "--output-file", "-o", help="Path to the output file"),
    debug_use_ols: bool = typer.Option(None, "--debug-use-ols", help="Use OLS instead of GLS for debugging"),
    gene_corr_file: str = typer.Option(None, "--gene-corr-file", help="Path to the gene correlation file"),
    use_covars: Optional[str] = typer.Option(None, "--covars", help="Covariates to use"),
    cohort_name: Optional[str] = typer.Option(None, "--cohort-name", help="Cohort name"),
    batch_id: Optional[str] = typer.Option(None, "--batch-id", help="Batch ID"),
    batch_n_splits: Optional[int] = typer.Option(None, "--batch-n-splits", help="Number of splits in the batch"),
    lv_list: Optional[List[str]] = typer.Option(None, "--lv-list", help="List of latent variables"),
    debug_use_sub_corr: bool = typer.Option(None, "--debug-use-sub-gene-corr", help="Use sub gene correlation for debugging")
) -> None:
    """
    Run the Generalized Least Squares (GLS) model
    """

    # Environmental checks
    required_env_vars = ["PHENOPLIER_ROOT_DIR", "PHENOPLIER_METAXCAN_BASE_DIR"]
    for var in required_env_vars:
        if os.getenv(var) is None:
            typer.echo(f"Error: {var} environment variable is not set", err=True)
            raise typer.Exit(code=1)

    # Check if both "debug_use_ols" and "gene_corr_file" are None
    if debug_use_ols is None and gene_corr_file is None:
        typer.echo("Error: either --debug-use-ols or --gene-corr-file <value> must be provided", err=True)
        raise typer.Exit(code=1)

    # Batch processing argument validation
    if (batch_id is None) != (batch_n_splits is None):
        typer.echo("Error: both --batch-id and --batch-n-splits must be provided together", err=True)
        raise typer.Exit(code=1)

    # Building command line arguments
    gene_corrs_args = f"--gene-corr-file {gene_corr_file}" if gene_corr_file else "--debug-use-ols"
    if debug_use_sub_corr:
        gene_corrs_args += " --debug-use-sub-gene-corr"

    covars_args = f"--covars {use_covars}" if use_covars else ""
    cohort_args = ""
    if cohort_name:
        cohort_metadata_dir = f"{os.getenv('PHENOPLIER_RESULTS_GLS')}/gene_corrs/cohorts/{cohort_name}/gtex_v8/mashr/"
        cohort_args = f"--cohort-metadata-dir {cohort_metadata_dir}"

    batch_args = ""
    if batch_id and batch_n_splits:
        batch_args = f"--batch-id {batch_id} --batch-n-splits {batch_n_splits}"
    elif lv_list:
        batch_args = f"--lv-list {','.join(lv_list)}"

    # Print command (dbg)
    command = f"python some_script.py -i {input_file} -o {output_file} {gene_corrs_args} {covars_args} {cohort_args} {batch_args}"
    typer.echo(f"Running command: {command}")

    # Call the GLS model

if __name__ == "__main__":
    app()
