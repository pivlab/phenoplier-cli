from typer.testing import CliRunner
from phenoplier import cli
from importlib.metadata import distribution

runner = CliRunner()
# Get package metadata
dist = distribution("phenoplier")
app_name = dist.metadata["name"]
app_version = dist.version

def test_version0():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{app_name} v{app_version}\n" in result.stdout