from pathlib import Path

from pytest import mark

from test.utils import get_test_output_dir
from phenoplier.config import settings as conf

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
    print(absolute_test_path)
    out_dir = get_test_output_dir(absolute_test_path)
    expected = Path(_test_output_dir) / relative_test_path.with_suffix("")
    assert out_dir == expected
