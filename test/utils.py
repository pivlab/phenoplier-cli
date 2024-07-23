"""This module contains utility functions that are used in the test suite."""
import os
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


def compare_hdf5_files(file1: Path, file2: Path) -> bool:
    """
    Compare two HDF5 files using h5diff.

    :param Path file1: Path to the first HDF5 file.
    :param Path file2: Path to the second HDF5 file.
    :return: True if the files are identical, False otherwise.
    """
    # Make sure files exist
    if not file1.exists() or not file2.exists():
        raise FileNotFoundError(f"File not found: {file1 if not file1.exists() else file2}")

    return _run_h5diff(file1, file2)[0]


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


def load_pickle(filepath):
    with open(filepath, 'rb') as file:
        return pickle.load(file)


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
