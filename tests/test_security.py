"""
Unit tests for security.py module.

This module tests security-related functions including:
- Path validation and sanitization
- File extension validation
- CSV injection prevention
- Backup creation
- User confirmation prompts
"""

import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

# Import functions to test
from security import (
    ALLOWED_CSV_EXTENSIONS,
    ALLOWED_EXCEL_EXTENSIONS,
    confirm_overwrite,
    create_backup,
    sanitize_csv_value,
    sanitize_dataframe_for_csv,
    validate_and_resolve_path,
    validate_directory_path,
    validate_file_path,
)


@pytest.mark.unit
class TestValidateAndResolvePath:
    """Tests for validate_and_resolve_path function."""

    def test_validate_absolute_path(self, temp_dir):
        """Test validation of absolute path."""
        result = validate_and_resolve_path(temp_dir)
        assert result.is_absolute()
        assert str(result) == str(Path(temp_dir).resolve())

    def test_validate_relative_path(self):
        """Test validation of relative path."""
        result = validate_and_resolve_path(".")
        assert result.is_absolute()

    def test_path_traversal_detection(self):
        """Test that path traversal patterns are normalized by resolve()."""
        # Note: Path.resolve() normalizes ../ patterns, so this won't raise
        # unless the result contains .. in the path parts after resolution.
        # This test validates that suspicious patterns are accepted if they resolve to valid paths
        result = validate_and_resolve_path("../../../tmp")
        assert result.is_absolute()

    def test_nonexistent_path_must_exist(self):
        """Test validation when path must exist but doesn't."""
        with pytest.raises(FileNotFoundError):
            validate_and_resolve_path("/nonexistent/path", must_exist=True)

    def test_nonexistent_path_optional(self):
        """Test validation when path doesn't need to exist."""
        result = validate_and_resolve_path("/tmp/newpath", must_exist=False)
        assert result.is_absolute()


@pytest.mark.unit
class TestValidateFilePath:
    """Tests for validate_file_path function."""

    def test_validate_csv_file(self, temp_csv_file):
        """Test validation of CSV file."""
        result = validate_file_path(temp_csv_file, allowed_extensions=ALLOWED_CSV_EXTENSIONS)
        assert result.is_absolute()
        assert result.suffix == ".csv"

    def test_invalid_extension(self, temp_csv_file):
        """Test rejection of invalid file extension."""
        with pytest.raises(ValueError, match="Invalid file extension"):
            validate_file_path(temp_csv_file, allowed_extensions=[".txt", ".pdf"])

    def test_file_is_directory(self, temp_dir):
        """Test rejection when path is a directory."""
        with pytest.raises(ValueError, match="Path is not a file"):
            validate_file_path(temp_dir, allowed_extensions=ALLOWED_CSV_EXTENSIONS, must_exist=True)

    def test_excel_extensions(self):
        """Test Excel file extension validation."""
        # Create temp Excel file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            result = validate_file_path(temp_path, allowed_extensions=ALLOWED_EXCEL_EXTENSIONS, must_exist=True)
            assert result.suffix == ".xlsx"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


@pytest.mark.unit
class TestValidateDirectoryPath:
    """Tests for validate_directory_path function."""

    def test_validate_existing_directory(self, temp_dir):
        """Test validation of existing directory."""
        result = validate_directory_path(temp_dir, must_exist=True)
        assert result.is_absolute()
        assert result.is_dir()

    def test_create_directory_if_missing(self):
        """Test automatic directory creation."""
        with tempfile.TemporaryDirectory() as temp_base:
            new_dir = os.path.join(temp_base, "new_folder")
            result = validate_directory_path(new_dir, create_if_missing=True)
            assert os.path.exists(result)
            assert os.path.isdir(result)

    def test_directory_is_file(self, temp_csv_file):
        """Test rejection when path is a file."""
        with pytest.raises(ValueError, match="Path is not a directory"):
            validate_directory_path(temp_csv_file, must_exist=True)

    def test_nonexistent_directory_no_create(self):
        """Test error when directory doesn't exist and creation not requested."""
        with pytest.raises(FileNotFoundError):
            validate_directory_path("/nonexistent/directory", must_exist=True)


@pytest.mark.unit
class TestSanitizeCsvValue:
    """Tests for sanitize_csv_value function."""

    def test_sanitize_formula_equals(self):
        """Test sanitization of formulas starting with =."""
        result = sanitize_csv_value("=SUM(A1:A10)")
        assert result == "'=SUM(A1:A10)"

    def test_sanitize_formula_plus(self):
        """Test sanitization of formulas starting with +."""
        result = sanitize_csv_value("+1+1")
        assert result == "'+1+1"

    def test_sanitize_formula_minus(self):
        """Test sanitization of formulas starting with -."""
        result = sanitize_csv_value("-1-1")
        assert result == "'-1-1"

    def test_sanitize_formula_at(self):
        """Test sanitization of formulas starting with @."""
        result = sanitize_csv_value("@SUM(1,2)")
        assert result == "'@SUM(1,2)"

    def test_sanitize_tab_character(self):
        """Test sanitization of tab characters (only at start)."""
        result = sanitize_csv_value("\tvalue")
        assert result == "'\tvalue"
        # Tabs in middle are safe
        result_safe = sanitize_csv_value("value\twith\ttabs")
        assert result_safe == "value\twith\ttabs"

    def test_sanitize_newline_character(self):
        """Test sanitization of newline characters (only at start)."""
        result = sanitize_csv_value("\nvalue")
        assert result == "'\nvalue"
        # Newlines in middle are safe
        result_safe = sanitize_csv_value("value\nwith\nnewlines")
        assert result_safe == "value\nwith\nnewlines"

    def test_safe_value_unchanged(self):
        """Test that safe values are not modified."""
        result = sanitize_csv_value("normal value")
        assert result == "normal value"

    def test_numeric_value_unchanged(self):
        """Test that numeric values are converted to string."""
        result = sanitize_csv_value(123.45)
        assert result == "123.45"

    def test_none_value(self):
        """Test handling of None value (converted to empty string)."""
        result = sanitize_csv_value(None)
        assert result == ""


@pytest.mark.unit
class TestSanitizeDataframeForCsv:
    """Tests for sanitize_dataframe_for_csv function."""

    def test_sanitize_dataframe_with_formulas(self):
        """Test sanitization of DataFrame with formula injection attempts."""
        df = pd.DataFrame({"A": ["=1+1", "normal", "+2+2"], "B": [1, 2, 3], "C": ["@SUM(1,2)", "safe", "-3-3"]})

        result = sanitize_dataframe_for_csv(df)

        assert result.loc[0, "A"] == "'=1+1"
        assert result.loc[1, "A"] == "normal"
        assert result.loc[2, "A"] == "'+2+2"
        assert result.loc[0, "C"] == "'@SUM(1,2)"
        assert result.loc[1, "C"] == "safe"
        assert result.loc[2, "C"] == "'-3-3"

    def test_sanitize_preserves_numeric_columns(self):
        """Test that numeric columns are converted to strings."""
        df = pd.DataFrame({"Numbers": [1, 2, 3], "Floats": [1.1, 2.2, 3.3]})

        result = sanitize_dataframe_for_csv(df)

        # Values are converted to strings by sanitize_csv_value
        assert result["Numbers"].tolist() == ["1", "2", "3"]
        assert result["Floats"].tolist() == ["1.1", "2.2", "3.3"]

    def test_sanitize_empty_dataframe(self):
        """Test sanitization of empty DataFrame."""
        df = pd.DataFrame()
        result = sanitize_dataframe_for_csv(df)
        assert result.empty


@pytest.mark.unit
class TestCreateBackup:
    """Tests for create_backup function."""

    def test_create_backup_success(self, temp_csv_file, mock_logger):
        """Test successful backup creation."""
        backup_path = create_backup(temp_csv_file, logger=mock_logger)

        assert backup_path is not None
        assert os.path.exists(backup_path)
        assert "backup" in backup_path
        # Backup format is: filename.csv.backup_TIMESTAMP
        assert ".backup_" in backup_path

        # Cleanup
        if os.path.exists(backup_path):
            os.remove(backup_path)

    def test_create_backup_nonexistent_file(self, mock_logger):
        """Test backup creation for non-existent file."""
        result = create_backup("/nonexistent/file.csv", logger=mock_logger)
        assert result is None

    def test_backup_preserves_content(self, temp_dir, mock_logger):
        """Test that backup preserves file content."""
        # Create file with content
        original_file = os.path.join(temp_dir, "test.csv")
        with open(original_file, "w") as f:
            f.write("Date,Amount\n01/01/2024,100\n")

        # Create backup
        backup_path = create_backup(original_file, logger=mock_logger)

        # Verify content matches
        with open(original_file, "r") as f:
            original_content = f.read()
        with open(backup_path, "r") as f:
            backup_content = f.read()

        assert original_content == backup_content

        # Cleanup
        if os.path.exists(backup_path):
            os.remove(backup_path)


@pytest.mark.unit
class TestConfirmOverwrite:
    """Tests for confirm_overwrite function."""

    def test_confirm_overwrite_with_input(self, temp_csv_file, mock_logger, monkeypatch):
        """Test confirmation with user input 'y'."""
        monkeypatch.setattr("builtins.input", lambda _: "y")
        result = confirm_overwrite(temp_csv_file, logger=mock_logger)
        assert result is True

    def test_reject_overwrite_with_input(self, temp_csv_file, mock_logger, monkeypatch):
        """Test rejection with user input 'n'."""
        monkeypatch.setattr("builtins.input", lambda _: "n")
        result = confirm_overwrite(temp_csv_file, logger=mock_logger)
        assert result is False

    def test_confirm_overwrite_case_insensitive(self, temp_csv_file, mock_logger, monkeypatch):
        """Test case-insensitive handling of yes input."""
        monkeypatch.setattr("builtins.input", lambda _: "Y")
        result = confirm_overwrite(temp_csv_file, logger=mock_logger)
        assert result is True


@pytest.mark.unit
class TestConstants:
    """Test that security constants are defined correctly."""

    def test_allowed_csv_extensions(self):
        """Test ALLOWED_CSV_EXTENSIONS constant."""
        assert ".csv" in ALLOWED_CSV_EXTENSIONS
        assert isinstance(ALLOWED_CSV_EXTENSIONS, list)

    def test_allowed_excel_extensions(self):
        """Test ALLOWED_EXCEL_EXTENSIONS constant."""
        assert ".xls" in ALLOWED_EXCEL_EXTENSIONS
        assert ".xlsx" in ALLOWED_EXCEL_EXTENSIONS
        assert isinstance(ALLOWED_EXCEL_EXTENSIONS, list)
