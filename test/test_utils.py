from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
import pandas as pd
import h5py
from pytest import mark, raises, fixture

from phenoplier.config import settings as conf
from test.utils import (
    get_test_output_dir,
    compare_npz_files,
    compare_npz_files_in_dirs,
    _list_hdf_keys,
    _are_close_hdf5_files,
    are_hdf5_files_close,
    are_non_numeric_df_equal,
    compare_dataframes,
)

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


@mark.parametrize("file_contents1, file_contents2, expected", [
    # Identical files
    (
            {"file1.npz": {'key1': np.array([1, 2, 3]), 'key2': np.array(['a', 'b', 'c'])},
             "file2.npz": {'key1': np.array([4, 5, 6]), 'key2': np.array(['d', 'e', 'f'])}},
            {"file1.npz": {'key1': np.array([1, 2, 3]), 'key2': np.array(['a', 'b', 'c'])},
             "file2.npz": {'key1': np.array([4, 5, 6]), 'key2': np.array(['d', 'e', 'f'])}},
            True
    ),
    # Different files
    (
            {"file1.npz": {'key1': np.array([1, 2, 3]), 'key2': np.array(['a', 'b', 'c'])},
             "file2.npz": {'key1': np.array([4, 5, 6]), 'key2': np.array(['d', 'e', 'f'])}},
            {"file1.npz": {'key1': np.array([1, 2, 3]), 'key2': np.array(['a', 'b', 'c'])},
             "file2.npz": {'key1': np.array([7, 8, 9]), 'key2': np.array(['x', 'y', 'z'])}},
            False
    ),
    # Different number of files
    (
            {"file1.npz": {'key1': np.array([1, 2, 3]), 'key2': np.array(['a', 'b', 'c'])},
             "file2.npz": {'key1': np.array([4, 5, 6]), 'key2': np.array(['d', 'e', 'f'])}},
            {"file1.npz": {'key1': np.array([1, 2, 3]), 'key2': np.array(['a', 'b', 'c'])}},
            False
    )
])
def test_compare_npz_files_in_dirs(file_contents1, file_contents2, expected):
    dir1 = _test_output_dir / "dir3"
    dir2 = _test_output_dir / "dir4"
    dir1.mkdir(parents=True, exist_ok=True)
    dir2.mkdir(parents=True, exist_ok=True)

    # Create files in dir1
    for filename, content in file_contents1.items():
        np.savez(dir1 / filename, **content)

    # Create files in dir2
    for filename, content in file_contents2.items():
        np.savez(dir2 / filename, **content)

    # Compare directories
    result, message = compare_npz_files_in_dirs(dir1, dir2)
    assert result is expected, message


@fixture
def sample_hdf_file():
    with NamedTemporaryFile(suffix='.h5', delete=False) as tmp:
        df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df2 = pd.DataFrame({'C': [7, 8, 9], 'D': [10, 11, 12]})
        metadata = pd.DataFrame({'varID': ['1', '2', '3'], 'info': ['a', 'b', 'c']})
        with pd.HDFStore(tmp.name, mode='w') as store:
            store['key1'] = df1
            store['key2'] = df2
            store['metadata'] = metadata
        yield Path(tmp.name)
    Path(tmp.name).unlink()


def test_are_non_numeric_df_equal():
    df1 = pd.DataFrame({'A': ['a', 'b', 'c']})
    df2 = pd.DataFrame({'A': ['a', 'b', 'c']})
    df3 = pd.DataFrame({'A': ['a', 'b', 'd']})

    yes, message = are_non_numeric_df_equal(df1, df2)
    assert yes, message

    yes, message = are_non_numeric_df_equal(df1, df3)
    assert not yes, message


def test_are_close_hdf5_files(sample_hdf_file):
    result, message = _are_close_hdf5_files(sample_hdf_file, sample_hdf_file, ("metadata", ))
    assert result
    assert message == "Files are close in value."


def test_are_close_hdf5_files_with_ignore(sample_hdf_file):
    result, message = _are_close_hdf5_files(sample_hdf_file, sample_hdf_file, ('key1',"metadata"))
    assert result
    assert message == "Files are close in value."


def test_are_close_hdf5_files_different():
    with NamedTemporaryFile(suffix='.h5', delete=False) as tmp1, \
         NamedTemporaryFile(suffix='.h5', delete=False) as tmp2:
        df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df2 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 7]})  # Different value
        with pd.HDFStore(tmp1.name, mode='w') as store1, \
             pd.HDFStore(tmp2.name, mode='w') as store2:
            store1['key1'] = df1
            store2['key1'] = df2
        result, message = _are_close_hdf5_files(Path(tmp1.name), Path(tmp2.name), ())
        assert result == False
        assert "Values under key key1 in HDF5 files are not close." in message
    Path(tmp1.name).unlink()
    Path(tmp2.name).unlink()


def test_are_hdf5_files_close_nonexistent():
    with raises(FileNotFoundError):
        are_hdf5_files_close(Path('nonexistent1.h5'), Path('nonexistent2.h5'))


def test_list_hdf_keys(sample_hdf_file):
    keys = _list_hdf_keys(sample_hdf_file)
    assert set(keys) == {'key1', 'key2', 'metadata'}
