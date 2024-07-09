"""This module contains utility functions that are used in the test suite."""
import os
import subprocess
import hashlib
from pathlib import Path

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

