import os

from typer.testing import CliRunner
from pytest import mark
from phenoplier import cli

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
_BASE_COMMAND_NAME = "run gene-corr"


@mark.parametrize("options, expected_output", [
    ([f"{_BASE_COMMAND_NAME} --help", f"{_BASE_COMMAND_NAME} -h"], ""),
    ([f"{_BASE_COMMAND_NAME} cov --help", f"{_BASE_COMMAND_NAME} cov -h"], ""),
    ([f"{_BASE_COMMAND_NAME} preprocess --help", f"{_BASE_COMMAND_NAME} preprocess -h"], ""),
    ([f"{_BASE_COMMAND_NAME} correlate --help", f"{_BASE_COMMAND_NAME} correlate -h"], ""),
    ([f"{_BASE_COMMAND_NAME} postprocess --help", f"{_BASE_COMMAND_NAME} postprocess -h"], ""),
    ([f"{_BASE_COMMAND_NAME} generate --help", f"{_BASE_COMMAND_NAME} generate -h"], ""),
])
def test_options(options, expected_output):
    """Check that the help message is displayed when the help flag is passed."""
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        assert result.exit_code == 0
        assert expected_output in result.stdout
