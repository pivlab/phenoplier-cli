# This module compares the results of the GWAS result from 05_gwas with those reference results on Alpine

import os
import gzip
import pytest
import pandas as pd

# Directories containing the result and reference files
output_dir = "/mnt/data/proj_data/phenoplier-cli/ukb-nullsim/"
red_dir = "/mnt/data/alpine_data/pivlab/data/phenoplier/results/gls/gwas/null_sims/ukb/"
file_ext = ".tsv.gz"


def get_files_in_dir(directory, ext):
    """Retrieve a list of files in a directory with the specified extension."""
    return sorted([f for f in os.listdir(directory) if f.endswith(ext)])


def load_tsv_gz_as_dataframe(filepath):
    """Load a gzipped TSV file into a Pandas DataFrame."""
    return pd.read_csv(filepath, sep='\t', compression='gzip')


@pytest.mark.parametrize("filename", get_files_in_dir(output_dir, file_ext))
def test_gwas_result_equality(filename):
    """Test if GWAS result files match the reference files using Pandas."""
    # Paths to the output and reference files
    output_file = os.path.join(output_dir, filename)
    reference_file = os.path.join(red_dir, filename)

    # Ensure both files exist
    assert os.path.exists(output_file), f"Output file {output_file} does not exist."
    assert os.path.exists(reference_file), f"Reference file {reference_file} does not exist."

    # Load the TSV files as DataFrames
    output_df = load_tsv_gz_as_dataframe(output_file)
    reference_df = load_tsv_gz_as_dataframe(reference_file)

    # Compare DataFrames (ignoring the index)
    pd.testing.assert_frame_equal(output_df, reference_df, check_like=True)