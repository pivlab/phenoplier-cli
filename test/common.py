"""This module contains utility functions that are used in the test suite."""
import os
from pathlib import Path

from phenoplier.config import settings as conf

_prefix_to_remove = os.path.dirname(__file__)
_output_dir = conf.TEST_OUTPUT_DIR


def get_test_output_dir(test_filepath: Path) -> Path:
    """Return the output directory for the test with the given path"""
    relative_path = test_filepath.relative_to(_prefix_to_remove)
    output_dir = _output_dir / relative_path
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

