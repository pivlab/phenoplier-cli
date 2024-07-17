import os
import random
import logging
from pathlib import Path

from typer.testing import CliRunner
from pytest import mark
from phenoplier import cli
from phenoplier.config import settings as conf
from test.utils import get_test_output_dir, load_pickle, compare_dataframes_close

logger = logging.getLogger(__name__)

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

# Define the placeholders in the command
_BASE_COMMAND = (
    "run gene-corr correlate "
    "-c {cohort} "
    "-r {reference_panel} "
    "-m {eqtl_models} "
    "-s {chromosome} "
    "-i {input_dir} "
    "-o {output_dir} "
)

# Define the test output directory
# Todo: organize test data dir the same way as test output dir
output_dir_base = get_test_output_dir(Path(__file__))
test_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/99_all_results/mashr/"
# To reduce test runtime, only test one random chromosome (1 -22)
chromosome_to_test = random.randint(1, 22)


@mark.skipif(IN_GITHUB_ACTIONS, reason="Slow and computationally expensive test, skip in GitHub Actions")
@mark.order(after="test_main_run_corr_preprocess::test_cli_command")
# Parameterize the test cases
@mark.parametrize(
    "cohort, reference_panel, eqtl_models, chromosome, input_dir, output_dir",
    [
        (
                "phenomexcan_rapid_gwas",
                "GTEX_V8",
                "MASHR",
                chromosome_to_test,
                test_data_dir,
                output_dir_base
        ),
        # Add more test cases here as needed
    ]
)
def test_cli_command(cohort, reference_panel, eqtl_models, chromosome, input_dir, output_dir):
    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_models=eqtl_models,
        chromosome=chromosome,
        input_dir=input_dir,
        output_dir=output_dir,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    logger.info(f"Running command: {command}")

    # Assert the command ran successfully
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"

    filename = f"by_chr/gene_corrs-chr{chromosome}.pkl"
    test_output = output_dir / filename
    ref_output = test_data_dir / filename
    # Assert the output file exists
    assert test_output.exists(), f"Output file {test_output} does not exist"
    # Load the pickled dataframes
    df1 = load_pickle(test_output)
    df2 = load_pickle(ref_output)
    # Assert the output matches the expected output
    assert compare_dataframes_close(df1, df2), f"Output file {test_output} does not match expected output"
