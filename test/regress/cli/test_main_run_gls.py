import os
from typer.testing import CliRunner
from pathlib import Path
from pytest import mark
from phenoplier import cli
from phenoplier.config import settings
from .utils import diff_tsv

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@mark.parametrize("options, expected_output", [
    (["run gls --help", "run gls -h"], "Run the Generalized Least Squares (GLS) model"),
])
def test_options(options, expected_output):
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        assert result.exit_code == 0
        assert expected_output in result.stdout


def _test_random_pheno(idx: int, with_default_covars: bool):
    # Prepare directories
    test_dir = settings.TEST_DIR
    test_output_dir = settings.TEST_OUTPUT_DIR + "/" + os.path.basename(__file__).replace(".py", "")
    Path(test_output_dir).mkdir(parents=True, exist_ok=True)
    print(test_output_dir)
    # Prepare cli options
    input_file = Path(f"{test_dir}/data/gls/covars_test/random.pheno{idx}-gtex_v8-mashr-smultixcan.txt").resolve()
    output_file_prefix = "with_covars_" if with_default_covars else "without_covars_"
    output_file = Path(f"{test_output_dir}/{output_file_prefix}random.pheno{idx}.tsv").resolve()
    gene_corr_file = Path(f"{test_dir}/data/gls/covars_test/gene_corr_file/gene_corrs-symbols-within_distance_5mb.per_lv").resolve()
    option = f"run gls -i {input_file} -o {output_file} --gene-corr-file {gene_corr_file}"
    if with_default_covars:
        option += ' --covars default'
    # Delete output file if it already exists
    if output_file.exists():
        output_file.unlink()
    # Run command
    result = runner.invoke(cli.app, option)
    print(result.stdout)
    if result.exit_code != 0:
        print(result.stdout)
        print(result.stderr)
    assert result.exit_code == 0
    # Compare output
    expected_output_file_folder = "with_covars" if with_default_covars else "without_covars"
    expected_output_file_prefix = "co_" if with_default_covars else ""
    expected_output_file = Path(f"{test_dir}/data/gls/covars_test/ref_output/{expected_output_file_folder}/{expected_output_file_prefix}random.pheno{idx}.tsv").resolve()
    assert not diff_tsv(output_file, expected_output_file)
    # Cleanup
    output_file.unlink()


def test_without_covars_random_pheno0():
    _test_random_pheno(0, False)


def test_with_covars_random_pheno0():
    _test_random_pheno(0, True)


@mark.skipif(IN_GITHUB_ACTIONS, reason="Redundant test. Slow for GitHub Actions.")
def test_without_covars_random_pheno15():
    _test_random_pheno(15, False)


@mark.skipif(IN_GITHUB_ACTIONS, reason="Redundant test. Slow for GitHub Actions.")
def test_with_covars_random_pheno15():
    _test_random_pheno(15, True)
