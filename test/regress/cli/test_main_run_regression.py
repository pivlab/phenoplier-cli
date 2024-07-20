import os
import tempfile
from typing import Iterator

import pytest
from _pytest.capture import CaptureFixture
from click.testing import Result
from typer.testing import CliRunner
from pathlib import Path
from pytest import mark
from phenoplier import cli
from phenoplier.config import settings
from .utils import diff_tsv, get_test_output_dir

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
_COMMAND_NAME = "run regression"


@pytest.fixture
def click_runner(capsys: CaptureFixture[str]) -> Iterator[CliRunner]:
    """
    Convenience fixture to return a click.CliRunner for cli testing
    """

    class MyCliRunner(CliRunner):
        """Override CliRunner to disable capsys"""

        def invoke(self, *args, **kwargs) -> Result:
            # Way to fix https://github.com/pallets/click/issues/824
            with capsys.disabled():
                result = super().invoke(*args, **kwargs)
            return result

    yield MyCliRunner()


@mark.parametrize("options, expected_output", [
    ([f"{_COMMAND_NAME} --help", f"{_COMMAND_NAME} regression -h"], "Run the Generalized Least Squares (GLS) model"),
])
def test_options(options, expected_output):
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        assert result.exit_code == 0
        assert expected_output in result.stdout


@pytest.mark.parametrize("idx, with_default_covars", [
    (0, True),
    (0, False),
    pytest.param(15, True, marks=pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Redundant test. Slow for GitHub Actions.")),
    pytest.param(15, False, marks=pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Redundant test. Slow for GitHub Actions.")),
    # Add more cases as needed
])
def test_random_pheno(idx: int, with_default_covars: bool, click_runner: CliRunner):
    # Prepare directories
    test_dir = settings.TEST_DIR
    test_output_dir = get_test_output_dir(__file__)
    Path(test_output_dir).mkdir(parents=True, exist_ok=True)
    print(test_output_dir)

    # Init project files
    temp_project_dir = get_test_output_dir(__file__) / "temp_project"
    temp_project_dir.mkdir(parents=True, exist_ok=True)
    runner.invoke(cli.app, f"init -p {temp_project_dir}")

    # Prepare cli options
    input_file = Path(f"{test_dir}/data/gls/covars_test/random.pheno{idx}-gtex_v8-mashr-smultixcan.txt").resolve()
    output_file_prefix = "with_covars_" if with_default_covars else "without_covars_"
    output_file = Path(f"{test_output_dir}/{output_file_prefix}random.pheno{idx}.tsv").resolve()
    gene_corr_file = Path(
        f"{test_dir}/data/gls/covars_test/gene_corr_file/gene_corrs-symbols-within_distance_5mb.per_lv").resolve()
    option = f"{_COMMAND_NAME} -i {input_file} -o {output_file} --gene-corr-file {gene_corr_file} -p {temp_project_dir}"
    if with_default_covars:
        option += ' --covars default'
    print(f"Running command: {option}")

    # Delete output file if it already exists
    if output_file.exists():
        output_file.unlink()

    # Run command
    result = runner.invoke(cli.app, option)
    print(result.stdout)
    assert result.exit_code == 0

    # Compare output
    expected_output_file_folder = "with_covars" if with_default_covars else "without_covars"
    expected_output_file_prefix = "co_" if with_default_covars else ""
    expected_output_file = Path(
        f"{test_dir}/data/gls/covars_test/ref_output/{expected_output_file_folder}/{expected_output_file_prefix}random.pheno{idx}.tsv").resolve()
    assert not diff_tsv(output_file, expected_output_file)

    # Cleanup
    # output_file.unlink()


# def test_without_covars_random_pheno0():
#     _test_random_pheno(0, False)
#
#
# def test_with_covars_random_pheno0():
#     _test_random_pheno(0, True)
#
#
# @mark.skipif(IN_GITHUB_ACTIONS, reason="Redundant test. Slow for GitHub Actions.")
# def test_without_covars_random_pheno15():
#     _test_random_pheno(15, False)
#
#
# @mark.skipif(IN_GITHUB_ACTIONS, reason="Redundant test. Slow for GitHub Actions.")
# def test_with_covars_random_pheno15():
#     _test_random_pheno(15, True)
