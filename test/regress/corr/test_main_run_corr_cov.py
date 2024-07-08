import os
import subprocess

from pathlib import Path

from typer.testing import CliRunner
from pytest import mark
from phenoplier.config import settings as conf
from phenoplier import cli
from test.utils import get_test_output_dir
from test.utils import compare_hdf5_files

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


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
# Parameterize the test cases
@mark.parametrize(
    "reference_panel, eqtl_model, output_dir",
    [
        (
                "1000G",
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
    #
    # # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    #
    # # Assert the command ran successfully
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"

    output_filename = f"{conf.TWAS["LD_BLOCKS"]["OUTPUT_FILE_NAME"]}"
    outfile = output_dir_base / output_filename
    print(outfile)

    assert outfile.exists(), f"Output file {outfile} does not exist"
    # use h5diff to compare generated file with reference file
    ref_file = Path("/tmp/phenoplier/results/gls/gene_corrs/reference_panels/1000g/mashr/snps_chr_blocks_cov.h5")
    assert compare_hdf5_files(outfile, ref_file), f"Output file {outfile} is not equal to reference file {ref_file}"
