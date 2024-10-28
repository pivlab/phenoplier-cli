# This module compares the results of the GWAS result from 05_gwas with those reference results on Alpine

import os
import gzip
import pytest
import pandas as pd
import numpy as np

# Directories containing the result and reference files
output_dir = "/mnt/data/proj_data/phenoplier-cli/ukb-nullsim/plink-v1.1.0/"
ref_dir = "/mnt/data/alpine_data/pivlab/data/phenoplier/results/gls/gwas/null_sims/ukb/"
file_ext = ".tsv.gz"
float_columns = ['BETA', 'SE', 'P']

def get_files_in_dir(directory, ext):
    """Retrieve a list of files in a directory with the specified extension."""
    return sorted([f for f in os.listdir(directory) if f.endswith(ext)])


def load_tsv_gz_as_dataframe(filepath):
    """Load a gzipped TSV file into a Pandas DataFrame."""
    return pd.read_csv(filepath, sep='\t', compression='gzip')


def compare_dataframes(df1, df2, float_cols, tol=0.2):
    differences = []
    max_diff = 0
    max_diff_info = None
    
    # Check if dataframes have the same shape
    if df1.shape != df2.shape:
        return False, "DataFrames have different shapes"
    
    # Check for exact equality of non-float columns
    non_float_cols = [col for col in df1.columns if col not in float_cols]
    if not df1[non_float_cols].equals(df2[non_float_cols]):
        return False, "Non-float columns are not equal"
    
    # Check if floating-point columns are close within the tolerance
    for col in float_cols:
        for idx in df1.index:
            val1 = df1.at[idx, col]
            val2 = df2.at[idx, col]
            diff = abs(val1 - val2)
            if not np.isclose(val1, val2, atol=tol, rtol=0):
                differences.append((idx, col, val1, val2, diff))
                if diff > max_diff:
                    max_diff = diff
                    max_diff_info = (idx, col, val1, val2)

    # If there are differences, print them
    if differences:
        print("Differences found:")
        for diff in differences:
            idx, col, val1, val2, diff_value = diff
            print(f"Index {idx}, Column '{col}': {val1} vs {val2}, Difference: {diff_value:.7f}")
        
        if max_diff_info:
            idx, col, val1, val2 = max_diff_info
            print(f"\nMaximum difference at Index {idx}, Column '{col}': {val1} vs {val2}, Difference: {max_diff:.7f}")
        return False, f"Found {len(differences)} differences"
    
    return True, "DataFrames are close"

# Only compare files that exist in the output directory
@pytest.mark.parametrize("filename", get_files_in_dir(output_dir, file_ext))
def test_gwas_result_equality(filename):
    """Test if GWAS result files match the reference files using Pandas."""
    # Paths to the output and reference files
    output_file = os.path.join(output_dir, filename)
    reference_file = os.path.join(ref_dir, filename)

    # Ensure both files exist
    assert os.path.exists(output_file), f"Output file {output_file} does not exist."
    assert os.path.exists(reference_file), f"Reference file {reference_file} does not exist."

    # Load the TSV files as DataFrames
    output_df = load_tsv_gz_as_dataframe(output_file)
    reference_df = load_tsv_gz_as_dataframe(reference_file)

    # Compare DataFrames (ignoring the index)
    suc, msg = compare_dataframes(output_df, reference_df, float_columns)
    assert suc, msg