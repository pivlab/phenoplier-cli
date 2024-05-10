from typer.testing import CliRunner
from pytest import fixture, mark
from importlib.metadata import distribution
from phenoplier import cli

runner = CliRunner()


@mark.parametrize("options, expected_output", [
    (["run --help", "run -h"], "Execute a specific Phenoplier pipeline."),
])
def test_options(options, expected_output):
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        assert result.exit_code == 0
        assert expected_output in result.stdout

