"""
Unit tests for helpers.py module.

This module tests all helper functions including:
- File validation functions
- Data preprocessing functions
- Date manipulation functions
- Column name matching functions
"""

import os
import tempfile
from datetime import datetime, timedelta

import pandas as pd
import pytest
from pandas.tseries.offsets import DateOffset

from exceptions import DataValidationError

# Import functions to test
from helpers import (
    DAY_OF_WEEK,
    TRANSACTION_AMOUNT_LABEL,
    VALUE_DATE_LABEL,
    chronological_train_test_split,
    find_column_name,
    get_quarter_end_date,
    get_training_date_range,
    prepare_future_dates,
    preprocess_data,
    validate_csv_file,
    validate_date_range,
    validate_excel_file,
    write_predictions,
)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateCsvFile:
    """Tests for validate_csv_file function."""

    def test_validate_csv_file_valid(self, sample_csv_path, mock_logger):
        """Test validation of a valid CSV file."""
        # Should not raise any exception
        validate_csv_file(sample_csv_path, logger=mock_logger)

    def test_validate_csv_file_not_found(self, mock_logger):
        """Test validation with non-existent file."""
        with pytest.raises(DataValidationError, match="CSV file not found"):
            validate_csv_file("/nonexistent/file.csv", logger=mock_logger)

    def test_validate_csv_file_is_directory(self, temp_dir, mock_logger):
        """Test validation when path is a directory."""
        with pytest.raises(DataValidationError, match="Path is not a file"):
            validate_csv_file(temp_dir, logger=mock_logger)

    def test_validate_csv_file_missing_columns(self, sample_invalid_columns_csv_path, mock_logger):
        """Test validation with missing required columns."""
        with pytest.raises(DataValidationError, match="Missing required columns"):
            validate_csv_file(sample_invalid_columns_csv_path, logger=mock_logger)

    def test_validate_csv_file_empty(self, sample_empty_csv_path, mock_logger):
        """Test validation with empty CSV file (has headers but no data rows)."""
        # A CSV with headers but no data rows is technically valid
        # It passes validation as it has the required columns
        validate_csv_file(sample_empty_csv_path, logger=mock_logger)

    def test_validate_csv_file_without_logger(self, sample_csv_path):
        """Test validation without logger (should still work)."""
        validate_csv_file(sample_csv_path)

    def test_validate_csv_file_completely_empty(self, mock_logger):
        """Test validation with completely empty CSV file (raises EmptyDataError)."""
        # Create a truly empty CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name
            # Don't write anything - file is completely empty

        try:
            with pytest.raises(DataValidationError, match="CSV file is empty"):
                validate_csv_file(temp_file, logger=mock_logger)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_validate_csv_file_parser_error(self, mock_logger):
        """Test validation with malformed CSV that causes parser error."""
        # Create a CSV with malformed content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name
            # Write malformed CSV content
            f.write("Date,Transaction Amount\n")
            f.write('"unclosed quote,123\n')
            f.write('normal,456\n')

        try:
            with pytest.raises(DataValidationError, match="not properly formatted"):
                validate_csv_file(temp_file, logger=mock_logger)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateExcelFile:
    """Tests for validate_excel_file function."""

    def test_validate_excel_file_not_found(self, mock_logger):
        """Test validation with non-existent Excel file."""
        with pytest.raises(DataValidationError, match="Excel file not found"):
            validate_excel_file("/nonexistent/file.xlsx", logger=mock_logger)

    def test_validate_excel_file_invalid_extension(self, temp_csv_file, mock_logger):
        """Test validation with invalid file extension."""
        with pytest.raises(DataValidationError, match="Invalid Excel file format"):
            validate_excel_file(temp_csv_file, logger=mock_logger)

    def test_validate_excel_file_is_directory(self, temp_dir, mock_logger):
        """Test validation when path is a directory."""
        with pytest.raises(DataValidationError, match="Path is not a file"):
            validate_excel_file(temp_dir, logger=mock_logger)

    def test_validate_excel_file_missing_openpyxl(self, mocker, mock_logger):
        """Test handling of missing openpyxl dependency for .xlsx files."""
        # Create a temporary .xlsx file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as f:
            temp_file = f.name

        try:
            # Mock pd.ExcelFile to raise ImportError for openpyxl
            mocker.patch("pandas.ExcelFile", side_effect=ImportError("Missing optional dependency 'openpyxl'"))

            with pytest.raises(DataValidationError, match="requires openpyxl"):
                validate_excel_file(temp_file, logger=mock_logger)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_validate_excel_file_missing_other_dependency(self, mocker, mock_logger):
        """Test handling of other missing dependencies for Excel files."""
        # Create a temporary .xlsx file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as f:
            temp_file = f.name

        try:
            # Mock pd.ExcelFile to raise a different ImportError
            mocker.patch("pandas.ExcelFile", side_effect=ImportError("Missing some_other_package"))

            with pytest.raises(DataValidationError, match="Missing required dependency"):
                validate_excel_file(temp_file, logger=mock_logger)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_validate_excel_file_corrupted_xls(self, mocker, mock_logger):
        """Test handling of corrupted .xls file."""
        # Create a temporary .xls file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xls", delete=False) as f:
            temp_file = f.name
            f.write("not valid xls content")

        try:
            # Mock to raise XLRDError
            import xlrd.biffh
            mocker.patch("pandas.ExcelFile", side_effect=xlrd.biffh.XLRDError("XLS format error"))

            with pytest.raises(DataValidationError, match="corrupted or cannot be read"):
                validate_excel_file(temp_file, logger=mock_logger)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_validate_excel_file_generic_corruption(self, mocker, mock_logger):
        """Test handling of generic Excel file corruption."""
        # Create a temporary .xlsx file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as f:
            temp_file = f.name

        try:
            # Mock pd.ExcelFile to raise ValueError
            mocker.patch("pandas.ExcelFile", side_effect=ValueError("File is corrupted"))

            with pytest.raises(DataValidationError, match="corrupted or cannot be read"):
                validate_excel_file(temp_file, logger=mock_logger)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_validate_excel_file_unexpected_exception(self, mocker, mock_logger):
        """Test handling of unexpected exceptions during Excel validation."""
        # Create a temporary .xlsx file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as f:
            temp_file = f.name

        try:
            # Mock pd.ExcelFile to raise an unexpected exception
            mocker.patch("pandas.ExcelFile", side_effect=Exception("Unexpected error"))

            with pytest.raises(DataValidationError, match="corrupted or cannot be read"):
                validate_excel_file(temp_file, logger=mock_logger)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateDateRange:
    """Tests for validate_date_range function."""

    def test_validate_date_range_valid(self, sample_dataframe, mock_logger):
        """Test validation with valid date range."""
        # Should not raise any exception
        validate_date_range(sample_dataframe, logger=mock_logger)

    def test_validate_date_range_missing_date_column(self, mock_logger):
        """Test validation with missing Date column."""
        df = pd.DataFrame({"Tran Amt": [100, 200, 300]})
        with pytest.raises(DataValidationError, match="Date column not found"):
            validate_date_range(df, logger=mock_logger)

    def test_validate_date_range_all_nat(self, mock_logger):
        """Test validation with all NaT (Not a Time) values."""
        df = pd.DataFrame({"Date": [pd.NaT, pd.NaT, pd.NaT]})
        with pytest.raises(DataValidationError, match="No valid dates found"):
            validate_date_range(df, logger=mock_logger)

    def test_validate_date_range_future_dates(self, mock_logger):
        """Test validation with only future dates."""
        future_date = datetime.now() + timedelta(days=365)
        df = pd.DataFrame({"Date": pd.date_range(start=future_date, periods=5, freq="D")})
        with pytest.raises(DataValidationError, match="Data contains only future dates"):
            validate_date_range(df, logger=mock_logger)

    def test_validate_date_range_without_logger(self, sample_dataframe):
        """Test validation without logger."""
        validate_date_range(sample_dataframe)

    def test_validate_date_range_with_nat_in_dates(self, mock_logger):
        """Test validation with some NaT values that result in invalid min/max."""
        # Create dataframe where all dates are NaT, caught by earlier check
        df = pd.DataFrame({"Date": [pd.NaT]})
        with pytest.raises(DataValidationError, match="No valid dates found"):
            validate_date_range(df, logger=mock_logger)

    def test_validate_date_range_with_some_nat_values(self, mock_logger):
        """Test validation with mix of valid and NaT dates."""
        # Create a dataframe with a mix that would result in NaT min/max
        # This is hard to trigger because pandas handles NaT in min/max
        # So we test a scenario where we have only NaT after filtering
        import pandas as pd
        df = pd.DataFrame({
            "Date": [pd.Timestamp("2024-01-01"), pd.NaT, pd.Timestamp("2024-01-03")]
        })
        # This should pass validation (NaT is ignored in min/max)
        validate_date_range(df, logger=mock_logger)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateMinimumData:
    """Tests for validate_minimum_data function."""

    def test_validate_minimum_data_sufficient_samples(self, mock_logger):
        """Test validation with sufficient data."""
        from helpers import validate_minimum_data
        # Create a dataframe with enough samples
        X = pd.DataFrame({"feature1": range(100)})
        # Should not raise any exception
        validate_minimum_data(X, min_total=30, min_test=10, logger=mock_logger)

    def test_validate_minimum_data_insufficient_total(self, mock_logger):
        """Test validation with insufficient total samples."""
        from helpers import validate_minimum_data
        # Create a dataframe with too few samples
        X = pd.DataFrame({"feature1": range(20)})  # Less than min_total=30
        with pytest.raises(DataValidationError, match="Insufficient data for training"):
            validate_minimum_data(X, min_total=30, min_test=10, logger=mock_logger)

    def test_validate_minimum_data_insufficient_test_samples(self, mock_logger):
        """Test validation with insufficient test samples after split."""
        from helpers import validate_minimum_data
        # Create a dataframe with enough total but not enough for test split
        # With test_size=0.2 (default in config), 40 samples gives 8 test samples
        X = pd.DataFrame({"feature1": range(40)})
        # Assuming config has test_size of 0.2, 40 * 0.2 = 8 < 10
        with pytest.raises(DataValidationError, match="Insufficient test data"):
            validate_minimum_data(X, min_total=30, min_test=10, logger=mock_logger)


@pytest.mark.unit
class TestFindColumnName:
    """Tests for find_column_name function."""

    def test_find_column_name_exact_match(self):
        """Test finding column with exact match."""
        columns = pd.Index(["Date", "Tran Amt", "Value Date"])
        result = find_column_name(columns, "Date")
        assert result == "Date"

    def test_find_column_name_normalized_match(self):
        """Test finding column with normalized spacing (no space before parenthesis)."""
        columns = pd.Index(["Withdrawal Amount(INR)", "Deposit Amount(INR)"])
        result = find_column_name(columns, "Withdrawal Amount (INR )")
        assert result == "Withdrawal Amount(INR)"

    def test_find_column_name_spaced_match(self):
        """Test finding column with spaces around parentheses."""
        columns = pd.Index(["Withdrawal Amount (INR )", "Deposit Amount (INR )"])
        result = find_column_name(columns, "Withdrawal Amount(INR)")
        assert result == "Withdrawal Amount (INR )"

    def test_find_column_name_fuzzy_match(self):
        """Test finding column with fuzzy base name match."""
        columns = pd.Index(["Withdrawal Amount (INR)", "Deposit Amount (INR)"])
        result = find_column_name(columns, "Withdrawal Amount (different)")
        assert result == "Withdrawal Amount (INR)"

    def test_find_column_name_not_found(self):
        """Test finding column that doesn't exist."""
        columns = pd.Index(["Date", "Amount"])
        result = find_column_name(columns, "NonExistent")
        assert result is None


@pytest.mark.unit
class TestGetQuarterEndDate:
    """Tests for get_quarter_end_date function."""

    def test_get_quarter_end_q1(self):
        """Test quarter end for Q1 (Jan-Mar)."""
        test_date = datetime(2024, 2, 15)
        result = get_quarter_end_date(test_date)
        expected = datetime(2024, 3, 31)
        assert result == expected

    def test_get_quarter_end_q2(self):
        """Test quarter end for Q2 (Apr-Jun)."""
        test_date = datetime(2024, 5, 15)
        result = get_quarter_end_date(test_date)
        expected = datetime(2024, 6, 30)
        assert result == expected

    def test_get_quarter_end_q3(self):
        """Test quarter end for Q3 (Jul-Sep)."""
        test_date = datetime(2024, 8, 15)
        result = get_quarter_end_date(test_date)
        expected = datetime(2024, 9, 30)
        assert result == expected

    def test_get_quarter_end_q4(self):
        """Test quarter end for Q4 (Oct-Dec)."""
        test_date = datetime(2024, 11, 15)
        result = get_quarter_end_date(test_date)
        expected = datetime(2024, 12, 31)
        assert result == expected

    def test_get_quarter_end_first_day_of_quarter(self):
        """Test quarter end on first day of quarter."""
        test_date = datetime(2024, 1, 1)
        result = get_quarter_end_date(test_date)
        expected = datetime(2024, 3, 31)
        assert result == expected

    def test_get_quarter_end_last_day_of_quarter(self):
        """Test quarter end on last day of quarter."""
        test_date = datetime(2024, 3, 31)
        result = get_quarter_end_date(test_date)
        expected = datetime(2024, 3, 31)
        assert result == expected

    def test_get_quarter_end_year_boundary(self):
        """Test quarter end at year boundary (Q4 to Q1)."""
        test_date = datetime(2023, 12, 31)
        result = get_quarter_end_date(test_date)
        expected = datetime(2023, 12, 31)
        assert result == expected


@pytest.mark.unit
@pytest.mark.validation
class TestGetTrainingDateRange:
    """Tests for get_training_date_range function."""

    def test_get_training_date_range_valid_data(self, sample_dataframe, mock_logger):
        """Test getting date range with valid data."""
        result = get_training_date_range(sample_dataframe, logger=mock_logger)

        # Check that result is a DatetimeIndex
        assert isinstance(result, pd.DatetimeIndex)

        # Check that start date matches the minimum date in the DataFrame
        expected_start = sample_dataframe["Date"].min()
        assert result[0] == expected_start

        # Check that end date is yesterday
        expected_end = datetime.now() - timedelta(days=1)
        expected_end = expected_end.replace(hour=0, minute=0, second=0, microsecond=0)
        assert result[-1] == expected_end

    def test_get_training_date_range_custom_column(self, mock_logger):
        """Test getting date range with custom column name."""
        df = pd.DataFrame({"CustomDate": pd.date_range(start="2024-01-01", periods=10), "Tran Amt": [100] * 10})

        result = get_training_date_range(df, date_column="CustomDate", logger=mock_logger)

        # Check that result uses the custom column
        assert isinstance(result, pd.DatetimeIndex)
        assert result[0] == df["CustomDate"].min()

    def test_get_training_date_range_without_logger(self, sample_dataframe):
        """Test getting date range without logger."""
        result = get_training_date_range(sample_dataframe)

        # Check that function works without logger
        assert isinstance(result, pd.DatetimeIndex)
        assert result[0] == sample_dataframe["Date"].min()

    def test_get_training_date_range_nat_start_date(self, mock_logger):
        """Test getting date range with NaT start date."""
        df = pd.DataFrame({"Date": [pd.NaT, pd.NaT], "Tran Amt": [100, 200]})

        with pytest.raises(DataValidationError, match="Invalid start or end date found"):
            get_training_date_range(df, logger=mock_logger)

    def test_get_training_date_range_excludes_today(self, mock_logger):
        """Test that date range excludes today."""
        # Create DataFrame with dates including today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dates = pd.date_range(start=today - timedelta(days=10), end=today, freq="D")
        df = pd.DataFrame({"Date": dates, "Tran Amt": [100] * len(dates)})

        result = get_training_date_range(df, logger=mock_logger)

        # Check that today is NOT in the range
        assert today not in result

        # Check that yesterday IS in the range
        yesterday = today - timedelta(days=1)
        assert yesterday in result

    def test_get_training_date_range_time_normalized(self, mock_logger):
        """Test that end date has time normalized to midnight."""
        df = pd.DataFrame({"Date": pd.date_range(start="2024-01-01", periods=5), "Tran Amt": [100] * 5})

        result = get_training_date_range(df, logger=mock_logger)

        # Check that the end date has time normalized
        end_date = result[-1]
        assert end_date.hour == 0
        assert end_date.minute == 0
        assert end_date.second == 0
        assert end_date.microsecond == 0

    def test_get_training_date_range_continuous_range(self, mock_logger):
        """Test that the returned date range is continuous."""
        df = pd.DataFrame({"Date": pd.date_range(start="2024-01-01", periods=10), "Tran Amt": [100] * 10})

        result = get_training_date_range(df, logger=mock_logger)

        # Check that there are no gaps in the date range
        expected_length = (result[-1] - result[0]).days + 1
        assert len(result) == expected_length

    def test_get_training_date_range_single_date(self, mock_logger):
        """Test getting date range with single date in DataFrame."""
        single_date = (datetime.now() - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        df = pd.DataFrame({"Date": [single_date], "Tran Amt": [100]})

        result = get_training_date_range(df, logger=mock_logger)

        # Check that range starts from the single date
        assert result[0] == single_date

        # Check that range ends at yesterday
        yesterday = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        assert result[-1] == yesterday


@pytest.mark.integration
class TestPreprocessData:
    """Tests for preprocess_data function."""

    def test_preprocess_data_valid_file(self, sample_csv_path, mock_logger):
        """Test preprocessing with valid CSV file."""
        X_train, y_train, df = preprocess_data(sample_csv_path, logger=mock_logger)

        # Check that data is returned
        assert X_train is not None
        assert y_train is not None
        assert df is not None

        # Check that X_train doesn't contain Date or Tran Amt columns
        assert "Date" not in X_train.columns
        assert TRANSACTION_AMOUNT_LABEL not in X_train.columns

        # Check that y_train has the same length as X_train
        assert len(X_train) == len(y_train)

        # Check that feature engineering was applied
        assert "Month" in X_train.columns
        assert "Day of the Month" in X_train.columns

        # Check for one-hot encoded day of week columns (at least some should exist)
        day_columns = [col for col in X_train.columns if "Day of the Week" in col]
        assert len(day_columns) > 0

    def test_preprocess_data_invalid_file(self, sample_invalid_columns_csv_path, mock_logger):
        """Test preprocessing with invalid CSV file."""
        with pytest.raises(DataValidationError, match="Missing required columns"):
            preprocess_data(sample_invalid_columns_csv_path, logger=mock_logger)

    def test_preprocess_data_nonexistent_file(self, mock_logger):
        """Test preprocessing with non-existent file."""
        with pytest.raises(DataValidationError):
            preprocess_data("/nonexistent/file.csv", logger=mock_logger)


@pytest.mark.unit
class TestPrepareFutureDates:
    """Tests for prepare_future_dates function."""

    def test_prepare_future_dates_default(self):
        """Test preparing future dates with default (quarter end)."""
        future_df, future_dates = prepare_future_dates()

        # Check that data is returned
        assert future_df is not None
        assert future_dates is not None

        # Check that future_df has the required columns
        assert "Date" in future_df.columns
        assert "Month" in future_df.columns
        assert "Day of the Month" in future_df.columns

        # Check that dates start from today
        assert future_dates[0].date() == datetime.now().date()

        # Check that end date is quarter end
        expected_end = get_quarter_end_date(datetime.now())
        assert future_dates[-1].date() == expected_end.date()

    def test_prepare_future_dates_custom_date(self):
        """Test preparing future dates with custom end date."""
        custom_date = (datetime.now() + timedelta(days=30)).strftime("%d-%m-%Y")
        future_df, future_dates = prepare_future_dates(custom_date)

        # Check that data is returned
        assert future_df is not None
        assert future_dates is not None

        # Check that dates start from today
        assert future_dates[0].date() == datetime.now().date()

        # Check that end date matches custom date
        expected_end = datetime.strptime(custom_date, "%d-%m-%Y")
        assert future_dates[-1].date() == expected_end.date()

    def test_prepare_future_dates_past_date(self):
        """Test preparing future dates with past date (should raise error)."""
        past_date = (datetime.now() - timedelta(days=30)).strftime("%d-%m-%Y")
        with pytest.raises(DataValidationError, match="Future date must be in the future"):
            prepare_future_dates(past_date)

    def test_prepare_future_dates_features(self):
        """Test that prepare_future_dates creates correct features."""
        custom_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")
        future_df, future_dates = prepare_future_dates(custom_date)

        # Check for one-hot encoded day of week columns
        day_columns = [col for col in future_df.columns if "Day of the Week" in col]
        assert len(day_columns) > 0

        # Check that Month and Day values are correct
        for idx, date in enumerate(future_dates):
            assert future_df.loc[idx, "Month"] == date.month
            assert future_df.loc[idx, "Day of the Month"] == date.day


@pytest.mark.unit
class TestWritePredictions:
    """Tests for write_predictions function."""

    def test_write_predictions_new_file(self, temp_dir, mock_logger):
        """Test writing predictions to a new file."""
        predicted_df = pd.DataFrame(
            {"Date": pd.date_range(start="2024-01-01", periods=5), "Predicted Tran Amt": [100.0, 150.0, 200.0, 175.0, 125.0]}
        )
        output_path = os.path.join(temp_dir, "predictions.csv")

        write_predictions(predicted_df, output_path, logger=mock_logger, skip_confirmation=True)

        # Check that file was created
        assert os.path.exists(output_path)

        # Read and verify content
        result_df = pd.read_csv(output_path)
        assert len(result_df) == 5
        assert "Date" in result_df.columns
        assert "Predicted Tran Amt" in result_df.columns

    def test_write_predictions_overwrite_with_backup(self, temp_dir, mock_logger):
        """Test overwriting existing file (backup creation tested in security module tests)."""
        predicted_df = pd.DataFrame(
            {"Date": pd.date_range(start="2024-01-01", periods=3), "Predicted Tran Amt": [100.0, 150.0, 200.0]}
        )
        output_path = os.path.join(temp_dir, "predictions.csv")

        # Create initial file
        write_predictions(predicted_df, output_path, logger=mock_logger, skip_confirmation=True)
        initial_df = pd.read_csv(output_path)
        assert abs(initial_df["Predicted Tran Amt"].iloc[0] - 100.0) < 0.001

        # Overwrite with new data
        new_predicted_df = pd.DataFrame(
            {"Date": pd.date_range(start="2024-02-01", periods=3), "Predicted Tran Amt": [300.0, 350.0, 400.0]}
        )
        write_predictions(new_predicted_df, output_path, logger=mock_logger, skip_confirmation=True)

        # Check that file was updated
        result_df = pd.read_csv(output_path)
        assert abs(result_df["Predicted Tran Amt"].iloc[0] - 300.0) < 0.001

        # Backup creation is tested separately in security module tests

    def test_write_predictions_csv_injection_prevention(self, temp_dir, mock_logger):
        """Test that CSV injection is prevented."""
        # Create DataFrame with potentially dangerous values
        predicted_df = pd.DataFrame(
            {"Date": pd.date_range(start="2024-01-01", periods=3), "Predicted Tran Amt": ["=1+1", "+2+2", "-3-3"]}
        )
        output_path = os.path.join(temp_dir, "predictions.csv")

        write_predictions(predicted_df, output_path, logger=mock_logger, skip_confirmation=True)

        # Read and verify that dangerous characters are escaped
        with open(output_path, "r") as f:
            content = f.read()
            # Check that formulas are escaped with single quote
            assert "'=1+1" in content or '"\'=1+1"' in content

    def test_write_predictions_without_logger(self, temp_dir):
        """Test writing predictions without logger."""
        predicted_df = pd.DataFrame(
            {"Date": pd.date_range(start="2024-01-01", periods=3), "Predicted Tran Amt": [100.0, 150.0, 200.0]}
        )
        output_path = os.path.join(temp_dir, "predictions.csv")

        write_predictions(predicted_df, output_path, skip_confirmation=True)

        # Check that file was created
        assert os.path.exists(output_path)


@pytest.mark.unit
class TestConstants:
    """Test that constants are defined correctly."""

    def test_transaction_amount_label(self):
        """Test TRANSACTION_AMOUNT_LABEL constant."""
        assert TRANSACTION_AMOUNT_LABEL == "Tran Amt"

    def test_day_of_week(self):
        """Test DAY_OF_WEEK constant."""
        assert DAY_OF_WEEK == "Day of the Week"

    def test_value_date_label(self):
        """Test VALUE_DATE_LABEL constant."""
        assert VALUE_DATE_LABEL == "Value Date"


@pytest.mark.unit
class TestChronologicalTrainTestSplit:
    """Tests for chronological_train_test_split function."""

    def _make_chronological_data(self, n=100):
        """Helper to create chronologically ordered test data."""
        dates = pd.date_range(start="2024-01-01", periods=n, freq="D")
        amounts = [50.0 + i * 2.0 for i in range(n)]
        df = pd.DataFrame({"Date": dates, TRANSACTION_AMOUNT_LABEL: amounts})
        # Add features
        df["Month"] = df["Date"].dt.month
        df["Day of the Month"] = df["Date"].dt.day
        X = df.drop(["Date", TRANSACTION_AMOUNT_LABEL], axis=1)
        y = df[TRANSACTION_AMOUNT_LABEL]
        return X, y, df

    def test_split_ratio(self, mock_logger):
        """Test that the split ratio matches the requested test_size."""
        X, y, df = self._make_chronological_data(100)

        X_train, X_test, y_train, y_test = chronological_train_test_split(
            X, y, df, test_size=0.2, logger=mock_logger
        )

        assert len(X_train) == 80
        assert len(X_test) == 20
        assert len(y_train) == 80
        assert len(y_test) == 20

    def test_no_temporal_overlap(self, mock_logger):
        """Test that training data dates are strictly before test data dates."""
        X, y, df = self._make_chronological_data(100)

        X_train, X_test, y_train, y_test = chronological_train_test_split(
            X, y, df, test_size=0.2, logger=mock_logger
        )

        split_idx = len(X_train)
        train_last_date = df["Date"].iloc[split_idx - 1]
        test_first_date = df["Date"].iloc[split_idx]

        assert train_last_date < test_first_date

    def test_train_indices_before_test(self, mock_logger):
        """Test that all training indices come before test indices."""
        X, y, df = self._make_chronological_data(100)

        X_train, X_test, _, _ = chronological_train_test_split(
            X, y, df, test_size=0.2, logger=mock_logger
        )

        assert X_train.index[-1] < X_test.index[0]

    def test_all_data_preserved(self, mock_logger):
        """Test that no data is lost in the split."""
        X, y, df = self._make_chronological_data(100)

        X_train, X_test, y_train, y_test = chronological_train_test_split(
            X, y, df, test_size=0.2, logger=mock_logger
        )

        assert len(X_train) + len(X_test) == len(X)
        assert len(y_train) + len(y_test) == len(y)

    def test_rejects_unsorted_data(self, mock_logger):
        """Test that non-chronological data raises DataValidationError."""
        dates = pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02"])
        df = pd.DataFrame({
            "Date": dates,
            TRANSACTION_AMOUNT_LABEL: [100, 200, 300],
            "Month": [1, 1, 1],
        })
        X = df.drop(["Date", TRANSACTION_AMOUNT_LABEL], axis=1)
        y = df[TRANSACTION_AMOUNT_LABEL]

        with pytest.raises(DataValidationError, match="not in chronological order"):
            chronological_train_test_split(X, y, df, test_size=0.3, logger=mock_logger)

    def test_rejects_duplicate_dates(self, mock_logger):
        """Test that duplicate dates raise DataValidationError.

        The pipeline should aggregate amounts per date, so duplicates
        indicate a preprocessing failure.
        """
        dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03"])
        df = pd.DataFrame({
            "Date": dates,
            TRANSACTION_AMOUNT_LABEL: [100, 200, 250, 300],
            "Month": [1, 1, 1, 1],
        })
        X = df.drop(["Date", TRANSACTION_AMOUNT_LABEL], axis=1)
        y = df[TRANSACTION_AMOUNT_LABEL]

        with pytest.raises(DataValidationError, match="duplicate dates"):
            chronological_train_test_split(X, y, df, test_size=0.25, logger=mock_logger)

    def test_different_test_sizes(self, mock_logger):
        """Test split with various test_size values."""
        X, y, df = self._make_chronological_data(100)

        for test_size in [0.1, 0.2, 0.3, 0.5]:
            X_train, X_test, _, _ = chronological_train_test_split(
                X, y, df, test_size=test_size, logger=mock_logger
            )
            expected_test = int(100 * test_size)
            assert len(X_test) == expected_test
            assert len(X_train) == 100 - expected_test

    def test_without_logger(self):
        """Test that split works without a logger."""
        X, y, df = self._make_chronological_data(50)

        X_train, X_test, y_train, y_test = chronological_train_test_split(
            X, y, df, test_size=0.2
        )

        assert len(X_train) + len(X_test) == 50


@pytest.mark.unit
class TestFutureDataLeakage:
    """Tests to detect future-data leakage in the ML pipeline.

    These tests verify that:
    - Training data never contains information from the test period
    - Features are derived only from each row's own date (no look-ahead)
    - The chronological split correctly separates past from future
    """

    def _make_pipeline_data(self, n=100):
        """Helper to create data that goes through the feature pipeline."""
        dates = pd.date_range(start="2024-01-01", periods=n, freq="D")
        amounts = [50.0 + i * 2.0 for i in range(n)]
        df = pd.DataFrame({"Date": dates, TRANSACTION_AMOUNT_LABEL: amounts})
        df[DAY_OF_WEEK] = df["Date"].dt.day_name()
        df["Month"] = df["Date"].dt.month
        df["Day of the Month"] = df["Date"].dt.day
        df = pd.get_dummies(df, columns=[DAY_OF_WEEK], drop_first=True)
        X = df.drop(["Date", TRANSACTION_AMOUNT_LABEL], axis=1)
        y = df[TRANSACTION_AMOUNT_LABEL]
        return X, y, df

    def test_no_future_targets_in_training(self, mock_logger):
        """Test that training targets do not contain values from the test period."""
        X, y, df = self._make_pipeline_data(100)

        X_train, X_test, y_train, y_test = chronological_train_test_split(
            X, y, df, test_size=0.2, logger=mock_logger
        )

        # Training target values should correspond to earlier time period
        train_dates = df["Date"].iloc[:len(X_train)]
        test_dates = df["Date"].iloc[len(X_train):]

        # No date in training should overlap with test dates
        assert not set(train_dates).intersection(set(test_dates))

        # Training targets should match the training date period
        assert len(y_train) == len(train_dates)
        assert len(y_test) == len(test_dates)

    def test_features_are_date_intrinsic(self, mock_logger):
        """Test that features are derived only from each row's own date.

        This ensures no look-ahead bias: each feature value depends only on
        the date of that row, not on future dates or target values.
        """
        X, y, df = self._make_pipeline_data(100)

        X_train, X_test, y_train, y_test = chronological_train_test_split(
            X, y, df, test_size=0.2, logger=mock_logger
        )

        split_idx = len(X_train)

        # Verify Month and Day features match their dates
        for i in range(split_idx):
            date = df["Date"].iloc[i]
            assert X_train["Month"].iloc[i] == date.month
            assert X_train["Day of the Month"].iloc[i] == date.day

        for i in range(len(X_test)):
            date = df["Date"].iloc[split_idx + i]
            assert X_test["Month"].iloc[i] == date.month
            assert X_test["Day of the Month"].iloc[i] == date.day

    def test_train_test_date_boundary_is_strict(self, mock_logger):
        """Test that the last training date is strictly before the first test date."""
        X, y, df = self._make_pipeline_data(100)

        X_train, X_test, _, _ = chronological_train_test_split(
            X, y, df, test_size=0.2, logger=mock_logger
        )

        split_idx = len(X_train)
        last_train_date = df["Date"].iloc[split_idx - 1]
        first_test_date = df["Date"].iloc[split_idx]

        assert last_train_date < first_test_date
        # They should be exactly 1 day apart for daily data
        assert (first_test_date - last_train_date).days == 1

    def test_no_shuffling_occurs(self, mock_logger):
        """Test that data order is preserved through the split (no shuffling)."""
        X, y, df = self._make_pipeline_data(100)

        X_train, X_test, y_train, y_test = chronological_train_test_split(
            X, y, df, test_size=0.2, logger=mock_logger
        )

        # Concatenating train and test should give back the original data
        X_reconstructed = pd.concat([X_train, X_test])
        y_reconstructed = pd.concat([y_train, y_test])

        pd.testing.assert_frame_equal(X_reconstructed, X)
        pd.testing.assert_series_equal(y_reconstructed, y)

    def test_leakage_detection_with_full_pipeline(self, mock_logger):
        """Integration test: verify no leakage when using preprocess_and_append_csv."""
        import os
        import tempfile

        # Create a temp CSV with known dates
        dates = pd.date_range(start="2024-01-01", periods=60, freq="D")
        amounts = [100.0 + i for i in range(60)]
        csv_df = pd.DataFrame({
            "Date": dates.strftime("%d/%m/%Y"),
            TRANSACTION_AMOUNT_LABEL: amounts,
        })

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_df.to_csv(f, index=False)
            csv_path = f.name

        try:
            from helpers import preprocess_and_append_csv

            X, y, processed_df, _ = preprocess_and_append_csv(csv_path, logger=mock_logger)

            X_train, X_test, y_train, y_test = chronological_train_test_split(
                X, y, processed_df, test_size=0.2, logger=mock_logger
            )

            split_idx = len(X_train)

            # Verify strict temporal ordering
            train_end = processed_df["Date"].iloc[split_idx - 1]
            test_start = processed_df["Date"].iloc[split_idx]
            assert train_end < test_start

            # Verify train/test sizes sum to total
            assert len(X_train) + len(X_test) == len(X)
        finally:
            os.remove(csv_path)


@pytest.mark.unit
@pytest.mark.transformation
class TestTargetTransformation:
    """Tests for target transformation functions."""

    def test_apply_log1p_transform(self, mock_logger):
        """Test log1p transformation."""
        import numpy as np
        from helpers import apply_target_transform

        y = pd.Series([0, 10, 100, 1000])
        y_transformed = apply_target_transform(y, method="log1p", logger=mock_logger)

        # Verify transformation is applied correctly
        expected = np.log1p(y)
        pd.testing.assert_series_equal(y_transformed, expected)

    def test_apply_log_transform(self, mock_logger):
        """Test log transformation with positive values."""
        import numpy as np
        from helpers import apply_target_transform

        y = pd.Series([1, 10, 100, 1000])
        y_transformed = apply_target_transform(y, method="log", logger=mock_logger)

        # Verify transformation is applied correctly
        expected = np.log(y)
        pd.testing.assert_series_equal(y_transformed, expected)

    def test_log_transform_with_zeros_raises_error(self, mock_logger):
        """Test that log transformation raises error with zero values."""
        from helpers import apply_target_transform

        y = pd.Series([0, 10, 100])
        with pytest.raises(ValueError, match="Cannot apply log transformation.*non-positive values"):
            apply_target_transform(y, method="log", logger=mock_logger)

    def test_log_transform_with_negative_raises_error(self, mock_logger):
        """Test that log transformation raises error with negative values."""
        from helpers import apply_target_transform

        y = pd.Series([-5, 10, 100])
        with pytest.raises(ValueError, match="Cannot apply log transformation.*non-positive values"):
            apply_target_transform(y, method="log", logger=mock_logger)

    def test_invalid_transform_method_raises_error(self, mock_logger):
        """Test that invalid transformation method raises error."""
        from helpers import apply_target_transform

        y = pd.Series([10, 100, 1000])
        with pytest.raises(ValueError, match="Unsupported transformation method"):
            apply_target_transform(y, method="invalid", logger=mock_logger)

    def test_inverse_log1p_transform(self, mock_logger):
        """Test inverse log1p transformation."""
        import numpy as np
        from helpers import apply_target_transform, inverse_target_transform

        y = pd.Series([0, 10, 100, 1000])
        y_transformed = apply_target_transform(y, method="log1p", logger=mock_logger)
        y_inverse = inverse_target_transform(y_transformed.values, method="log1p", logger=mock_logger)

        # Verify inverse returns original values (within floating point precision)
        np.testing.assert_allclose(y_inverse, y.values, rtol=1e-10)

    def test_inverse_log_transform(self, mock_logger):
        """Test inverse log transformation."""
        import numpy as np
        from helpers import apply_target_transform, inverse_target_transform

        y = pd.Series([1, 10, 100, 1000])
        y_transformed = apply_target_transform(y, method="log", logger=mock_logger)
        y_inverse = inverse_target_transform(y_transformed.values, method="log", logger=mock_logger)

        # Verify inverse returns original values (within floating point precision)
        np.testing.assert_allclose(y_inverse, y.values, rtol=1e-10)

    def test_inverse_invalid_method_raises_error(self, mock_logger):
        """Test that invalid inverse transformation method raises error."""
        import numpy as np
        from helpers import inverse_target_transform

        y_pred = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError, match="Unsupported transformation method"):
            inverse_target_transform(y_pred, method="invalid", logger=mock_logger)


@pytest.mark.unit
@pytest.mark.metrics
class TestRobustMetrics:
    """Tests for robust evaluation metrics functions."""

    def test_median_absolute_error(self):
        """Test Median Absolute Error calculation."""
        import numpy as np
        from helpers import calculate_median_absolute_error

        y_true = np.array([100, 200, 300, 400, 500])
        y_pred = np.array([110, 190, 310, 390, 510])
        
        medae = calculate_median_absolute_error(y_true, y_pred)
        
        # Absolute errors: [10, 10, 10, 10, 10]
        # Median: 10
        assert abs(medae - 10.0) < 1e-9

    def test_median_absolute_error_with_outlier(self):
        """Test MedAE is robust to outliers."""
        import numpy as np
        from helpers import calculate_median_absolute_error

        y_true = np.array([100, 200, 300, 400, 500])
        y_pred = np.array([110, 190, 310, 390, 1000])  # Large outlier
        
        medae = calculate_median_absolute_error(y_true, y_pred)
        
        # Absolute errors: [10, 10, 10, 10, 500]
        # Median: 10 (robust to the outlier)
        assert abs(medae - 10.0) < 1e-9

    def test_smape_perfect_prediction(self):
        """Test SMAPE with perfect predictions."""
        import numpy as np
        from helpers import calculate_smape

        y_true = np.array([100, 200, 300])
        y_pred = np.array([100, 200, 300])
        
        smape = calculate_smape(y_true, y_pred)
        
        # Perfect prediction should give 0%
        assert abs(smape) < 1e-9

    def test_smape_calculation(self):
        """Test SMAPE calculation."""
        import numpy as np
        from helpers import calculate_smape

        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 330])
        
        smape = calculate_smape(y_true, y_pred)
        
        # SMAPE = mean(|y_true - y_pred| / ((|y_true| + |y_pred|) / 2)) * 100
        # For [100, 200, 300] vs [110, 190, 330]:
        # Errors: [10, 10, 30]
        # Denominators: [105, 195, 315]
        # Ratios: [10/105, 10/195, 30/315]
        # Mean * 100
        expected = np.mean([10/105, 10/195, 30/315]) * 100
        assert abs(smape - expected) < 0.01
        # Verify smape is approximately 8.06%
        assert abs(smape - 8.06) < 0.1

    def test_smape_handles_zeros(self):
        """Test SMAPE handles zeros correctly."""
        import numpy as np
        from helpers import calculate_smape

        y_true = np.array([0, 100, 200])
        y_pred = np.array([0, 110, 190])
        
        smape = calculate_smape(y_true, y_pred)
        
        # When both are zero, should contribute 0 to SMAPE
        # For [0, 100, 200] vs [0, 110, 190]:
        # Errors: [0, 10, 10]
        # Denominators: [0, 105, 195]
        # Ratios: [0, 10/105, 10/195]
        expected = np.mean([0, 10/105, 10/195]) * 100
        assert abs(smape - expected) < 0.01

    def test_percentile_errors_default(self):
        """Test percentile errors calculation with default percentiles."""
        import numpy as np
        from helpers import calculate_percentile_errors

        y_true = np.array([100] * 100)
        y_pred = np.arange(100)  # Errors from 0 to 99
        
        percentiles = calculate_percentile_errors(y_true, y_pred)
        
        # Check that default percentiles are calculated
        assert "P50" in percentiles
        assert "P75" in percentiles
        assert "P90" in percentiles
        
        # P50 should be around 50
        assert abs(percentiles["P50"] - 50) < 5
        # P75 should be around 75
        assert abs(percentiles["P75"] - 75) < 5
        # P90 should be around 90
        assert abs(percentiles["P90"] - 90) < 5

    def test_percentile_errors_custom(self):
        """Test percentile errors with custom percentiles."""
        import numpy as np
        from helpers import calculate_percentile_errors

        y_true = np.array([100] * 100)
        y_pred = np.arange(100)
        
        percentiles = calculate_percentile_errors(y_true, y_pred, percentiles=[25, 50, 95])
        
        assert "P25" in percentiles
        assert "P50" in percentiles
        assert "P95" in percentiles
        assert "P75" not in percentiles  # Not requested
        assert "P90" not in percentiles  # Not requested
