from pathlib import Path

import numpy as np
import h5py
from pytest import mark, raises

from test.utils import get_test_output_dir, compare_hdf5_files
from phenoplier.config import settings as conf
from test.utils import compare_npz_files

_test_output_dir = conf.TEST_OUTPUT_DIR


@mark.parametrize(
    "relative_test_path",
    [
        Path("testdir/testA.py"),
    ]
)
def test_get_test_output_dir(relative_test_path: Path):
    # We want to mirror the relative directory structure of the test files, for the output files
    # Get the "fake" absolute path of the test file
    absolute_test_path = (Path(__file__).parent / relative_test_path).resolve()
    out_dir = get_test_output_dir(absolute_test_path)
    expected = Path(_test_output_dir) / relative_test_path.with_suffix("")
    assert out_dir == expected


def test_compare_hdf5_files0():
    outdir = get_test_output_dir(__file__)
    # Both files exist and are equal
    non_existing_file1 = Path(outdir, "non_existing_file1.h5")
    non_existing_file2 = Path(outdir, "non_existing_file2.h5")
    with raises(FileNotFoundError):
        compare_hdf5_files(non_existing_file1, non_existing_file2)
    # Create test HDF5 files
    # existing_file1 and existing_file2 are equal
    existing_file1 = Path(outdir, "existing_file1.h5")
    existing_file2 = Path(outdir, "existing_file2.h5")
    diff_file = Path(outdir, "diff_file.h5")
    data = np.arange(100).reshape(10, 10)
    diff_data = np.arange(100).reshape(10, 10) + 1
    # Create an HDF5 file
    with h5py.File(str(existing_file1), 'w') as h5file1, \
            h5py.File(str(existing_file2), 'w') as h5file2, \
            h5py.File(str(diff_file), 'w') as h5file_diff:
        # Create a dataset in the file
        h5file1.create_dataset('dataset1', data=data)
        # Only file1 exists
        with raises(FileNotFoundError):
            compare_hdf5_files(Path(h5file1.filename), non_existing_file2)
        # Both files exist and are equal
        h5file2.create_dataset('dataset1', data=data)
        h5file_diff.create_dataset('dataset1', data=diff_data)
    # Compare the identical files
    assert compare_hdf5_files(existing_file1, existing_file2) is True
    # Compare the different files
    assert compare_hdf5_files(existing_file1, diff_file) is False
    assert compare_hdf5_files(existing_file2, diff_file) is False


@mark.parametrize("filename1, content1, filename2, content2, expected", [
    ("same1.npz", {'key1': np.array(['value1', 'value2']), 'key2': np.array([1, 2, 3])},
     "same2.npz", {'key1': np.array(['value1', 'value2']), 'key2': np.array([1, 2, 3])}, True),
    ("file.npz", {'key1': np.array(['value1', 'value2']), 'key2': np.array([1, 2, 3])},
     "diff.npz", {'key1': np.array(['value1', 'value2']), 'key2': np.array([2, 3, 4])}, False),
    ("file.npz", {'key1': np.array(['value1', 'value2']), 'key2': np.array([1, 2, 3])},
     "diff_keys.npz", {'k1': np.array(['value1', 'value2']), 'k2': np.array([2, 3, 4])}, False),
    ("file.npz", {'key1': np.array(['value1', 'value2']), 'key2': np.array([1, 2, 3])},
     "empty.npz", {'key1': np.array([]), 'key2': np.array([])}, False),
])
def test_compare_npz_files(filename1, content1, filename2, content2, expected):
    dir1 = _test_output_dir / "dir1"
    dir2 = _test_output_dir / "dir2"
    dir1.mkdir(parents=True, exist_ok=True)
    dir2.mkdir(parents=True, exist_ok=True)

    file1 = dir1 / filename1
    file2 = dir2 / filename2

    np.savez(file1, **content1)
    np.savez(file2, **content2)

    assert compare_npz_files(file1, file2)[0] is expected
