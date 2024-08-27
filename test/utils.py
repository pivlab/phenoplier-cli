"""This module contains utility functions that are used in the test suite."""
import os
import gzip
import subprocess
import hashlib
import pickle
from pathlib import Path
from typing import Tuple

import pandas as pd
import numpy as np

from phenoplier.config import settings as conf

# Get the root dir of the test suite of the repository
_prefix_to_remove = os.path.dirname(__file__)
_output_dir = conf.TEST_OUTPUT_DIR


def get_test_output_dir(test_filepath: Path) -> Path:
    """Return the output directory for the test with the given path"""
    # We want to mirror the relative directory structure of the test files, for the output files
    # "relative_path" refers to the test file, relative to root of test directory of the project repo
    if type(test_filepath) is str:
        test_filepath = Path(test_filepath)
    relative_path = test_filepath.relative_to(_prefix_to_remove)
    # Remove .py extension. E.g. testdir/testA.py -> testdir/testA
    relative_path = relative_path.with_suffix("")
    # Construct the output directory
    output_dir = _output_dir / relative_path
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _calculate_md5(file_path: Path, chunk_size: int = 8192) -> str:
    """
    Calculate the MD5 hash of a file.
    """
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()


def compare_files_md5(file1: Path, file2: Path) -> bool:
    """
    Compare two files to check if they are the same using MD5 hash.
    """
    md5_file1 = _calculate_md5(file1)
    md5_file2 = _calculate_md5(file2)

    return md5_file1 == md5_file2


def _run_h5diff(file1: Path, file2: Path, args: str = "-r") -> tuple[bool, str]:
    """
    Run h5diff to compare two HDF5 files.
    """
    cmd = f"h5diff {args} {file1} {file2}"
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    return True, "Files are identical"


def _list_hdf_keys(file_path: Path) -> list[str]:
    with pd.HDFStore(file_path, mode='r') as store:
        return [key.lstrip('/') for key in store.keys()]


def are_non_numeric_df_equal(df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[bool, str]:
    """
    Compare two non-numeric dataframes and return True if they are identical,
    otherwise return False and the error message.

    :param df1: First dataframe.
    :param df2: Second dataframe.
    :return: A tuple of (bool, str). The boolean indicates whether the
             DataFrames are identical, and the string provides details on
             the difference if they are not.
    """
    try:
        # Use assert_frame_equal to compare the DataFrames
        pd.testing.assert_frame_equal(df1, df2, check_dtype=False, check_exact=False)
        return True, "DataFrames are identical."

    except AssertionError as e:
        return False, str(e)


def _are_close_hdf5_files(file1: Path, file2: Path, ignore_fields: Tuple[str]) -> Tuple[bool, str]:
    """
    Compare two HDF5 files using h5diff.
    """
    # Get the list of keys in the HDF5 files
    keys1 = _list_hdf_keys(file1)
    keys2 = _list_hdf_keys(file2)

    # Check if the keys are the same
    if keys1 != keys2:
        return False, "Keys in the HDF5 files are not the same."

    # Check if the values are the same
    for key in keys1:
        if key in ignore_fields:
            continue
        arr1 = pd.read_hdf(file1, key).sort_index(axis=0).sort_index(axis=1).to_numpy()
        arr2 = pd.read_hdf(file2, key).sort_index(axis=0).sort_index(axis=1).to_numpy()
        if not np.allclose(arr1, arr2):
            return False, f"Values under key {key} in HDF5 files are not close."

    return True, "Files are close in value."


def are_hdf5_files_close(file1: Path, file2: Path, ignore_fields: Tuple[str] = ()) -> tuple[bool, str]:
    """
    Compare two HDF5 files using h5diff.

    :param Path file1: Path to the first HDF5 file.
    :param Path file2: Path to the second HDF5 file.
    :param Tuple[str] ignore_fields: Tuple of fields to ignore.
    :return: True if the files are identical, False otherwise.
    """
    # Make sure files exist
    if not file1.exists() or not file2.exists():
        raise FileNotFoundError(f"File not found: {file1 if not file1.exists() else file2}")

    return _are_close_hdf5_files(file1, file2, ignore_fields)


def compare_dataframes_close(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """
    Compare two dataframes and return True if they are identical.

    :param df1: First dataframe.
    :param df2: Second dataframe.
    """
    return np.isclose(df1, df2).all().all()


def compare_dataframes_equal(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """
    Compare two dataframes and return True if they are identical.

    :param df1: First dataframe.
    :param df2: Second dataframe.
    """
    return df1.equals(df2)


def are_close_arrays(arr1: np.ndarray, arr2: np.ndarray) -> bool:
    """
    Compare two dataframes and return True if they are identical.

    :param arr1: First ndarray.
    :param arr2: Second ndarray.
    """
    return np.allclose(arr1, arr2)


def load_pickle(filepath):
    with open(filepath, 'rb') as file:
        return pickle.load(file)


def load_pickle_to_ndarray(filepath: Path) -> np.ndarray:
    return np.load(filepath, allow_pickle=True)


def compare_metadata_npz_files(dir1, dir2):
    """
    Special handling for 'metadata.npz' files to compare case-insensitively.
    New results are saved with upper-case keys while old results are saved with lower-case keys.
    This function servers as an ad-hoc solution.
    """
    # Special handling for 'metadata.npz'
    file1 = Path(dir1) / 'metadata.npz'
    file2 = Path(dir2) / 'metadata.npz'
    if not file1.exists() or not file2.exists():
        return False, "metadata.npz file not found in both directories."
    # Load the .npz files
    npz1 = np.load(file1)
    npz2 = np.load(file2)
    print(f"Comparing metadata.npz files...")
    for key in npz1.files:
        if key not in npz2.files:
            return False, f"Key {key} not found in both metadata.npz files."
        array1 = npz1[key]
        array2 = npz2[key]

        if array1.dtype.kind in {'U', 'S'} and array2.dtype.kind in {'U', 'S'}:
            if not np.array_equal(np.char.lower(array1), np.char.lower(array2)):
                return False, f"Arrays under key {key} in metadata.npz are not case-insensitively equal."
        else:
            if not np.array_equal(array1, array2):
                return False, f"Arrays under key {key} in metadata.npz are not equal."
    return True, "All metadata.npz files are equal."


def compare_npz_files(file1: Path, file2: Path, rtol: float = 1e-5, atol: float = 1e-8) -> tuple[bool, str]:
    if not file1.exists() or not file2.exists():
        raise FileNotFoundError(f"File not found: {file1 if not file1.exists() else file2}")

    npz1 = np.load(file1)
    npz2 = np.load(file2)

    # Check if all arrays in the .npz files are close
    for key in npz1.files:
        if key not in npz2.files:
            return False, f"Key {key} not found in both .npz files."
        array1 = npz1[key]
        array2 = npz2[key]

        # Handle different data types
        if array1.dtype != array2.dtype:
            return False, f"Arrays under key {key} in file {file1} have different data types: {array1.dtype} vs {array2.dtype}"

        if np.issubdtype(array1.dtype, np.number) and np.issubdtype(array2.dtype, np.number):
            if not np.allclose(array1, array2, rtol=rtol, atol=atol):
                return False, f"Arrays under key {key} in file {file1} are not close."
        else:
            if not np.array_equal(array1, array2):
                return False, f"Non-numeric arrays under key {key} in file {file1} are not equal."

    return True, "Two files are equal or close in value."


def compare_npz_files_in_dirs(dir1: Path, dir2: Path,
                              ignore_files: Tuple[str, ...] = ('metadata.npz',),
                              include_files: Tuple[str, ...] = ()) -> Tuple[bool, str]:
    """
    Compare .npz files in two directories.

    :param Path dir1: Path to the first directory.
    :param Path dir2: Path to the second directory.
    :param Tuple[str, ...] ignore_files: Tuple of file names (not path) to ignore.
    :param Tuple[str, ...] include_files: Tuple of file names (not path) to include.
    """

    def get_npz_files(directory, ignores):
        # Get list of .npz files in the directory, excluding ignored files, and return absolute paths
        return sorted([Path(directory) / f for f in os.listdir(directory) if f.endswith('.npz') and f not in ignores])

    if len(include_files) > 0:
        files1 = list(map(lambda f: dir1 / f, include_files))
        files2 = list(map(lambda f: dir2 / f, include_files))
    else:
        files1 = get_npz_files(dir1, ignore_files)
        files2 = get_npz_files(dir2, ignore_files)

    # Check if the number of files is the same
    if len(files1) != len(files2):
        return False, "Number of files in the directories are not the same."

    # Compare files
    for file1, file2 in zip(files1, files2):
        # If include_files is specified, the files should be present in both directories
        try:
            success, message = compare_npz_files(file1, file2)
            if not success:
                return False, message
        except FileNotFoundError:
            return False, "Include file(s) not found in both directories."

    return True, "All files are equal or close in value."


def skip_test_on_ci():
    """
    Skip the test if running on CI.
    """
    if os.getenv("GITHUB_ACTIONS") == "true":
        return True
    return False


def compare_gene_tissues(df1: pd.DataFrame, df2: pd.DataFrame, numeric_tolerance: float = 1e-6) -> Tuple[bool, str]:
    """
    Compare two pandas DataFrames where all columns are pandas Series.

    This function compares two DataFrames and checks for equality in shape, columns, and values.
    It handles numeric Series with a tolerance and performs element-wise comparison for non-numeric Series.

    Parameters:
    df1 (pd.DataFrame): The first DataFrame to compare.
    df2 (pd.DataFrame): The second DataFrame to compare.
    numeric_tolerance (float): The tolerance for comparing numeric values. Default is 1e-6.

    Returns:
    Tuple[bool, str]: A tuple containing a boolean indicating whether the DataFrames are equal,
                      and a string message describing the result or the reason for inequality.
    """
    # Check if the DataFrames have the same shape
    if df1.shape != df2.shape:
        return False, f"DataFrames have different shapes: {df1.shape} vs {df2.shape}"

    # Check if the DataFrames have the same columns
    if not df1.columns.equals(df2.columns):
        diff_columns = set(df1.columns).symmetric_difference(set(df2.columns))
        return False, f"DataFrames have different columns. Differing columns: {diff_columns}"

    # Iterate through each column for detailed comparison
    for column in df1:
        series1 = df1[column]
        series2 = df2[column]

        # Check if the Series have the same dtype
        if series1.dtype != series2.dtype:
            return False, f"Column '{column}' has different dtypes: {series1.dtype} vs {series2.dtype}"

        if not series1.equals(series2):
            # Handle numeric Series
            if isinstance(series1.iloc[0], np.ndarray):
                if not all(np.allclose(arr1, arr2, atol=numeric_tolerance, equal_nan=True)
                           for arr1, arr2 in zip(series1, series2)):
                    diff_indices = [i for i, (arr1, arr2) in enumerate(zip(series1, series2))
                                    if not np.allclose(arr1, arr2, atol=numeric_tolerance, equal_nan=True)]
                    return False, f"Column '{column}' contains numpy arrays that are not close enough. Differences at indices: {diff_indices}"
            elif isinstance(series1.iloc[0], dict): # tissues_variances
                for d1, d2 in zip(series1, series2):
                    for key, val1 in d1.items():
                        if key not in d2:
                            return False, f"Column '{column}' contains dictionaries with different keys"
                        val2 = d2[key]
                        if not np.isclose(val1, val2, atol=numeric_tolerance, equal_nan=True):
                            return False, f"Column '{column}' contains dictionaries with different values"
            else:
                # Handle non-numeric Series
                if not series1.apply(str).equals(series2.apply(str)):
                    return False, f"Column '{column}' values are not equal"
            # return False, f"Column '{column}' are not equal or close. col1: {series1}, col2: {series2}"
        # print(f"Column '{column}' are equal.")

    # If all checks pass, the DataFrames are considered equal
    return True, "DataFrames are equal"


def compare_genes_info(df1: pd.DataFrame, df2: pd.DataFrame, numeric_tolerance: float = 1e-6) -> Tuple[bool, str]:
    """
    Compare two "genes_info" DataFrames. Used specifically for testing the preprocess command

    Parameters:
    df1 (pd.DataFrame): The first DataFrame to compare.
    df2 (pd.DataFrame): The second DataFrame to compare.
    numeric_tolerance (float): The tolerance for comparing numeric values. Default is 1e-6.

    Returns:
    Tuple[bool, str]: A tuple containing a boolean indicating whether the DataFrames are equal,
                      and a string message describing the result or the reason for inequality.
    """
    # Check if the DataFrames have the same shape
    if df1.shape != df2.shape:
        return False, f"DataFrames have different shapes: {df1.shape} vs {df2.shape}"

    # Check if the DataFrames have the same columns
    if not df1.columns.equals(df2.columns):
        diff_columns = set(df1.columns).symmetric_difference(set(df2.columns))
        return False, f"DataFrames have different columns. Differing columns: {diff_columns}"

    # Sort the dfs using the first column (gene_name)
    df1 = df1.sort_values(by=df1.columns[0]).reset_index(drop=True)
    df2 = df2.sort_values(by=df2.columns[0]).reset_index(drop=True)

    # Iterate through each column for detailed comparison
    for column in df1:
        series1 = df1[column]
        series2 = df2[column]
        if not series1.equals(series2):
            return False, f"Column '{column}' are not equal. col1: {series1}, col2: {series2}"

    # If all checks pass, the DataFrames are considered equal
    return True, "DataFrames are equal"


def compare_gwas_variant_ids(set1: frozenset, set2: frozenset) -> Tuple[bool, str]:
    """
    Compare two "gwas_variant_ids" sets. Used specifically for testing the preprocess command

    Returns:
    Tuple[bool, str]: A tuple containing a boolean indicating whether the DataFrames are equal,
                      and a string message describing the result or the reason for inequality.
    """
    # Check if the DataFrames have the same shape
    if len(set1) != len(set2):
        return False, f"Sets have different lengths: {len(set1)} vs {len(set2)}"

    if set1 != set2:
        return False, f"Sets are not equal"

    # If all checks pass, the DataFrames are considered equal
    return True, "DataFrames are equal"


def compare_dataframes(df1, df2):
    """
    Compare two dataframes that may have different row and column orders.

    Args:
    df1 (pd.DataFrame): First dataframe
    df2 (pd.DataFrame): Second dataframe

    Returns:
    bool: True if dataframes are equivalent, False otherwise
    """
    # Check if dataframes have the same shape
    if df1.shape != df2.shape:
        return False

    # Check if dataframes have the same column names (ignoring order)
    if set(df1.columns) != set(df2.columns):
        return False

    # Sort both dataframes by all columns and rows
    df1_sorted = df1.sort_index(axis=0).sort_index(axis=1)
    df2_sorted = df2.sort_index(axis=0).sort_index(axis=1)

    # Compare the sorted dataframes
    return df1_sorted.equals(df2_sorted)


def compare_gene_tissues_models(dict1: dict, dict2: dict) -> Tuple[bool, str]:
    """
    Compare two "genes_info" DataFrames. Used specifically for testing the preprocess command

    Parameters:
    df1 (pd.DataFrame): The first DataFrame to compare.
    df2 (pd.DataFrame): The second DataFrame to compare.
    numeric_tolerance (float): The tolerance for comparing numeric values. Default is 1e-6.

    Returns:
    Tuple[bool, str]: A tuple containing a boolean indicating whether the DataFrames are equal,
                      and a string message describing the result or the reason for inequality.
    """
    # Check if the DataFrames have the same shape
    if len(dict1) != len(dict2):
        return False, f"gene_tissues_models dicts have different shapes"

    # Sort by keys
    dict1 = dict(sorted(dict1.items()))
    dict2 = dict(sorted(dict2.items()))
    if dict1.keys() != dict2.keys():
        return False, f"gene_tissues_models dicts have different keys"

    # Iterate through each key for detailed comparison
    for key in dict1:
        df1 = dict1[key]
        df2 = dict2[key]
        # sort the dfs using the first column and firs row
        # df1 = sort_dataframe(df1, sort_columns=True, sort_rows=True)
        # df2 = sort_dataframe(df2, sort_columns=True, sort_rows=True)
        if not compare_dataframes(df1, df2):
            return False, f"gene_tissues_models dicts are not equal. key: {key}"

    # If all checks pass, the DataFrames are considered equal
    return True, "gene_tissues_models dicts are equal"


def load_pickle_or_gz_pickle(file_path):
    if file_path.suffix == '.gz':
        with gzip.open(file_path, 'rb') as f:
            return pickle.load(f)
    else:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
