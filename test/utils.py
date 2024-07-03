"""This module contains utility functions that are used in the test suite."""
import os
import hashlib
from pathlib import Path

import pandas as pd

from phenoplier.config import settings as conf

# Get the root dir of the test suite of the repository
_prefix_to_remove = os.path.dirname(__file__)
_output_dir = conf.TEST_OUTPUT_DIR


def get_test_output_dir(test_filepath: Path) -> Path:
    """Return the output directory for the test with the given path"""
    # We want to mirror the relative directory structure of the test files, for the output files
    # "relative_path" refers to the test file, relative to root of test directory of the project repo
    relative_path = test_filepath.relative_to(_prefix_to_remove)
    # Remove .py extension. E.g. testdir/testA.py -> testdir/testA
    relative_path = relative_path.with_suffix("")
    # Construct the output directory
    output_dir = _output_dir / relative_path
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def calculate_md5(file_path, chunk_size=8192):
    """
    Calculate the MD5 hash of a file.
    """
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()


def compare_files_md5(file1, file2):
    """
    Compare two files to check if they are the same using MD5 hash.
    """
    md5_file1 = calculate_md5(file1)
    md5_file2 = calculate_md5(file2)

    if md5_file1 == md5_file2:
        return True, "Files are identical"
    else:
        return False, "Files are different"