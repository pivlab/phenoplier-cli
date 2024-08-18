import os
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from typer.testing import CliRunner
from pytest import mark

from phenoplier.config import settings as conf
from phenoplier import cli
from test.utils import get_test_output_dir
from test.utils import compare_hdf5_files

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
# Parameterize the test cases
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
    # command = _BASE_COMMAND.format(
    #     reference_panel=reference_panel,
    #     eqtl_model=eqtl_model,
    #     output_dir=output_dir,
    # )
    # #
    # # # Execute the command using runner.invoke
    # result = runner.invoke(cli.app, command)
    # logger.info(f"Running command: {command}")
    # #
    # # # Assert the command ran successfully
    # assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"

    output_filename = f"{conf.TWAS["LD_BLOCKS"]["OUTPUT_FILE_NAME"]}"
    outfile = output_dir_base / output_filename

    assert outfile.exists(), f"Output file {outfile} does not exist"
    # use h5diff to compare generated file with reference file
    ref_file = "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/gene_corrs/reference_panels/gtex_v8/mashr/snps_chr_blocks_cov.h5"
    # assert compare_hdf5_files(outfile, ref_file), f"Output file {outfile} is not equal to reference file {ref_file}"
    df1 = pd.read_hdf(outfile, key="chr1").sort_index(axis=0).sort_index(axis=1)
    df2 = pd.read_hdf(ref_file, key="chr1").sort_index(axis=0).sort_index(axis=1)
    arr1 = df1.to_numpy()
    arr2 = df2.to_numpy()
    assert np.allclose(arr1, arr2), f"Output file {outfile} is not equal to reference file {ref_file}"
    return