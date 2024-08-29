import os
from pathlib import Path
import logging
import gzip
import pickle
import numpy as np
import pandas as pd

from typer.testing import CliRunner
from pytest import mark

from phenoplier import cli
from phenoplier.config import settings as conf
from test.utils import (
    get_test_output_dir,
    compare_gene_tissues,
    compare_genes_info,
    compare_gwas_variant_ids,
    compare_gene_tissues_models,
    compare_dataframes
)

logger = logging.getLogger(__name__)

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

# Define the placeholders in the command
_BASE_COMMAND = (
    "run gene-corr preprocess "
    "-c {cohort} "
    "-g {gwas_file} "
    "-s {spredixcan_dir} "
    "-n {output_file_name} "
    "-f {smultixcan_file} "
    "-r {reference_panel} "
    "-m {eqtl_model} "
    "-o {output_dir}"
)

# Define the test output directory
# Todo: organize test data dir the same way as test output dir
output_dir_base = get_test_output_dir(Path(__file__))
test_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/2-preprocess/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr/"


@mark.skipif(IN_GITHUB_ACTIONS, reason="Data has not been setup in Github Actions yet. Local test only.")
@mark.corr
@mark.order(-5)
@mark.parametrize(
    "cohort, gwas_file, spredixcan_dir, output_file_name, smultixcan_file, reference_panel, eqtl_model, output_dir",
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
                     eqtl_model, output_dir):
    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        gwas_file=gwas_file,
        spredixcan_dir=spredixcan_dir,
        output_file_name=output_file_name,
        smultixcan_file=smultixcan_file,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        output_dir=output_dir,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    logger.info(f"Running command: {command}")
    # Assert the command ran successfully
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"

    def load_pickle_or_gz_pickle(file_path):
        if file_path.suffix == '.gz':
            with gzip.open(file_path, 'rb') as f:
                return pickle.load(f)
        else:
            with open(file_path, 'rb') as f:
                return pickle.load(f)

    files_and_handlers = (
                            ("genes_info.pkl", compare_genes_info),
                            ("gene_tissues.pkl", compare_gene_tissues),
                            ("gwas_variant_ids.pkl.gz", compare_gwas_variant_ids),
                            ("gene_tissues_models.pkl.gz", compare_gene_tissues_models),
    )
    for file, compare in files_and_handlers:
        out = output_dir / file
        ref = test_data_dir / file

        # Assert the output files exist
        assert out.exists(), f"{file} not found in {output_dir}"
        assert ref.exists(), f"{file} not found in {test_data_dir}"

        # Load the pickled data
        df1 = load_pickle_or_gz_pickle(out)
        df2 = load_pickle_or_gz_pickle(ref)

        equal, msg = compare(df1, df2)
        assert equal, msg

        print(f"File {file} matches expected output")
