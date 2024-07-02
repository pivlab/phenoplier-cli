from pathlib import Path
from common import get_test_output_dir
from phenoplier.config import settings as conf

_test_output_dir = conf.TEST_OUTPUT_DIR


def test_get_test_output_dir():
    relative_test_path = "testdir/testA.py"
    absolute_test_path = Path(__file__).parent / relative_test_path
    out_path = get_test_output_dir(absolute_test_path)
    print(out_path)
    assert out_path == Path(_test_output_dir) / relative_test_path
