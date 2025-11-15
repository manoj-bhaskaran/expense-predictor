"""
Unit tests for helpers.py module.

This module tests all helper functions including:
- File validation functions
- Data preprocessing functions
- Date manipulation functions
- Column name matching functions
"""

import os
import pytest
import pandas as pd
import tempfile
from datetime import datetime, timedelta
from pandas.tseries.offsets import DateOffset

# Import functions to test
from helpers import (
    validate_csv_file,
    validate_excel_file,
    validate_date_range,
    find_column_name,
    get_quarter_end_date,
    get_training_date_range,
    preprocess_data,
    prepare_future_dates,
    write_predictions,
    TRANSACTION_AMOUNT_LABEL,
    DAY_OF_WEEK,
    VALUE_DATE_LABEL
)
from exceptions import DataValidationError


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
        df = pd.DataFrame({'Tran Amt': [100, 200, 300]})
        with pytest.raises(DataValidationError, match="Date column not found"):
            validate_date_range(df, logger=mock_logger)

    def test_validate_date_range_all_nat(self, mock_logger):
        """Test validation with all NaT (Not a Time) values."""
        df = pd.DataFrame({'Date': [pd.NaT, pd.NaT, pd.NaT]})
        with pytest.raises(DataValidationError, match="No valid dates found"):
            validate_date_range(df, logger=mock_logger)

    def test_validate_date_range_future_dates(self, mock_logger):
        """Test validation with only future dates."""
        future_date = datetime.now() + timedelta(days=365)
        df = pd.DataFrame({
            'Date': pd.date_range(start=future_date, periods=5, freq='D')
        })
        with pytest.raises(DataValidationError, match="Data contains only future dates"):
            validate_date_range(df, logger=mock_logger)

    def test_validate_date_range_without_logger(self, sample_dataframe):
        """Test validation without logger."""
        validate_date_range(sample_dataframe)


@pytest.mark.unit
class TestFindColumnName:
    """Tests for find_column_name function."""

    def test_find_column_name_exact_match(self):
        """Test finding column with exact match."""
        columns = pd.Index(['Date', 'Tran Amt', 'Value Date'])
        result = find_column_name(columns, 'Date')
        assert result == 'Date'

    def test_find_column_name_normalized_match(self):
        """Test finding column with normalized spacing (no space before parenthesis)."""
        columns = pd.Index(['Withdrawal Amount(INR)', 'Deposit Amount(INR)'])
        result = find_column_name(columns, 'Withdrawal Amount (INR )')
        assert result == 'Withdrawal Amount(INR)'

    def test_find_column_name_spaced_match(self):
        """Test finding column with spaces around parentheses."""
        columns = pd.Index(['Withdrawal Amount (INR )', 'Deposit Amount (INR )'])
        result = find_column_name(columns, 'Withdrawal Amount(INR)')
        assert result == 'Withdrawal Amount (INR )'

    def test_find_column_name_fuzzy_match(self):
        """Test finding column with fuzzy base name match."""
        columns = pd.Index(['Withdrawal Amount (INR)', 'Deposit Amount (INR)'])
        result = find_column_name(columns, 'Withdrawal Amount (different)')
        assert result == 'Withdrawal Amount (INR)'

    def test_find_column_name_not_found(self):
        """Test finding column that doesn't exist."""
        columns = pd.Index(['Date', 'Amount'])
        result = find_column_name(columns, 'NonExistent')
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
        expected_start = sample_dataframe['Date'].min()
        assert result[0] == expected_start

        # Check that end date is yesterday
        expected_end = datetime.now() - timedelta(days=1)
        expected_end = expected_end.replace(hour=0, minute=0, second=0, microsecond=0)
        assert result[-1] == expected_end

    def test_get_training_date_range_custom_column(self, mock_logger):
        """Test getting date range with custom column name."""
        df = pd.DataFrame({
            'CustomDate': pd.date_range(start='2024-01-01', periods=10),
            'Tran Amt': [100] * 10
        })

        result = get_training_date_range(df, date_column='CustomDate', logger=mock_logger)

        # Check that result uses the custom column
        assert isinstance(result, pd.DatetimeIndex)
        assert result[0] == df['CustomDate'].min()

    def test_get_training_date_range_without_logger(self, sample_dataframe):
        """Test getting date range without logger."""
        result = get_training_date_range(sample_dataframe)

        # Check that function works without logger
        assert isinstance(result, pd.DatetimeIndex)
        assert result[0] == sample_dataframe['Date'].min()

    def test_get_training_date_range_nat_start_date(self, mock_logger):
        """Test getting date range with NaT start date."""
        df = pd.DataFrame({
            'Date': [pd.NaT, pd.NaT],
            'Tran Amt': [100, 200]
        })

        with pytest.raises(DataValidationError, match="Invalid start or end date found"):
            get_training_date_range(df, logger=mock_logger)

    def test_get_training_date_range_excludes_today(self, mock_logger):
        """Test that date range excludes today."""
        # Create DataFrame with dates including today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dates = pd.date_range(start=today - timedelta(days=10), end=today, freq='D')
        df = pd.DataFrame({
            'Date': dates,
            'Tran Amt': [100] * len(dates)
        })

        result = get_training_date_range(df, logger=mock_logger)

        # Check that today is NOT in the range
        assert today not in result

        # Check that yesterday IS in the range
        yesterday = today - timedelta(days=1)
        assert yesterday in result

    def test_get_training_date_range_time_normalized(self, mock_logger):
        """Test that end date has time normalized to midnight."""
        df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=5),
            'Tran Amt': [100] * 5
        })

        result = get_training_date_range(df, logger=mock_logger)

        # Check that the end date has time normalized
        end_date = result[-1]
        assert end_date.hour == 0
        assert end_date.minute == 0
        assert end_date.second == 0
        assert end_date.microsecond == 0

    def test_get_training_date_range_continuous_range(self, mock_logger):
        """Test that the returned date range is continuous."""
        df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=10),
            'Tran Amt': [100] * 10
        })

        result = get_training_date_range(df, logger=mock_logger)

        # Check that there are no gaps in the date range
        expected_length = (result[-1] - result[0]).days + 1
        assert len(result) == expected_length

    def test_get_training_date_range_single_date(self, mock_logger):
        """Test getting date range with single date in DataFrame."""
        single_date = (datetime.now() - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        df = pd.DataFrame({
            'Date': [single_date],
            'Tran Amt': [100]
        })

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
        assert 'Date' not in X_train.columns
        assert TRANSACTION_AMOUNT_LABEL not in X_train.columns

        # Check that y_train has the same length as X_train
        assert len(X_train) == len(y_train)

        # Check that feature engineering was applied
        assert 'Month' in X_train.columns
        assert 'Day of the Month' in X_train.columns

        # Check for one-hot encoded day of week columns (at least some should exist)
        day_columns = [col for col in X_train.columns if 'Day of the Week' in col]
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
        assert 'Date' in future_df.columns
        assert 'Month' in future_df.columns
        assert 'Day of the Month' in future_df.columns

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
        day_columns = [col for col in future_df.columns if 'Day of the Week' in col]
        assert len(day_columns) > 0

        # Check that Month and Day values are correct
        for idx, date in enumerate(future_dates):
            assert future_df.loc[idx, 'Month'] == date.month
            assert future_df.loc[idx, 'Day of the Month'] == date.day


@pytest.mark.unit
class TestWritePredictions:
    """Tests for write_predictions function."""

    def test_write_predictions_new_file(self, temp_dir, mock_logger):
        """Test writing predictions to a new file."""
        predicted_df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=5),
            'Predicted Tran Amt': [100.0, 150.0, 200.0, 175.0, 125.0]
        })
        output_path = os.path.join(temp_dir, 'predictions.csv')

        write_predictions(predicted_df, output_path, logger=mock_logger, skip_confirmation=True)

        # Check that file was created
        assert os.path.exists(output_path)

        # Read and verify content
        result_df = pd.read_csv(output_path)
        assert len(result_df) == 5
        assert 'Date' in result_df.columns
        assert 'Predicted Tran Amt' in result_df.columns

    def test_write_predictions_overwrite_with_backup(self, temp_dir, mock_logger):
        """Test overwriting existing file (backup creation tested in security module tests)."""
        predicted_df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=3),
            'Predicted Tran Amt': [100.0, 150.0, 200.0]
        })
        output_path = os.path.join(temp_dir, 'predictions.csv')

        # Create initial file
        write_predictions(predicted_df, output_path, logger=mock_logger, skip_confirmation=True)
        initial_df = pd.read_csv(output_path)
        assert abs(initial_df['Predicted Tran Amt'].iloc[0] - 100.0) < 0.001

        # Overwrite with new data
        new_predicted_df = pd.DataFrame({
            'Date': pd.date_range(start='2024-02-01', periods=3),
            'Predicted Tran Amt': [300.0, 350.0, 400.0]
        })
        write_predictions(new_predicted_df, output_path, logger=mock_logger, skip_confirmation=True)

        # Check that file was updated
        result_df = pd.read_csv(output_path)
        assert abs(result_df['Predicted Tran Amt'].iloc[0] - 300.0) < 0.001

        # Backup creation is tested separately in security module tests

    def test_write_predictions_csv_injection_prevention(self, temp_dir, mock_logger):
        """Test that CSV injection is prevented."""
        # Create DataFrame with potentially dangerous values
        predicted_df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=3),
            'Predicted Tran Amt': ['=1+1', '+2+2', '-3-3']
        })
        output_path = os.path.join(temp_dir, 'predictions.csv')

        write_predictions(predicted_df, output_path, logger=mock_logger, skip_confirmation=True)

        # Read and verify that dangerous characters are escaped
        with open(output_path, 'r') as f:
            content = f.read()
            # Check that formulas are escaped with single quote
            assert "'=1+1" in content or "\"'=1+1\"" in content

    def test_write_predictions_without_logger(self, temp_dir):
        """Test writing predictions without logger."""
        predicted_df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=3),
            'Predicted Tran Amt': [100.0, 150.0, 200.0]
        })
        output_path = os.path.join(temp_dir, 'predictions.csv')

        write_predictions(predicted_df, output_path, skip_confirmation=True)

        # Check that file was created
        assert os.path.exists(output_path)


@pytest.mark.unit
class TestConstants:
    """Test that constants are defined correctly."""

    def test_transaction_amount_label(self):
        """Test TRANSACTION_AMOUNT_LABEL constant."""
        assert TRANSACTION_AMOUNT_LABEL == 'Tran Amt'

    def test_day_of_week(self):
        """Test DAY_OF_WEEK constant."""
        assert DAY_OF_WEEK == 'Day of the Week'

    def test_value_date_label(self):
        """Test VALUE_DATE_LABEL constant."""
        assert VALUE_DATE_LABEL == 'Value Date'
