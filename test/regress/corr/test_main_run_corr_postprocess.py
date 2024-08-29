import os
import logging
from pathlib import Path

from typer.testing import CliRunner
from pytest import mark
from phenoplier import cli
from phenoplier.config import settings as conf
from phenoplier.commands.invoker import invoke_corr_postprocess
from test.utils import get_test_output_dir, load_pickle, compare_dataframes_close

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


# Define the placeholders in the command
_BASE_COMMAND = (
    "run gene-corr postprocess "
    "-c {cohort} "
    "-r {reference_panel} "
    "-m {eqtl_model} "
    "-i {input_dir} "
    "-g {genes_info} "
    "-o {output_dir}"
)

# Define the test output directory
# Todo: organize test data dir the same way as test output dir
output_dir_base = get_test_output_dir(Path(__file__))
prev_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/3-correlate/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr"
test_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/4-postprocess/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr"


@mark.skipif(IN_GITHUB_ACTIONS, reason="Slow and computationally expensive test, skip in GitHub Actions")
@mark.corr
@mark.order(4)
# Parameterize the test cases
@mark.parametrize(
    "cohort, reference_panel, eqtl_model, input_dir, genes_info, output_dir",
    [
        (
                "phenomexcan_rapid_gwas",
                "GTEX_V8",
                "MASHR",
                prev_data_dir / "by_chr",
                prev_data_dir / "genes_info.pkl",
                output_dir_base
        ),
        # Add more test cases here as needed
    ]
)
def test_cli_command(cohort, reference_panel, eqtl_model, input_dir, genes_info, output_dir):
    # Build the command
    suc, msg = invoke_corr_postprocess(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        input_dir=input_dir,
        genes_info=genes_info,
        output_dir=output_dir,
    )
    assert suc, msg

    filename = f"gene_corrs-symbols.pkl"
    test_output = output_dir / filename
    ref_output = test_data_dir / filename
    # Assert the output file exists
    assert test_output.exists(), f"Output file {test_output} does not exist"
    # Load the pickled dataframes
    df1 = load_pickle(test_output)
    df2 = load_pickle(ref_output)
    # Assert the output matches the expected output
    assert compare_dataframes_close(df1, df2), f"Output file {test_output} does not match expected output"
