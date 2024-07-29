import os
from pathlib import Path
import logging

from typer.testing import CliRunner
from pytest import mark

from phenoplier import cli
from phenoplier.config import settings as conf
from phenoplier.commands.invoker import invoke_corr_preprocess
from test.utils import get_test_output_dir, compare_dataframes_equal, load_pickle

logger = logging.getLogger(__name__)

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

# Define the placeholders in the command
_BASE_COMMAND = (
    "run gene-corr pipeline "
    "-c {cohort} "
    "-r {reference_panel} "
    "-m {eqtl_models} "
    "-g {gwas_file} "
    "-s {spredixcan_dir} "
    "-n {output_file_name} "
    "-f {smultixcan_file} "
    # "-o {output_dir}"
)

# Define the test output directory
# Todo: organize test data dir the same way as test output dir
output_dir_base = get_test_output_dir(Path(__file__))
test_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/99_all_results/mashr/"


@mark.skipif(IN_GITHUB_ACTIONS, reason="Data has not been setup in Github Actions yet. Local test only.")
@mark.corr
# Parameterize the test cases
@mark.parametrize(
    "cohort, gwas_file, spredixcan_dir, output_file_name, smultixcan_file, reference_panel, eqtl_models, output_dir",
    [
        (
                "phenomexcan_rapid_gwas",
                "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gwas_parsing/full/22617_7112.txt.gz",
                "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gene_assoc/spredixcan/rapid_gwas_project/22617_7112",
                "22617_7112-gtex_v8-{tissue}-2018_10.csv",
                "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gene_assoc/smultixcan/rapid_gwas_project/smultixcan_22617_7112_ccn30.tsv.gz",
                "GTEX_V8",
                "MASHR",
                output_dir_base
        ),
        # Add more test cases here as needed
    ]
)
def test_cli_command(cohort, gwas_file, spredixcan_dir, output_file_name, smultixcan_file, reference_panel,
                     eqtl_models, output_dir):
    # -p <project_dir> is omitted here
    suc, msg = invoke_corr_preprocess(
        cohort=cohort,
        gwas_file=gwas_file,
        spredixcan_dir=spredixcan_dir,
        output_file_name=output_file_name,
        smultixcan_file=smultixcan_file,
        reference_panel=reference_panel,
        eqtl_models=eqtl_models,
        output_dir = output_dir,
    )
    assert suc, msg

    # gene_tissues_filename = "gene_tissues.pkl"
    # test_gene_tissues = output_dir / gene_tissues_filename
    # ref_gene_tissues = test_data_dir / gene_tissues_filename
    # # Assert the output files exist
    # assert test_gene_tissues.exists(), f"gene-tissues.pkl not found in {output_dir}"
    # # Load the pickled dataframes
    # df1 = load_pickle(test_gene_tissues)
    # df2 = load_pickle(ref_gene_tissues)
    # # Assert the output matches the expected output
    # assert compare_dataframes_equal(df1, df2), f"Output file {gene_tissues_filename} does not match expected output"
