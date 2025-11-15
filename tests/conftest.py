"""
Pytest configuration and fixtures for expense-predictor tests.

This module provides shared fixtures and configuration for all tests.
"""

import logging
import os
import tempfile
from datetime import datetime, timedelta

import pandas as pd
import pytest


@pytest.fixture
def sample_csv_path():
    """Path to a valid sample CSV file with transaction data."""
    return os.path.join(os.path.dirname(__file__), "test_data", "sample.csv")


@pytest.fixture
def sample_invalid_columns_csv_path():
    """Path to a CSV file with invalid column names."""
    return os.path.join(os.path.dirname(__file__), "test_data", "sample_invalid_columns.csv")


@pytest.fixture
def sample_empty_csv_path():
    """Path to an empty CSV file."""
    return os.path.join(os.path.dirname(__file__), "test_data", "sample_empty.csv")


@pytest.fixture
def sample_invalid_dates_csv_path():
    """Path to a CSV file with invalid dates."""
    return os.path.join(os.path.dirname(__file__), "test_data", "sample_invalid_dates.csv")


@pytest.fixture
def sample_future_dates_csv_path():
    """Path to a CSV file with future dates only."""
    return os.path.join(os.path.dirname(__file__), "test_data", "sample_future_dates.csv")


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    return pd.DataFrame(
        {"Date": dates, "Tran Amt": [150.00, 75.50, 200.00, 120.75, 95.25, 180.00, 210.50, 165.25, 145.00, 190.75]}
    )


@pytest.fixture
def sample_dataframe_with_column_variations():
    """Create a DataFrame with flexible column name variations."""
    return pd.DataFrame(
        {
            "Value Date": ["01/01/2024", "02/01/2024", "03/01/2024"],
            "Withdrawal Amount (INR )": [100.0, 150.0, 200.0],
            "Deposit Amount (INR )": [0.0, 50.0, 0.0],
        }
    )


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing write operations."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Date,Tran Amt\n")
        f.write("01/01/2024,150.00\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
    # Also clean up any backup files
    backup_pattern = temp_path.replace(".csv", ".backup_*")
    import glob

    for backup_file in glob.glob(backup_pattern):
        if os.path.exists(backup_file):
            os.remove(backup_file)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path

    # Cleanup
    import shutil

    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    return logger


@pytest.fixture
def current_year():
    """Get the current year for testing date-related functions."""
    return datetime.now().year


@pytest.fixture
def sample_processed_dataframe():
    """Create a sample processed DataFrame with features."""
    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    df = pd.DataFrame(
        {
            "Date": dates,
            "Tran Amt": [150.00, 75.50, 200.00, 120.75, 95.25, 180.00, 210.50, 165.25, 145.00, 190.75],
            "Month": [d.month for d in dates],
            "Day of the Month": [d.day for d in dates],
        }
    )

    # Add one-hot encoded day of week columns (drop first)
    day_names = ["Monday", "Saturday", "Sunday", "Thursday", "Tuesday", "Wednesday"]
    for day in day_names:
        df[f"Day of the Week_{day}"] = 0

    return df


@pytest.fixture
def test_data_dir():
    """Get the path to the test_data directory."""
    return os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture
def fixtures_dir():
    """Get the path to the fixtures directory."""
    return os.path.join(os.path.dirname(__file__), "fixtures")
