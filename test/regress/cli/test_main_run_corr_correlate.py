import os

from typer.testing import CliRunner
from pytest import mark
from phenoplier import cli

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


# Define the placeholders in the command
_BASE_COMMAND = (
    "run gene-corr correlate "
    "-c {cohort} "
    "-r {reference_panel} "
    "-m {eqtl_models} "
    "-s {chromosome}"
)


@mark.skipif(IN_GITHUB_ACTIONS, reason="Data has not been setup in Github Actions yet. Local test only.")
@mark.skip()
# Parameterize the test cases
@mark.parametrize(
    "cohort, reference_panel, eqtl_models, chromosome",
    [
        (
                "1000g_eur",
                "GTEX_V8",
                "MASHR",
                "1"
        ),
        # Add more test cases here as needed
    ]
)
def test_cli_command(cohort, reference_panel, eqtl_models, chromosome):
    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_models=eqtl_models,
        chromosome=chromosome,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)

    # Assert the command ran successfully
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"
