import os
import logging
import random
import zipfile
from pathlib import Path

from typer.testing import CliRunner
from pytest import mark
from phenoplier import cli
from phenoplier.commands.invoker import invoke_corr_generate
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
    "-m {eqtl_model} "
    "-l {lv_code} "
    "-e {lv_percentile} "
    "-g {genes_symbols_dir} "
    "-o {output_dir} "
)

# Define the test output directory
# Todo: organize test data dir the same way as test output dir
output_dir_base = get_test_output_dir(Path(__file__))
prev_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/5-filter/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr"
ref_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/6-generate/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr"
ref_zip_file = ref_data_dir / "gene_corrs-symbols-within_distance_5mb.per_lv.zip"

# Create a directory for extraction
temp_extract_dir = output_dir_base / "ref"
if not temp_extract_dir.exists():
    temp_extract_dir.mkdir(exist_ok=True)
    # Unzip the file
    with zipfile.ZipFile(ref_zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)


@mark.skipif(IN_GITHUB_ACTIONS, reason="Slow and computationally expensive test, skip in GitHub Actions")
@mark.corr
@mark.order(6)
@mark.parametrize(
    "cohort, reference_panel, eqtl_model, lv_code, lv_percentile, genes_symbols_dir, output_dir",
    [
        (
                "phenomexcan_rapid_gwas",
                "GTEX_V8",
                "MASHR",
                lv_code,
                0.01,
                prev_data_dir,
                output_dir_base
        )
        # Use sampling test to reduce runtime
        for lv_code in random.sample(range(1, 988), 5)
    ]
)
def test_cli_command(cohort, reference_panel, eqtl_model, lv_code, lv_percentile, genes_symbols_dir, output_dir):
    # Build the command
    suc, msg = invoke_corr_generate(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        lv_code=lv_code,
        lv_percentile=lv_percentile,
        genes_symbols_dir=genes_symbols_dir,
        output_dir=output_dir,
    )

    assert suc, msg

    filenames = genes_symbols_dir.glob("gene_corrs-symbols*.pkl")
    for filename in filenames:
        filename = filename.stem
        test_output = (output_dir / filename).with_suffix(".per_lv")
        ref_output = (temp_extract_dir / filename).with_suffix(".per_lv")
        # Assert the output file exists
        assert test_output.exists(), f"Output directory {test_output} does not exist"
        files = ("gene_names.npz", f"LV{lv_code}_corr_mat.npz", f"LV{lv_code}.npz")
        logger.info(f"Comparing {test_output} and {ref_output}...")
        success, message = compare_npz_files_in_dirs(test_output, ref_output, include_files=files)
        assert success, message
