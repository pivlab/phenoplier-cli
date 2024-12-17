import pytest
import numpy as np
import pandas as pd
import phenoplier.multiplier as multiplier

from pathlib import Path
from phenoplier.config import settings as conf
from phenoplier.utils import read_rds

def read_test_case(test_case_number: int, kind: str) -> pd.DataFrame:
    """Reads a test case data from an RDS file.

    Args:
        test_case_number (int): test case number to be read.
        kind (str): kind of data; it could be 'input_data' or 'output_data'.

    Returns:
        pd.DataFrame: Test case data.
    """
    rds_file = (
        Path(conf.TEST_DIR)
        / "data"
        / "multiplier"
        / f"test_case{test_case_number}"
        / f"{kind}.rds"
    )
    return read_rds(rds_file)


def run_saved_test_case_simple_check(test_case_number, test_function=np.allclose):
    # prepare
    np.random.seed(0)
    input_data = read_test_case(test_case_number, "input_data")

    # run
    proj_data = multiplier.transform(input_data)

    # evaluate
    assert proj_data is not None
    assert proj_data.shape == (987, input_data.shape[1])
    assert isinstance(proj_data, pd.DataFrame)

    expected_output_data = read_test_case(test_case_number, "output_data")
    assert expected_output_data.shape == proj_data.shape
    assert test_function(expected_output_data.values, proj_data.values)


@pytest.mark.parametrize(
    "test_case_number",
    # these three cases include simple and small dataset with just a few genes and
    # traits (columns)
    [1, 2, 3],
)
def test_project_simple_data(test_case_number):
    run_saved_test_case_simple_check(test_case_number)


@pytest.mark.parametrize("test_case_number", [4])
@pytest.mark.filterwarnings("ignore:Input data contains NaN values")
def test_project_data_with_nan(test_case_number):
    run_saved_test_case_simple_check(
        test_case_number, lambda x, y: np.allclose(x, y, equal_nan=True)
    )


@pytest.mark.parametrize("test_case_number", [5])
def test_project_phenomexcan_subsample(test_case_number):
    run_saved_test_case_simple_check(test_case_number)
