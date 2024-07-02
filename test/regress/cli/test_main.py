from pathlib import Path

from pytest import mark
from tomlkit import parse
from typer.testing import CliRunner

from phenoplier import cli
from phenoplier import __name__, __version__

runner = CliRunner()


@mark.parametrize("options, expected_output", [
    (["--help", "-h"], "Phenopliler CLI"),
    (["--version", "-v"], f"{__name__} v{__version__}\n"),
])
def test_options(options, expected_output):
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        print(result.stdout)
        assert result.exit_code == 0
        assert expected_output in result.stdout
