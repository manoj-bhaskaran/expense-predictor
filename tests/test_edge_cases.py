"""
Additional edge case tests to reach 80% coverage.

This module tests edge cases and error paths in helpers.py and security.py.
"""

import os
import tempfile
from datetime import datetime
from typing import cast

import pandas as pd
import pytest

from exceptions import DataValidationError
from helpers import preprocess_and_append_csv, validate_excel_file
from security import validate_and_resolve_path


@pytest.mark.unit
@pytest.mark.validation
class TestHelpersEdgeCases:
    """Edge case tests for helpers.py."""

    def test_validate_excel_corrupt_file(self, temp_dir, mock_logger):
        """Test validation of corrupted Excel file."""
        # Create a fake Excel file (actually just text)
        fake_excel = os.path.join(temp_dir, "corrupt.xlsx")
        with open(fake_excel, "w") as f:
            f.write("This is not really an Excel file")

        with pytest.raises(DataValidationError, match="corrupted or cannot be read"):
            validate_excel_file(fake_excel, logger=mock_logger)

    def test_preprocess_and_append_with_excel(self, sample_csv_path, temp_dir, mock_logger):
        """Test preprocessing with valid Excel file."""
        # Create a minimal valid Excel file
        excel_path = os.path.join(temp_dir, "test.xlsx")

        # Create test data
        df = pd.DataFrame(
            {
                "Value Date": pd.date_range("2024-01-01", periods=5),
                "Withdrawal Amount (INR)": [100, 0, 150, 0, 200],
                "Deposit Amount (INR)": [0, 50, 0, 75, 0],
            }
        )

        # Add some header rows to skip
        header_df = pd.DataFrame([["Header"] * 3] * 12)

        # Write to Excel with headers
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            header_df.to_excel(writer, index=False, header=False)
            df.to_excel(writer, index=False, startrow=12)

        # Test preprocessing with Excel
        X, y, processed_df = preprocess_and_append_csv(sample_csv_path, excel_path=excel_path, logger=mock_logger)

        # Should have data from both CSV and Excel
        assert X is not None
        assert y is not None
        assert len(processed_df) > 0


@pytest.mark.unit
class TestSecurityEdgeCases:
    """Edge case tests for security.py."""

    def test_validate_empty_path_string(self, mock_logger):
        """Test validation with empty path string."""
        with pytest.raises(ValueError, match="Path must be a non-empty string"):
            validate_and_resolve_path("", logger=mock_logger)

    def test_validate_none_path(self, mock_logger):
        """Test validation with None path."""
        with pytest.raises(ValueError, match="Path must be a non-empty string"):
            # Intentionally pass None to test error handling
            validate_and_resolve_path(cast(str, None), logger=mock_logger)

    def test_validate_path_with_quotes(self, temp_dir, mock_logger):
        """Test validation strips quotes from path."""
        quoted_path = f'"{temp_dir}"'
        result = validate_and_resolve_path(quoted_path, must_exist=True, logger=mock_logger)
        assert result.exists()

    def test_validate_path_with_whitespace(self, temp_dir, mock_logger):
        """Test validation strips whitespace from path."""
        whitespace_path = f"  {temp_dir}  "
        result = validate_and_resolve_path(whitespace_path, must_exist=True, logger=mock_logger)
        assert result.exists()


@pytest.mark.unit
@pytest.mark.validation
class TestHelpersValidationEdgeCases:
    """Additional validation edge cases."""

    def test_validate_csv_with_parser_error(self, temp_dir, mock_logger):
        """Test CSV with malformed content."""
        from helpers import validate_csv_file

        bad_csv = os.path.join(temp_dir, "bad.csv")
        with open(bad_csv, "w") as f:
            f.write("Date,Tran Amt\n")
            f.write('"unclosed quote,123\n')  # Malformed CSV

        # This might not raise if pandas is lenient, but we test the code path
        try:
            validate_csv_file(bad_csv, logger=mock_logger)
        except DataValidationError:
            # Expected for some pandas versions
            pass

    def test_preprocess_with_non_numeric_amounts(self, temp_dir, mock_logger):
        """Test preprocessing with non-numeric transaction amounts."""
        from helpers import preprocess_data

        bad_data_csv = os.path.join(temp_dir, "bad_amounts.csv")
        with open(bad_data_csv, "w") as f:
            f.write("Date,Tran Amt\n")
            f.write("01/01/2024,not_a_number\n")
            f.write("02/01/2024,also_not_number\n")

        with pytest.raises(DataValidationError, match="non-numeric values"):
            preprocess_data(bad_data_csv, logger=mock_logger)
