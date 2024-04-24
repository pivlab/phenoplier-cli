import typer
import os
from typing import Optional, Annotated, List
from pathlib import Path

app = typer.Typer()

@app.command()
def gls(
    input_file: Annotated[str, typer.Option("--input-file", "-i", help="Path to the input file")],
    output_file: Annotated[str, typer.Option("--output-file", "-o", help="Path to the output file")],
    phenoplier_root_dir: Annotated[str, typer.Option("--phenoplier-root-dir", envvar="PHENOPLIER_ROOT_DIR", help="Phenoplier root directory")],
    phenoplier_metaxcan_base_dir: Annotated[str, typer.Option("--phenoplier-metaxcan-base-dir", envvar="PHENOPLIER_METAXCAN_BASE_DIR", help="Phenoplier MetaXcan base directory")],
    batch_id: Annotated[int, typer.Option("--batch-id", help="Batch ID")] = None,
    batch_n_splits: Annotated[int, typer.Option("--batch-n-splits", help="Number of splits in the batch")] = None,
    debug_use_sub_corr: Annotated[int, typer.Option("--debug-use-sub-gene-corr", help="Use sub gene correlation for debugging")] = False,
    debug_use_ols: Annotated[bool, typer.Option("--debug-use-ols", help="Use OLS instead of GLS for debugging")] = False,
    gene_corr_file: Annotated[str, typer.Option("--gene-corr-file", help="Path to the gene correlation file")] = None,
    use_covars: Annotated[str, typer.Option("--covars", help="Covariates to use")] = None,
    cohort_name: Annotated[str, typer.Option("--cohort-name", help="Cohort name")] = None,
    lv_list: Annotated[List[str], typer.Option("--lv-list", help="List of latent variables")] = None,
) -> None:
    """
    Run the Generalized Least Squares (GLS) model
    """

    # TODO: Put error messages in constants.messages as dict kv paris
    # Check if both "debug_use_ols" and "gene_corr_file" are None
    if debug_use_ols is False and gene_corr_file is None:
        # typer.echo("Error: either --debug-use-ols or --gene-corr-file <value> must be provided", err=True)
        raise typer.BadParameter("Either --debug-use-ols or --gene-corr-file <value> must be provided")
    # and they shold not be both provided
    if debug_use_ols is True and gene_corr_file is not None:
        raise typer.BadParameter("Only one of --debug-use-ols or --gene-corr-file <value> can be provided")
    
    # Build command line arguments
    gene_corrs_args = f"--gene-corr-file {gene_corr_file}" if gene_corr_file else "--debug-use-ols"
    if debug_use_sub_corr:
        gene_corrs_args += " --debug-use-sub-gene-corr"

    covars_args = f"--covars {use_covars}" if use_covars else ""
    cohort_args = ""
    if cohort_name:
        # FIXME: hardcoded
        cohort_metadata_dir = f"{os.getenv('PHENOPLIER_RESULTS_GLS')}/gene_corrs/cohorts/{cohort_name}/gtex_v8/mashr/"
        cohort_args = f"--cohort-metadata-dir {cohort_metadata_dir}"

    batch_args = ""
    if batch_id and batch_n_splits:
        batch_args = f"--batch-id {batch_id} --batch-n-splits {batch_n_splits}"
    elif lv_list:
        batch_args = f"--lv-list {','.join(lv_list)}"

    # Print command (dbg)
    PHENOPLIER_CODE_DIR = os.environ["PHENOPLIER_CODE_DIR"]
    GLS_PATH = Path(PHENOPLIER_CODE_DIR + "/libs/gls_cli.py").resolve()
    command = ( f"poetry run python {GLS_PATH} "
                f"-i {input_file} "
                f"--duplicated-genes-action keep-first "
                f"-o {output_file} {gene_corrs_args} {covars_args} {cohort_args} {batch_args}")
    typer.echo(f"Running command: {command}")
    # Execute Command
    os.system(command)
    
if __name__ == "__main__":
    app()
