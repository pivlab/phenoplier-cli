from typer.testing import CliRunner
from pytest import fixture, mark
from importlib.metadata import distribution
from phenoplier import cli

runner = CliRunner()
# Get package metadata
dist = distribution("phenoplier")
app_name = dist.metadata["name"]
app_version = dist.version


@mark.parametrize("options, expected_output", [
    (["--help", "-h"], "Phenopliler CLI"),
    (["--version", "-v"], f"{app_name} v{app_version}\n"),
])
def test_options(options, expected_output):
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        assert result.exit_code == 0
        assert expected_output in result.stdout
