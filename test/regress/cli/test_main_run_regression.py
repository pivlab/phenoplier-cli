import re
import os
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import pytest

from typer.testing import CliRunner
import typer.core

from phenoplier import cli
from phenoplier.config import settings
from phenoplier.constants.message import RegressionError as err
from phenoplier.constants.message import RegressionInfo as info
from test.utils import get_test_output_dir


TEST_DIR = settings.TEST_DIR
DATA_DIR = Path(TEST_DIR, "data", "gls").resolve()
assert DATA_DIR.exists()

TEMP_DIR = get_test_output_dir(__file__)

typer.core.rich = None
runner = CliRunner()


# Note that since the following tests execute the CLI script directly, we need to add the source root to the PYTHONPATH
# i.e., PYTHONPATH=. pytest tests/test_gls_cli.py

@pytest.fixture()
def output_file():
    out_file = Path(TEMP_DIR) / "out.tsv"
    yield out_file
    if out_file.exists():
        out_file.unlink()


@pytest.fixture()
def full_gene_corrs_filepath():
    from scipy import sparse

    out_file = Path(TEMP_DIR) / "gene_corrs.pkl"

    gene_corrs = sparse.load_npz(DATA_DIR / "gene_corrs.npz").toarray()
    gene_names = np.load(DATA_DIR / "gene_corrs-gene_names.npz")["gene_names"]
    gene_corrs = pd.DataFrame(gene_corrs, index=gene_names, columns=gene_names)
    gene_corrs.to_pickle(out_file)

    yield out_file
    if out_file.exists():
        out_file.unlink()


_PATH_NOT_FOUND_REGEX = r"Path\s+.*?\s+does not exist"


def regex_match(regex: str, text: str) -> Tuple[bool, str]:
    # use the re.DOTALL flag, which makes the . (dot) match any character, including newline characters
    match = re.search(regex, text, re.DOTALL)
    return (True, "Match found!") if match else (False, "No match found.")


def rm_path_not_found(text):
    return regex_match(_PATH_NOT_FOUND_REGEX, text)


def test_gls_cli_input_file_does_not_exist(output_file):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "does_not_exist.txt"),
            "-o",
            output_file,
        ],
    )
    assert r is not None
    assert r.exit_code == 2
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Error" in r_output
    match, msg = rm_path_not_found(r_output)
    assert match, msg


def test_gls_cli_output_file_does_exist(output_file):
    # create output file
    with open(output_file, "a"):
        pass

    assert output_file.exists()

    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2",
            "--model",
            "ols",
        ],
    )
    assert r.exit_code == 0, r.stdout
    r_output = r.stdout
    assert "Skipping, output file exists" in r_output
    import os
    assert os.stat(output_file).st_size == 0, "Output file size is not empty"


def test_gls_cli_parent_of_output_file_does_not_exist():
    output_file = Path(TEMP_DIR) / "some_dir" / "out.tsv"

    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2",
            "--model",
            "ols",
        ],
    )
    assert r.exit_code == 1, r.stdout
    r_output = r.stdout.replace(os.linesep, "")
    assert "Error: parent directory of output file does not exist" in r_output
    assert not output_file.exists()


def test_gls_cli_single_smultixcan_no_gene_name_column(output_file):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-no_gene_name_column.txt"),
            "-o",
            output_file,
            "--model",
            "ols"
        ],
    )
    assert r is not None
    assert r.exit_code == 1, r.stdout
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert info.LOADING_INPUT in r_output
    assert err.NO_GENE_NAME_COLUMN in r_output


def test_gls_cli_single_smultixcan_no_pvalue_column(output_file):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-no_pvalue_column.txt"),
            "-o",
            output_file,
            "--model",
            "ols"
        ],
    )
    assert r is not None
    assert r.exit_code == 1
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert info.LOADING_INPUT in r_output
    assert err.NO_P_VALUE_COLUMN in r_output


def test_gls_cli_single_smultixcan_repeated_gene_names(output_file):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-repeated_gene_names.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--model",
            "ols"
        ],
    )
    assert r is not None
    assert r.exit_code == 1, r.stdout
    r_output = r.stdout.replace(os.linesep, "").replace(os.linesep, " ")
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert info.LOADING_INPUT in r_output
    assert err.DUP_GENES_FOUND in r_output


def test_gls_cli_single_smultixcan_repeated_gene_names_remove_repeated_keep_first(
        output_file,
):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-repeated_gene_names.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--dup-genes-action",
            "keep-first",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],
    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None

    # print(r_output)
    assert r.exit_code == 0
    assert len(r_output) > 1, r_output
    assert info.LOADING_INPUT in r_output
    assert "Input file has 54 genes" in r_output
    assert (
            "Removed duplicated genes symbols using 'keep-first'. Data now has 53 genes"
            in r_output
    )


def test_gls_cli_single_smultixcan_repeated_gene_names_remove_repeated_keep_last(
        output_file,
):
    # run keep-first first, and then check that results are not the same with keep-last

    # with keep-first
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-repeated_gene_names.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--dup-genes-action",
            "keep-first",
            "-l",
            "LV1 LV5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],
    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None
    assert r.exit_code == 0, r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert not output_data.isna().any().any()
    keep_first_results = output_data
    output_file.unlink()

    # with keep-last
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-repeated_gene_names.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--dup-genes-action",
            "keep-last",
            "-l",
            "LV1 LV5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],
    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None

    # print(r_output)
    assert r.exit_code == 0
    assert len(r_output) > 1, r_output
    assert (
            "Removed duplicated genes symbols using 'keep-last'. Data now has 53 genes"
            in r_output
    )

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert not output_data.isna().any().any()
    keep_last_results = output_data

    # results should be different across batches
    assert not np.allclose(
        keep_first_results["beta"].to_numpy(),
        keep_last_results["beta"].to_numpy(),
    )
    assert not np.allclose(
        keep_first_results["pvalue"].to_numpy(),
        keep_last_results["pvalue"].to_numpy(),
    )


def test_gls_cli_single_smultixcan_repeated_gene_names_remove_repeated_remove_all(
        output_file,
):
    # run keep-last first, and then check that results with remove-all are different

    # with keep-last
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-repeated_gene_names.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--dup-genes-action",
            "keep-last",
            "-l",
            "LV1 LV5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None
    # print(r_output)
    assert r.exit_code == 0

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert not output_data.isna().any().any()
    keep_last_results = output_data
    output_file.unlink()

    # with remove-all
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-repeated_gene_names.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--dup-genes-action",
            "remove-all",
            "-l",
            "LV1 LV5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None

    # print(r_output)
    assert r.exit_code == 0
    assert len(r_output) > 1, r_output
    assert (
            "Removed duplicated genes symbols using 'remove-all'. Data now has 52 genes"
            in r_output
    )

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert not output_data.isna().any().any()
    remove_all_results = output_data

    # results should be different across batches
    assert not np.allclose(
        keep_last_results["beta"].to_numpy(),
        remove_all_results["beta"].to_numpy(),
    )
    assert not np.allclose(
        keep_last_results["pvalue"].to_numpy(),
        remove_all_results["pvalue"].to_numpy(),
    )


def test_gls_cli_single_smultixcan_input_full_subset_of_lvs(output_file):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert info.LOADING_INPUT in r_output
    assert "Input file has 54 genes" in r_output
    assert "3 genes with missing values have been removed" in r_output
    assert (
            "p-values statistics: min=3.2e-05 | mean=2.2e-03 | max=6.3e-03 | # missing=3 (5.6%)"
            in r_output
    )

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data.isna().any().any()


def test_gls_cli_single_smultixcan_input_full_subset_of_lvs_none_exist_in_models(
        output_file,
):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1a LV2b LV3c",
            "--model",
            "ols"
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 1
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "A list of 3 LVs was provided, and 0 are present in LV models" in r_output
    assert "No LVs were selected" in r_output


def test_gls_cli_single_smultixcan_input_full_all_lvs_in_model_file(output_file):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert info.LOADING_INPUT in r_output
    assert "Input file has 54 genes" in r_output
    assert (
            "p-values statistics: min=3.2e-05 | mean=2.2e-03 | max=6.3e-03 | # missing=3 (5.6%)"
            in r_output
    )

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 5  # 5 lvs tested (all in the model file)
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert "LV4" in _lvs
    assert "LV5" in _lvs
    assert not output_data.isna().any().any()


def test_gls_cli_single_smultixcan_input_full_specify_gene_corrs(output_file):
    # gtex v8 and mashr
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using gene correlation file:" in r_output
    assert "sample-gene_corrs-gtex_v8-mashr.pkl" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert not output_data.isna().any().any()
    gtex_mashr_results = output_data
    output_file.unlink()

    # 1000 genomes and elastic net
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-en.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using gene correlation file:" in r_output
    assert "sample-gene_corrs-1000g-en.pkl" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert not output_data.isna().any().any()
    a1000g_en_results = output_data
    output_file.unlink()

    # results should be different across batches
    assert not np.allclose(
        gtex_mashr_results["beta"].to_numpy(),
        a1000g_en_results["beta"].to_numpy(),
    )
    assert not np.allclose(
        gtex_mashr_results["pvalue"].to_numpy(),
        a1000g_en_results["pvalue"].to_numpy(),
    )


def test_gls_cli_single_smultixcan_input_debug_use_ols(output_file):
    # first, run a standard GLS (using correlation matrix)
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using gene correlation file:" in r_output
    assert "sample-gene_corrs-gtex_v8-mashr.pkl" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert not output_data.isna().any().any()
    gls_results = output_data
    output_file.unlink()

    # now run an OLS model
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--model",
            "ols"
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using gene correlation file:" not in r_output
    assert "No gene correlations file specified" not in r_output
    assert "Using a Ordinary Least Squares (OLS) model" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert not output_data.isna().any().any()
    ols_results = output_data
    output_file.unlink()

    # results should be different across batches
    assert not np.allclose(
        gls_results["beta"].to_numpy(),
        ols_results["beta"].to_numpy(),
    )
    assert not np.allclose(
        gls_results["pvalue"].to_numpy(),
        ols_results["pvalue"].to_numpy(),
    )


def test_gls_cli_single_smultixcan_input_debug_use_ols_incompatible_arguments(
        output_file,
):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
            "--model",
            "ols"
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, " ")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert err.EXPECT_NO_GENE_CORR_FILE in r_output

    assert not output_file.exists()


def test_gls_cli_use_incompatible_parameters_batch_and_lv_list(output_file):
    # batch 1
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "-l",
            "LV1a LV2b LV3c",
            "--batch-id",
            "1",
            "--batch-n-splits",
            "3",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert err.INCOMPATIBLE_BATCH_ID_AND_LV_LIST in r_output


def test_gls_cli_batch_parameters_batch_n_splits_missing(output_file):
    # batch 1
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "1",
        ],

    )
    assert r is not None
    # Todo: Add helper function to process stdout with "\n" properly
    r_output = r.stdout.replace(os.linesep, " ")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert err.EXPECT_BOTH_BATCH_ARGS in r_output


def test_gls_cli_batch_parameters_batch_id_missing(output_file):
    # batch 1
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-n-splits",
            "3",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Both --batch-id and --batch-n-splits" in r_output


def test_gls_cli_batch_parameters_batch_id_value_invalid(output_file):
    # batch id is not an integer
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "a",
            "--batch-n-splits",
            "3",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Error: Invalid value for '--batch-id'" in r_output

    # batch id is negative
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "-1",
            "--batch-n-splits",
            "3",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert err.EXPECT_BATCH_ID_GT_ZERO  in r_output

    # batch id is zero
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "0",
            "--batch-n-splits",
            "3",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert err.EXPECT_BATCH_ID_GT_ZERO  in r_output

    # batch id is larger than --batch-n-splits
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "4",
            "--batch-n-splits",
            "3",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert err.INCOMPATIBLE_BATCH_ARGS in r_output


def test_gls_cli_batch_parameters_batch_n_splits_value_invalid(output_file):
    # batch n splits is not an integer
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "1",
            "--batch-n-splits",
            "a",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Error: Invalid value for '--batch-n-splits'" in r_output

    # batch n splits is smaller than batch id
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "3",
            "--batch-n-splits",
            "0",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert err.INCOMPATIBLE_BATCH_ARGS in r_output

    # batch n splits is smaller than batch id
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "3",
            "--batch-n-splits",
            "-2",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert err.INCOMPATIBLE_BATCH_ARGS in r_output

    # batch n splits larger than LVs in the model
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "3",
            "--batch-n-splits",
            "6",
            "--model",
            "ols"
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 2
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert (
            err.EXPECT_BATCH_N_SPLITS_LT_LVS
            in r_output
    )


def test_gls_cli_single_smultixcan_input_full_use_batches_with_n_splits(output_file):
    # batch 1
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "1",
            "--batch-n-splits",
            "3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 1 out of 3" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 2  # 5 lvs tested (all in the model file)
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert not output_data.isna().any().any()
    batch1_values = output_data
    output_file.unlink()

    # batch 2
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "2",
            "--batch-n-splits",
            "3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 2 out of 3" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 2  # 5 lvs tested (all in the model file)
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV3" in _lvs
    assert "LV4" in _lvs
    assert not output_data.isna().any().any()
    batch2_values = output_data
    output_file.unlink()

    # batch 3
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "3",
            "--batch-n-splits",
            "3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 3 out of 3" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 1  # 5 lvs tested (all in the model file)
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV5" in _lvs
    assert not output_data.isna().any().any()
    batch3_values = output_data

    # results should be different across batches
    assert not np.allclose(
        batch1_values["beta"].to_numpy(),
        batch2_values["beta"].to_numpy(),
    )
    assert not np.allclose(
        batch1_values["pvalue"].to_numpy(),
        batch2_values["pvalue"].to_numpy(),
    )

    assert not np.allclose(
        batch1_values["beta"].to_numpy(),
        batch3_values["beta"].to_numpy(),
    )
    assert not np.allclose(
        batch1_values["pvalue"].to_numpy(),
        batch3_values["pvalue"].to_numpy(),
    )

    assert not np.allclose(
        batch2_values["beta"].to_numpy(),
        batch3_values["beta"].to_numpy(),
    )
    assert not np.allclose(
        batch2_values["pvalue"].to_numpy(),
        batch3_values["pvalue"].to_numpy(),
    )


def test_gls_cli_single_smultixcan_input_full_use_batches_with_n_splits_chunks_same_size_of_1(
        output_file,
):
    # batch 1
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "1",
            "--batch-n-splits",
            "5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 1 out of 5" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 1  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # batch 2
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "2",
            "--batch-n-splits",
            "5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 2 out of 5" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 1  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV2" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # batch 3
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "3",
            "--batch-n-splits",
            "5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 3 out of 5" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 1  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV3" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # batch 4
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "4",
            "--batch-n-splits",
            "5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 4 out of 5" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 1  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV4" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # batch 5
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "5",
            "--batch-n-splits",
            "5",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 5 out of 5" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 1  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV5" in _lvs
    assert not output_data.isna().any().any()


def test_gls_cli_single_smultixcan_input_full_use_batches_with_n_splits_is_1(
        output_file,
):
    # batch 1
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--batch-id",
            "1",
            "--batch-n-splits",
            "1",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 1 out of 1" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 5  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert "LV4" in _lvs
    assert "LV5" in _lvs
    assert not output_data.isna().any().any()


def test_gls_cli_single_smultixcan_input_full_use_batches_with_n_splits_problematic_with_9_lvs(
        output_file,
):
    # if the chuncker of LVs is not doing it right, here it wont separate the list of LVs into exactly the same
    # number of chunks requested by --batch-n-splits

    # batch 1
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model-n9.pkl"),
            "--batch-id",
            "1",
            "--batch-n-splits",
            "4",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 1 out of 4" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 3
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # batch 2
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model-n9.pkl"),
            "--batch-id",
            "2",
            "--batch-n-splits",
            "4",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 2 out of 4" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 2  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV4" in _lvs
    assert "LV5" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # batch 3
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model-n9.pkl"),
            "--batch-id",
            "3",
            "--batch-n-splits",
            "4",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 3 out of 4" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 2  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV6" in _lvs
    assert "LV7" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # batch 4
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model-n9.pkl"),
            "--batch-id",
            "4",
            "--batch-n-splits",
            "4",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-gtex_v8-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using batch 4 out of 4" in r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 2  # 1 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    _lvs = set(output_data["lv"].tolist())
    assert "LV8" in _lvs
    assert "LV9" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()


def test_gls_cli_use_covar_gene_size(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    assert output_data["pvalue"].between(0.0, 1.0, inclusive="neither").all()
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # run using gene_size as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_size",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output

    assert output_file.exists()
    output_data2 = pd.read_csv(output_file, sep="\t")
    assert output_data2.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data2.columns
    assert "beta" in output_data2.columns
    assert "pvalue" in output_data2.columns
    assert output_data2["pvalue"].between(0.0, 1.0, inclusive="neither").all()
    _lvs = set(output_data2["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data2.isna().any().any()

    # make sure results differ
    assert not np.allclose(
        output_data["beta"].to_numpy(),
        output_data2["beta"].to_numpy(),
    )

    assert not np.allclose(
        output_data["beta_se"].to_numpy(),
        output_data2["beta_se"].to_numpy(),
    )

    assert not np.allclose(
        output_data["pvalue"].to_numpy(),
        output_data2["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_gene_density(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    assert output_data["pvalue"].between(0.0, 1.0, inclusive="neither").all()
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # run using gene_density as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_density",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_density" in r_output

    assert output_file.exists()
    output_data2 = pd.read_csv(output_file, sep="\t")
    assert output_data2.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data2.columns
    assert "beta" in output_data2.columns
    assert "pvalue" in output_data2.columns
    assert output_data2["pvalue"].between(0.0, 1.0, inclusive="neither").all()
    _lvs = set(output_data2["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data2.isna().any().any()

    # make sure results differ
    assert not np.allclose(
        output_data["beta"].to_numpy(),
        output_data2["beta"].to_numpy(),
    )

    assert not np.allclose(
        output_data["beta_se"].to_numpy(),
        output_data2["beta_se"].to_numpy(),
    )

    assert not np.allclose(
        output_data["pvalue"].to_numpy(),
        output_data2["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_gene_n_snps_used_without_cohort_metadata_dir_specified(
        output_file,
):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_n_snps_used",
        ],

    )
    assert r is not None
    assert r.exit_code == 1
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None
    assert len(r_output) > 1, r_output
    # print(r_output)
    # assert "ERROR" in r_output
    assert "cohort metadata folder must be provided" in r_output


def test_gls_cli_use_covar_gene_n_snps_used(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    assert output_data["pvalue"].between(0.0, 1.0, inclusive="neither").all()
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # run using gene_density as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_n_snps_used",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_n_snps_used" in r_output

    assert output_file.exists()
    output_data2 = pd.read_csv(output_file, sep="\t")
    assert output_data2.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data2.columns
    assert "beta" in output_data2.columns
    assert "pvalue" in output_data2.columns
    assert output_data2["pvalue"].between(0.0, 1.0, inclusive="neither").all()
    _lvs = set(output_data2["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data2.isna().any().any()

    # make sure results differ
    assert not np.allclose(
        output_data["beta"].to_numpy(),
        output_data2["beta"].to_numpy(),
    )

    assert not np.allclose(
        output_data["beta_se"].to_numpy(),
        output_data2["beta_se"].to_numpy(),
    )

    assert not np.allclose(
        output_data["pvalue"].to_numpy(),
        output_data2["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_gene_n_snps_used_density(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    output_data = pd.read_csv(output_file, sep="\t")
    assert output_data.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data.columns
    assert "beta" in output_data.columns
    assert "pvalue" in output_data.columns
    assert output_data["pvalue"].between(0.0, 1.0, inclusive="neither").all()
    _lvs = set(output_data["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data.isna().any().any()
    output_file.unlink()

    # run using gene_n_snps_used_density as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_n_snps_used_density",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_n_snps_used_density" in r_output

    assert output_file.exists()
    output_data2 = pd.read_csv(output_file, sep="\t")
    assert output_data2.shape[0] == 3  # 3 lvs tested
    assert "lv" in output_data2.columns
    assert "beta" in output_data2.columns
    assert "pvalue" in output_data2.columns
    assert output_data2["pvalue"].between(0.0, 1.0, inclusive="neither").all()
    _lvs = set(output_data2["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not output_data2.isna().any().any()

    # make sure results differ
    assert not np.allclose(
        output_data["beta"].to_numpy(),
        output_data2["beta"].to_numpy(),
    )

    assert not np.allclose(
        output_data["beta_se"].to_numpy(),
        output_data2["beta_se"].to_numpy(),
    )

    assert not np.allclose(
        output_data["pvalue"].to_numpy(),
        output_data2["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_gene_size_and_its_log(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    results_without_covars = pd.read_csv(output_file, sep="\t")
    assert results_without_covars.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_without_covars.columns
    assert "beta" in results_without_covars.columns
    assert "pvalue" in results_without_covars.columns
    assert (
        results_without_covars["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_without_covars["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_without_covars.isna().any().any()
    output_file.unlink()

    # run using gene_size as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_size",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output

    assert output_file.exists()
    results_covar_gene_size = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_size.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_size.columns
    assert "beta" in results_covar_gene_size.columns
    assert "pvalue" in results_covar_gene_size.columns
    assert (
        results_covar_gene_size["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_size["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_size.isna().any().any()
    output_file.unlink()

    # run using gene_size and gene_size_log
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_size gene_size_log",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output
    assert "gene_size_log" in r_output

    assert output_file.exists()
    results_covar_gene_size_and_log = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_size_and_log.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_size_and_log.columns
    assert "beta" in results_covar_gene_size_and_log.columns
    assert "pvalue" in results_covar_gene_size_and_log.columns
    assert (
        results_covar_gene_size_and_log["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_size_and_log["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_size_and_log.isna().any().any()

    # make sure results differ
    # no covars vs gene size + log
    assert not np.allclose(
        results_without_covars["beta"].to_numpy(),
        results_covar_gene_size_and_log["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_without_covars["pvalue"].to_numpy(),
        results_covar_gene_size_and_log["pvalue"].to_numpy(),
    )

    # gene size covar vs gene size + log
    assert not np.allclose(
        results_covar_gene_size["beta"].to_numpy(),
        results_covar_gene_size_and_log["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_covar_gene_size["pvalue"].to_numpy(),
        results_covar_gene_size_and_log["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_gene_density_and_its_log(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    results_without_covars = pd.read_csv(output_file, sep="\t")
    assert results_without_covars.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_without_covars.columns
    assert "beta" in results_without_covars.columns
    assert "pvalue" in results_without_covars.columns
    assert (
        results_without_covars["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_without_covars["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_without_covars.isna().any().any()
    output_file.unlink()

    # run using gene_density as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_density",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_density" in r_output

    assert output_file.exists()
    results_covar_gene_density = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_density.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_density.columns
    assert "beta" in results_covar_gene_density.columns
    assert "pvalue" in results_covar_gene_density.columns
    assert (
        results_covar_gene_density["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_density["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_density.isna().any().any()
    output_file.unlink()

    # run using gene_density and gene_size_log
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_density gene_density_log",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_density" in r_output
    assert "gene_density_log" in r_output

    assert output_file.exists()
    results_covar_gene_density_and_log = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_density_and_log.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_density_and_log.columns
    assert "beta" in results_covar_gene_density_and_log.columns
    assert "pvalue" in results_covar_gene_density_and_log.columns
    assert (
        results_covar_gene_density_and_log["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_density_and_log["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_density_and_log.isna().any().any()

    # make sure results differ
    # no covars vs gene density + log
    assert not np.allclose(
        results_without_covars["beta"].to_numpy(),
        results_covar_gene_density_and_log["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_without_covars["pvalue"].to_numpy(),
        results_covar_gene_density_and_log["pvalue"].to_numpy(),
    )

    # gene density covar vs gene density + log
    assert not np.allclose(
        results_covar_gene_density["beta"].to_numpy(),
        results_covar_gene_density_and_log["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_covar_gene_density["pvalue"].to_numpy(),
        results_covar_gene_density_and_log["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_gene_n_snps_used_and_its_log(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    results_without_covars = pd.read_csv(output_file, sep="\t")
    assert results_without_covars.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_without_covars.columns
    assert "beta" in results_without_covars.columns
    assert "pvalue" in results_without_covars.columns
    assert (
        results_without_covars["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_without_covars["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_without_covars.isna().any().any()
    output_file.unlink()

    # run using gene_n_snps_used as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_n_snps_used",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_n_snps_used" in r_output

    assert output_file.exists()
    results_covar_gene_n_snps_used = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_n_snps_used.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_n_snps_used.columns
    assert "beta" in results_covar_gene_n_snps_used.columns
    assert "pvalue" in results_covar_gene_n_snps_used.columns
    assert (
        results_covar_gene_n_snps_used["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_n_snps_used["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_n_snps_used.isna().any().any()
    output_file.unlink()

    # run using gene_n_snps_used and gene_n_snps_used_log
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_n_snps_used gene_n_snps_used_log",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_n_snps_used" in r_output
    assert "gene_n_snps_used_log" in r_output

    assert output_file.exists()
    results_covar_gene_n_snps_used_and_log = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_n_snps_used_and_log.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_n_snps_used_and_log.columns
    assert "beta" in results_covar_gene_n_snps_used_and_log.columns
    assert "pvalue" in results_covar_gene_n_snps_used_and_log.columns
    assert (
        results_covar_gene_n_snps_used_and_log["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_n_snps_used_and_log["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_n_snps_used_and_log.isna().any().any()

    # make sure results differ
    # no covars vs gene size + log
    assert not np.allclose(
        results_without_covars["beta"].to_numpy(),
        results_covar_gene_n_snps_used_and_log["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_without_covars["pvalue"].to_numpy(),
        results_covar_gene_n_snps_used_and_log["pvalue"].to_numpy(),
    )

    # gene size covar vs gene size + log
    assert not np.allclose(
        results_covar_gene_n_snps_used["beta"].to_numpy(),
        results_covar_gene_n_snps_used_and_log["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_covar_gene_n_snps_used["pvalue"].to_numpy(),
        results_covar_gene_n_snps_used_and_log["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_gene_n_snps_used_density_and_its_log(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    results_without_covars = pd.read_csv(output_file, sep="\t")
    assert results_without_covars.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_without_covars.columns
    assert "beta" in results_without_covars.columns
    assert "pvalue" in results_without_covars.columns
    assert (
        results_without_covars["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_without_covars["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_without_covars.isna().any().any()
    output_file.unlink()

    # run using gene_n_snps_used_density as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_n_snps_used_density",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_n_snps_used_density" in r_output

    assert output_file.exists()
    results_covar_gene_n_snps_used_density = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_n_snps_used_density.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_n_snps_used_density.columns
    assert "beta" in results_covar_gene_n_snps_used_density.columns
    assert "pvalue" in results_covar_gene_n_snps_used_density.columns
    assert (
        results_covar_gene_n_snps_used_density["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_n_snps_used_density["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_n_snps_used_density.isna().any().any()
    output_file.unlink()

    # run using gene_n_snps_used_density and gene_n_snps_used_density_log
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_n_snps_used_density gene_n_snps_used_density_log",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_n_snps_used_density" in r_output
    assert "gene_n_snps_used_density_log" in r_output

    assert output_file.exists()
    results_covar_gene_n_snps_used_density_and_log = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_n_snps_used_density_and_log.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_n_snps_used_density_and_log.columns
    assert "beta" in results_covar_gene_n_snps_used_density_and_log.columns
    assert "pvalue" in results_covar_gene_n_snps_used_density_and_log.columns
    assert (
        results_covar_gene_n_snps_used_density_and_log["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_n_snps_used_density_and_log["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_n_snps_used_density_and_log.isna().any().any()

    # make sure results differ
    # no covars vs gene size + log
    assert not np.allclose(
        results_without_covars["beta"].to_numpy(),
        results_covar_gene_n_snps_used_density_and_log["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_without_covars["pvalue"].to_numpy(),
        results_covar_gene_n_snps_used_density_and_log["pvalue"].to_numpy(),
    )

    # gene size covar vs gene size + log
    assert not np.allclose(
        results_covar_gene_n_snps_used_density["beta"].to_numpy(),
        results_covar_gene_n_snps_used_density_and_log["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_covar_gene_n_snps_used_density["pvalue"].to_numpy(),
        results_covar_gene_n_snps_used_density_and_log["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_log_without_specifying_original_covariate(
        output_file,
):
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_density_log gene_size_log",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    assert r_output is not None
    assert len(r_output) > 1, r_output
    # print(r_output)
    assert r.exit_code == 1
    # assert "ERROR" in r_output
    assert "covar has to be selected as well" in r_output


def test_gls_cli_use_covar_all(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    results_without_covars = pd.read_csv(output_file, sep="\t")
    assert results_without_covars.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_without_covars.columns
    assert "beta" in results_without_covars.columns
    assert "pvalue" in results_without_covars.columns
    assert (
        results_without_covars["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_without_covars["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_without_covars.isna().any().any()
    output_file.unlink()

    # run using gene_density as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_density",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_density" in r_output

    assert output_file.exists()
    results_covar_gene_density = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_density.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_density.columns
    assert "beta" in results_covar_gene_density.columns
    assert "pvalue" in results_covar_gene_density.columns
    assert (
        results_covar_gene_density["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_density["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_density.isna().any().any()
    output_file.unlink()

    # run using gene_size as covariate
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_size",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output

    assert output_file.exists()
    results_covar_gene_size = pd.read_csv(output_file, sep="\t")
    assert results_covar_gene_size.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_gene_size.columns
    assert "beta" in results_covar_gene_size.columns
    assert "pvalue" in results_covar_gene_size.columns
    assert (
        results_covar_gene_size["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_gene_size["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_gene_size.isna().any().any()
    output_file.unlink()

    # run using all available covars
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "all",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    from phenoplier.commands.util.enums import CovarOptions
    assert all(c.value in r_output for c in CovarOptions if c != CovarOptions.ALL and c != CovarOptions.DEFAULT), r_output

    assert output_file.exists()
    results_covar_all = pd.read_csv(output_file, sep="\t")
    assert results_covar_all.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_all.columns
    assert "beta" in results_covar_all.columns
    assert "pvalue" in results_covar_all.columns
    assert (
        results_covar_all["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_all["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_all.isna().any().any()

    # make sure results differ
    # no covars vs all covars
    assert not np.allclose(
        results_without_covars["beta"].to_numpy(),
        results_covar_all["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_without_covars["pvalue"].to_numpy(),
        results_covar_all["pvalue"].to_numpy(),
    )

    # gene size covar vs all covars
    assert not np.allclose(
        results_covar_gene_size["beta"].to_numpy(),
        results_covar_all["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_covar_gene_size["pvalue"].to_numpy(),
        results_covar_all["pvalue"].to_numpy(),
    )

    # gene density covar vs all covars
    assert not np.allclose(
        results_covar_gene_density["beta"].to_numpy(),
        results_covar_all["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_covar_gene_density["pvalue"].to_numpy(),
        results_covar_all["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_all_vs_all_specified_separately(output_file):
    # run first without covariates
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output

    assert output_file.exists()
    results_without_covars = pd.read_csv(output_file, sep="\t")
    assert results_without_covars.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_without_covars.columns
    assert "beta" in results_without_covars.columns
    assert "pvalue" in results_without_covars.columns
    assert (
        results_without_covars["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_without_covars["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_without_covars.isna().any().any()
    output_file.unlink()

    # run using all covariates specified separately
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "gene_size gene_size_log gene_density gene_density_log gene_n_snps_used gene_n_snps_used_log gene_n_snps_used_density gene_n_snps_used_density_log",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output

    assert output_file.exists()
    results_covar_all_separately = pd.read_csv(output_file, sep="\t")
    assert results_covar_all_separately.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_all_separately.columns
    assert "beta" in results_covar_all_separately.columns
    assert "pvalue" in results_covar_all_separately.columns
    assert (
        results_covar_all_separately["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_all_separately["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_all_separately.isna().any().any()
    output_file.unlink()

    # run using all available covars
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-l",
            "LV1 LV2 LV3",
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "all",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--dup-genes-action",
            "keep-first",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output
    assert "gene_size_log" in r_output
    assert "gene_density" in r_output
    assert "gene_density_log" in r_output

    assert output_file.exists()
    results_covar_all = pd.read_csv(output_file, sep="\t")
    assert results_covar_all.shape[0] == 3  # 3 lvs tested
    assert "lv" in results_covar_all.columns
    assert "beta" in results_covar_all.columns
    assert "pvalue" in results_covar_all.columns
    assert (
        results_covar_all["pvalue"]
        .between(0.0, 1.0, inclusive="neither")
        .all()
    )
    _lvs = set(results_covar_all["lv"].tolist())
    assert "LV1" in _lvs
    assert "LV2" in _lvs
    assert "LV3" in _lvs
    assert not results_covar_all.isna().any().any()

    # compare results
    # no covars vs all covars should be different
    assert not np.allclose(
        results_without_covars["beta"].to_numpy(),
        results_covar_all["beta"].to_numpy(),
    )

    assert not np.allclose(
        results_without_covars["pvalue"].to_numpy(),
        results_covar_all["pvalue"].to_numpy(),
    )

    # all separately vs "all" should be equal
    assert np.array_equal(
        results_covar_all_separately["beta"].to_numpy(),
        results_covar_all["beta"].to_numpy(),
    )

    assert np.array_equal(
        results_covar_all_separately["pvalue"].to_numpy(),
        results_covar_all["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_gene_size_and_gene_density_lv45_random_phenotype_6(
        output_file,
        full_gene_corrs_filepath,
):
    # in this test, I make sure that the output values are the expected ones
    # generated in notebook nbs/15_gsa_gls/misc/10_10-gls-generate_cases-cases.ipynb
    # run using all covariates specified separately
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno6-gtex_v8-mashr-smultixcan.txt.gz"),
            "-o",
            output_file,
            "-l",
            "LV45",
            "-g",
            full_gene_corrs_filepath,
            "--dup-genes-action",
            "keep-first",
            "--covars",
            "gene_size gene_density",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output
    assert "gene_density" in r_output

    assert output_file.exists()
    results = pd.read_csv(output_file, sep="\t")

    assert results.shape[0] == 1  # only 1 LV tested
    assert "lv" in results.columns
    assert "beta" in results.columns
    assert "beta_se" in results.columns
    assert "t" in results.columns
    # assert "pvalue_twosided" in results.columns
    assert "pvalue" in results.columns

    # assert results["pvalue_twosided"].between(0.0, 1.0, inclusive="neither").all()
    assert results["pvalue"].between(0.0, 1.0, inclusive="neither").all()

    _lvs = set(results["lv"].tolist())
    assert "LV45" in _lvs
    assert not results.isna().any().any()

    # check values
    exp_coef = -0.10018201664770203
    exp_coef_se = 0.09298021617384379
    exp_tvalue = -1.0774551917624404
    exp_pval_twosided = 0.28131731604765614
    exp_pval_onesided = 0.859341341976172

    assert results.iloc[0].loc["beta"] == pytest.approx(exp_coef, rel=1e-2)
    assert results.iloc[0].loc["beta_se"] == pytest.approx(exp_coef_se, rel=1e-2)
    assert results.iloc[0].loc["t"] == pytest.approx(exp_tvalue, rel=1e-2)
    # assert results.iloc[0].loc["pvalue_twosided"] == pytest.approx(
    #     exp_pval_twosided, rel=1e-2
    # )
    assert results.iloc[0].loc["pvalue"] == pytest.approx(
        exp_pval_onesided, rel=1e-2
    )


def test_gls_cli_use_covar_gene_size_and_gene_density_lv455_random_phenotype_6(
        output_file,
        full_gene_corrs_filepath,
):
    # in this test, I make sure that the output values are the expected ones
    # generated in notebook nbs/15_gsa_gls/misc/10_10-gls-generate_cases-cases.ipynb
    # run using all covariates specified separately
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno6-gtex_v8-mashr-smultixcan.txt.gz"),
            "-o",
            output_file,
            "-l",
            "LV455",
            "-g",
            full_gene_corrs_filepath,
            "--dup-genes-action",
            "keep-first",
            "--covars",
            "gene_size gene_density",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output
    assert "gene_density" in r_output

    assert output_file.exists()
    results = pd.read_csv(output_file, sep="\t")

    assert results.shape[0] == 1  # only 1 LV tested
    assert "lv" in results.columns
    assert "beta" in results.columns
    assert "beta_se" in results.columns
    assert "t" in results.columns
    # assert "pvalue_twosided" in results.columns
    assert "pvalue" in results.columns

    # assert results["pvalue_twosided"].between(0.0, 1.0, inclusive="neither").all()
    assert results["pvalue"].between(0.0, 1.0, inclusive="neither").all()

    _lvs = set(results["lv"].tolist())
    assert "LV455" in _lvs
    assert not results.isna().any().any()

    # check values
    exp_coef = 0.0784587858266203
    exp_coef_se = 0.1152051853461905
    exp_tvalue = 0.6810351946472929
    exp_pval_twosided = 0.4958737072729271
    exp_pval_onesided = 0.24793685363646356

    assert results.iloc[0].loc["beta"] == pytest.approx(exp_coef, rel=1e-2)
    assert results.iloc[0].loc["beta_se"] == pytest.approx(exp_coef_se, rel=1e-2)
    assert results.iloc[0].loc["t"] == pytest.approx(exp_tvalue, rel=1e-2)
    # assert results.iloc[0].loc["pvalue_twosided"] == pytest.approx(
    #     exp_pval_twosided, rel=1e-2
    # )
    assert results.iloc[0].loc["pvalue"] == pytest.approx(
        exp_pval_onesided, rel=1e-2
    )


def test_gls_cli_use_covar_gene_size_and_gene_density_lv45_and_lv455_random_phenotype_6(
        output_file, full_gene_corrs_filepath
):
    # in this test, I make sure that the output values are the expected ones
    # generated in notebook nbs/15_gsa_gls/misc/10_10-gls-generate_cases-cases.ipynb
    #
    # the difference with the previous test, is that this one computes two LVs
    # in the same run, checking results are the same as if run separately
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno6-gtex_v8-mashr-smultixcan.txt.gz"),
            "-o",
            output_file,
            "-l",
            "LV45 LV455",
            "-g",
            full_gene_corrs_filepath,
            "--dup-genes-action",
            "keep-first",
            "--covars",
            "gene_size gene_density",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output
    assert "gene_density" in r_output

    assert output_file.exists()
    results = pd.read_csv(output_file, sep="\t")

    assert results.shape[0] == 2  # only 1 LV tested
    assert "lv" in results.columns
    assert "beta" in results.columns
    assert "beta_se" in results.columns
    assert "t" in results.columns
    # assert "pvalue_twosided" in results.columns
    assert "pvalue" in results.columns

    # assert results["pvalue_twosided"].between(0.0, 1.0, inclusive="neither").all()
    assert results["pvalue"].between(0.0, 1.0, inclusive="neither").all()

    _lvs = set(results["lv"].tolist())
    assert "LV45" in _lvs
    assert "LV455" in _lvs
    assert not results.isna().any().any()

    results = results.set_index("lv")

    # check values for LV45
    _lv_code = "LV45"

    exp_coef = -0.10052902446730924
    exp_coef_se = 0.09300042682237371
    exp_tvalue = -1.0809522913192084
    exp_pval_twosided = 0.27975882566803706
    exp_pval_onesided = 0.8601205871659815

    assert results.loc[_lv_code, "beta"] == pytest.approx(exp_coef, rel=1e-2)
    assert results.loc[_lv_code, "beta_se"] == pytest.approx(exp_coef_se, rel=1e-2)
    assert results.loc[_lv_code, "t"] == pytest.approx(exp_tvalue, rel=1e-2)
    # assert results.loc[_lv_code, "pvalue_twosided"] == pytest.approx(
    #     exp_pval_twosided, rel=1e-2
    # )
    assert results.loc[_lv_code, "pvalue"] == pytest.approx(
        exp_pval_onesided, rel=1e-2
    )


def test_gls_cli_use_covar_debug_use_ols_vs_ols_without_covars(output_file):
    # tests that covars are used when debug_use_ols is employed

    # first, run OLS without covars
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--model",
            "ols",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using covariates: " not in r_output

    assert output_file.exists()
    results_ols_no_covars = pd.read_csv(output_file, sep="\t")
    assert results_ols_no_covars.shape[0] == 5  # 5 lvs tested
    assert not results_ols_no_covars.isna().any().any()
    output_file.unlink()

    # now run an OLS with covars
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--covars",
            "all",
            "--dup-genes-action",
            "keep-first",
            "--model",
            "ols",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using gene correlation file:" not in r_output
    assert "No gene correlations file specified" not in r_output
    assert "Using a Ordinary Least Squares (OLS) model" in r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output
    assert "gene_size_log" in r_output
    assert "gene_density" in r_output
    assert "gene_density_log" in r_output

    assert output_file.exists()
    results_ols = pd.read_csv(output_file, sep="\t")
    assert results_ols.shape[0] == results_ols_no_covars.shape[0]
    assert not results_ols.isna().any().any()

    # results should be different across batches
    assert not np.allclose(
        results_ols_no_covars["beta"].to_numpy(),
        results_ols["beta"].to_numpy(),
    )
    assert not np.allclose(
        results_ols_no_covars["pvalue"].to_numpy(),
        results_ols["pvalue"].to_numpy(),
    )


def test_gls_cli_use_covar_debug_use_ols_vs_gls(output_file):
    # tests that covars are used when debug_use_ols is employed

    # first, run GLS with covars
    # run using all available covars
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "-g",
            str(DATA_DIR / "sample-gene_corrs-1000g-mashr.pkl"),
            "--covars",
            "all",
            "--dup-genes-action",
            "keep-first",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using gene correlation file:" in r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output
    assert "gene_size_log" in r_output
    assert "gene_density" in r_output
    assert "gene_density_log" in r_output

    assert output_file.exists()
    results_gls = pd.read_csv(output_file, sep="\t")
    assert results_gls.shape[0] == 5  # 5 lvs tested
    assert not results_gls.isna().any().any()
    output_file.unlink()

    # now run an OLS with covars
    r = runner.invoke(
        cli.app,
        [
            "run",
            "regression",
            "-i",
            str(DATA_DIR / "random.pheno0-smultixcan-full.txt"),
            "-o",
            output_file,
            "-f",
            str(DATA_DIR / "sample-lv-model.pkl"),
            "--covars",
            "all",
            "--dup-genes-action",
            "keep-first",
            "--cohort-metadata-dir",
            str(DATA_DIR / "cohort_1000g_eur_metadata"),
            "--model",
            "ols",
        ],

    )
    assert r is not None
    r_output = r.stdout.replace(os.linesep, "")
    # print("\n" + r_output)

    assert r.exit_code == 0
    assert r_output is not None
    assert len(r_output) > 1, r_output
    assert "Using gene correlation file:" not in r_output
    assert "No gene correlations file specified" not in r_output
    assert "Using a Ordinary Least Squares (OLS) model" in r_output
    assert "Using covariates: " in r_output
    assert "gene_size" in r_output
    assert "gene_size_log" in r_output
    assert "gene_density" in r_output
    assert "gene_density_log" in r_output

    assert output_file.exists()
    results_ols = pd.read_csv(output_file, sep="\t")
    assert results_ols.shape[0] == results_gls.shape[0]
    assert not results_ols.isna().any().any()

    # results should be different across batches
    assert not np.allclose(
        results_gls["beta"].to_numpy(),
        results_ols["beta"].to_numpy(),
    )
    assert not np.allclose(
        results_gls["pvalue"].to_numpy(),
        results_ols["pvalue"].to_numpy(),
    )
