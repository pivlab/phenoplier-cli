from typer.testing import CliRunner
from pytest import fixture, mark
from phenoplier import cli
import pytest
from pathlib import Path
import pandas as pd
import numpy as np

from phenoplier.config import settings as conf
from phenoplier.commands.project import to_multiplier
from phenoplier.utils import read_rds

runner = CliRunner()


# Test help message
@mark.parametrize("options, expected_output", [
    (["project --help", "project -h"], "Projects input data into the specified representation space."),
])
def test_options(options, expected_output):
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        assert result.exit_code == 0
        assert expected_output in result.stdout


# Define test cases using the reference data
TEST_CASES = [f"test_case{i}" for i in range(1, 6)]
TEST_DATA_DIR = Path(conf.TEST_DIR) / "data" / "multiplier"


def compare_results(result, reference_output, test_case):
    """Helper function to compare projection results with reference data."""
    assert result is not None
    assert result.shape == reference_output.shape
    assert isinstance(result, pd.DataFrame)
    # Use equal_nan=True only for test_case4 which contains NaN values
    equal_nan = test_case == "test_case4"
    assert np.allclose(reference_output.values, result.values, equal_nan=equal_nan)


@pytest.mark.parametrize("test_case", TEST_CASES)
def test_projection_correctness(test_case, tmp_path):
    """Test if the projection matches the reference output."""
    data_dir = TEST_DATA_DIR / test_case
    input_file = data_dir / "input_data.rds"
    reference_output = read_rds(data_dir / "output_data.rds")
    
    output_file = tmp_path / "explicit_output.pkl"
    to_multiplier(input_file=input_file, output_file=output_file)
    
    result = pd.read_pickle(output_file)
    compare_results(result, reference_output, test_case)


@pytest.mark.parametrize("test_case", TEST_CASES)
def test_default_output_location(test_case, tmp_path):
    """Test if default output file is created in the correct location."""
    data_dir = TEST_DATA_DIR / test_case
    input_file = tmp_path / "input_data.rds"
    
    import shutil
    shutil.copy(data_dir / "input_data.rds", input_file)
    
    to_multiplier(input_file=input_file)
    
    expected_output = input_file.parent / "input_data_projected_to_m.pkl"
    assert expected_output.exists()
    
    reference_output = read_rds(data_dir / "output_data.rds")
    result = pd.read_pickle(expected_output)
    compare_results(result, reference_output, test_case)


def test_missing_input_file():
    """Test if appropriate error is raised for missing input file."""
    with pytest.raises(FileNotFoundError):
        to_multiplier(input_file=Path("nonexistent_file.rds"))
