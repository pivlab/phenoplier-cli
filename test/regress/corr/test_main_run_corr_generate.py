import os
import logging
import random
from pathlib import Path

from typer.testing import CliRunner
from pytest import mark
from phenoplier import cli
from phenoplier.config import settings as conf
from test.utils import get_test_output_dir, compare_npz_files_in_dirs

logger = logging.getLogger(__name__)

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

# Define the placeholders in the command
_BASE_COMMAND = (
    "run gene-corr generate "
    "-c {cohort} "
    "-r {reference_panel} "
    "-m {eqtl_models} "
    "-l {lv_code} "
    "-e {lv_percentile} "
    "-g {genes_symbols_dir} "
    "-o {output_dir} "
)

# Define the test output directory
# Todo: organize test data dir the same way as test output dir
output_dir_base = get_test_output_dir(Path(__file__))
test_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/99_all_results/mashr/"


@mark.skipif(IN_GITHUB_ACTIONS, reason="Slow and computationally expensive test, skip in GitHub Actions")
# Parameterize the test cases
@mark.parametrize(
    "cohort, reference_panel, eqtl_models, lv_code, lv_percentile, genes_symbols_dir, output_dir",
    [
        (
                "phenomexcan_rapid_gwas",
                "GTEX_V8",
                "MASHR",
                lv_code,
                0.01,
                test_data_dir,
                output_dir_base
        )
        # Use sampling test to reduce runtime
        for lv_code in random.sample(range(1, 988), 1)
    ]
)
def test_cli_command(cohort, reference_panel, eqtl_models, lv_code, lv_percentile, genes_symbols_dir, output_dir):
    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_models=eqtl_models,
        lv_code=lv_code,
        lv_percentile=lv_percentile,
        genes_symbols_dir=genes_symbols_dir,
        output_dir=output_dir,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    logger.info(f"Running command: {command}")
    # Assert the command ran successfully
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"

    filenames = genes_symbols_dir.glob("gene_corrs-symbols*.pkl")
    for filename in filenames:
        filename = filename.stem
        test_output = (output_dir / filename).with_suffix(".per_lv")
        ref_output = (test_data_dir / filename).with_suffix(".per_lv")
        # Assert the output file exists
        assert test_output.exists(), f"Output directory {test_output} does not exist"
        files = ("gene_names.npz", f"LV{lv_code}_corr_mat.npz", f"LV{lv_code}.npz")
        logger.info(f"Comparing {test_output} and {ref_output}...")
        success, message = compare_npz_files_in_dirs(test_output, ref_output, include_files=files)
        assert success, message
