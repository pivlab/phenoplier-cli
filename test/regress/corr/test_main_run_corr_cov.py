import os
import logging
from typing import Tuple
from pathlib import Path

import pandas as pd
from typer.testing import CliRunner
from pytest import mark

from phenoplier.config import settings as conf
from phenoplier import cli
from test.utils import get_test_output_dir
from test.utils import are_hdf5_files_close, are_non_numeric_df_equal

logger = logging.getLogger(__name__)

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

test_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/1-cov/reference_panels/"
# Define the placeholders in the command
_BASE_COMMAND = (
    "run gene-corr cov "
    "-r {reference_panel} "
    "-m {eqtl_model} "
    "-o {output_dir} "
)
# Define the test output directory
output_dir_base = get_test_output_dir(Path(__file__))


@mark.skipif(IN_GITHUB_ACTIONS, reason="Slow and computationally expensive test, skip in GitHub Actions")
@mark.corr
@mark.order(1)
@mark.parametrize(
    "reference_panel, eqtl_model, output_dir",
    [
        (
                "GTEX_V8",
                "MASHR",
                output_dir_base
        ),
        # Add more test cases here as needed
    ]
)
def test_cli_command(reference_panel, eqtl_model, output_dir):
    # Build the command
    command = _BASE_COMMAND.format(
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        output_dir=output_dir,
    )
    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    logger.info(f"Running command: {command}")
    #
    # Assert the command ran successfully
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"

    output_filename = f"{conf.TWAS["LD_BLOCKS"]["OUTPUT_FILE_NAME"]}"
    out_file = output_dir_base / output_filename

    assert out_file.exists(), f"Output file {out_file} does not exist"
    ref_file = (Path(conf.RESULTS["GLS"])
                / "gene_corrs"
                / "reference_panels"
                / reference_panel.lower()
                / eqtl_model.lower()
                / output_filename)
    # Handle the non-numerical field "metadata"
    df1 = pd.read_hdf(out_file, "metadata").sort_values(by="varID").reset_index(drop=True)
    df2 = pd.read_hdf(ref_file, "metadata").sort_values(by="varID").reset_index(drop=True)
    yes, msg = are_non_numeric_df_equal(df1, df2)
    assert yes, msg
    yes, msg = are_hdf5_files_close(out_file, ref_file, ("metadata",))
    assert yes, msg
