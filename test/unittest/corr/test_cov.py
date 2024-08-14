import pytest
import numpy as np
import pandas as pd

from phenoplier.commands.run.correlation.cov import covariance


@pytest.fixture
def generate_test_data():
    def _generate(size, seed=0):
        rs = np.random.RandomState(seed)
        return pd.DataFrame(rs.normal(size=size), columns=[f"c{i}" for i in range(size[1])])
    return _generate


@pytest.mark.parametrize("dtype, rtol, atol, check_dtype, size, seed", [
    # Original tests
    (np.float64, 1e-10, 1e-10, True, (50, 5), 0),
    (np.float32, 1e-5, 1e-8, False, (50, 5), 0),
    # Additional data types
    (np.float16, 1e-2, 1e-2, False, (50, 5), 0),  # Less precise, larger tolerances
    # Different sized datasets
    (np.float64, 1e-10, 1e-10, True, (100, 10), 1),
    (np.float64, 1e-10, 1e-10, True, (1000, 3), 2),
    # Edge cases
    (np.float64, 1e-10, 1e-10, True, (2, 2), 3),  # Minimum size for covariance
    (np.float64, 1e-10, 1e-10, True, (100, 1), 4),  # Single column
    # Different random seeds
    (np.float64, 1e-10, 1e-10, True, (50, 5), 5),
    (np.float32, 1e-5, 1e-8, False, (50, 5), 6),
])
def test_covariance(generate_test_data, dtype, rtol, atol, check_dtype, size, seed):
    test_data = generate_test_data(size, seed)
    pd.testing.assert_frame_equal(
        covariance(test_data, dtype),
        test_data.cov(),
        rtol=rtol,
        atol=atol,
        check_dtype=check_dtype
    )


# Additional test for empty DataFrame
def test_covariance_empty_df():
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError):
        covariance(empty_df, np.float64)


# Test for DataFrame with constant values
def test_covariance_constant_values(generate_test_data):
    constant_df = generate_test_data((10, 3)).iloc[:, 0:1].assign(const=1)
    result = covariance(constant_df, np.float64)
    expected = constant_df.cov()
    pd.testing.assert_frame_equal(result, expected, rtol=1e-10, atol=1e-10)
