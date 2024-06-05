from typer.testing import CliRunner
from phenoplier import cli
from phenoplier.config import settings
from pytest import mark
from pathlib import Path

runner = CliRunner()
_TEST_OUTPUT_DIR = Path(settings.TEST_OUTPUT_DIR) / "test_main_init"


@mark.parametrize("file", [
    "phenoplier_settings.toml"
])
def test_create_file(file):
    command = f"init -p {_TEST_OUTPUT_DIR}"
    result = runner.invoke(cli.app, command)
    assert result.exit_code == 0
    out_path = Path(_TEST_OUTPUT_DIR, file)
    print(out_path)
    assert Path(_TEST_OUTPUT_DIR, file).exists()
    Path(_TEST_OUTPUT_DIR, file).unlink()
    assert not Path(_TEST_OUTPUT_DIR, file).exists()
