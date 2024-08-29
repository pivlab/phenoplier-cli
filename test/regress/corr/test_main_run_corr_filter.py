import os
from pathlib import Path
import logging

from typer.testing import CliRunner
from pytest import mark
from phenoplier import cli
from phenoplier.config import settings as conf
from phenoplier.commands.invoker import invoke_corr_filter
from test.utils import get_test_output_dir, load_pickle_or_gz_pickle, compare_dataframes_close

logger = logging.getLogger(__name__)

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


# Define the test output directory
# Todo: organize test data dir the same way as test output dir
output_dir_base = get_test_output_dir(Path(__file__))
prev_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/4-postprocess/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr"
ref_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/5-filter/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr"


@mark.skipif(IN_GITHUB_ACTIONS, reason="Slow and computationally expensive test, skip in GitHub Actions")
@mark.corr
@mark.order(-2)
@mark.parametrize(
    "cohort, reference_panel, eqtl_model, distances, genes_symbols, output_dir",
    [
        (
                "phenomexcan_rapid_gwas",
                "GTEX_V8",
                "MASHR",
                5,
                prev_data_dir / "gene_corrs-symbols.pkl",
                output_dir_base
        ),
        # Add more test cases here as needed
    ]
)
def test_cli_command(cohort, reference_panel, eqtl_model, distances, genes_symbols, output_dir):
    # Build the command
    suc, msg = invoke_corr_filter(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        distances=distances,
        genes_symbols=genes_symbols,
        output_dir=output_dir
    )

    assert suc, msg

    filename = "gene_corrs-symbols-within_distance_5mb.pkl.gz"
    test_output = output_dir / filename
    ref_output = ref_data_dir / filename
    # Assert the output file exists
    assert test_output.exists(), f"Output file {test_output} does not exist"
    # Load the pickled dataframes
    df1 = load_pickle_or_gz_pickle(test_output)
    df2 = load_pickle_or_gz_pickle(ref_output)
    # Assert the output matches the expected output
    assert compare_dataframes_close(df1, df2), f"Output file {test_output} does not match expected output"
