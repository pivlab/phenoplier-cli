from typer.testing import CliRunner
from pytest import mark
from pathlib import Path
from tomlkit import parse
from phenoplier import cli

runner = CliRunner()
# Get package metadata
pacakge_toml_file = Path(__file__).parent.parent.parent.parent.resolve() / "pyproject.toml"
with open(pacakge_toml_file) as f:
    package_toml = parse(f.read())
    _PACKAGE_NAME = package_toml["tool"]["poetry"]["name"]
    _PACKAGE_VERSION = package_toml["tool"]["poetry"]["version"]


@mark.parametrize("options, expected_output", [
    (["--help", "-h"], "Phenopliler CLI"),
    (["--version", "-v"], f"{_PACKAGE_NAME} v{_PACKAGE_VERSION}\n"),
])
def test_options(options, expected_output):
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        print(result.stdout)
        assert result.exit_code == 0
        assert expected_output in result.stdout
