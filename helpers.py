import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import xlrd
from pandas.tseries.offsets import DateOffset

import python_logging_framework as plog
from config import config
from constants import DAY_OF_WEEK, TRANSACTION_AMOUNT_LABEL, VALUE_DATE_LABEL
from exceptions import DataValidationError
from security import confirm_overwrite, sanitize_dataframe_for_csv


def validate_csv_file(file_path: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Validate that CSV file exists and has required columns.

    Parameters:
    file_path (str): Path to the CSV file
    logger (logging.Logger, optional): Logger instance for logging messages

    Raises:
    DataValidationError: If the CSV file does not exist, is not a file,
                        has missing required columns, is empty, or is not properly formatted
    """
    # Check if file exists
    if not os.path.exists(file_path):
        plog.log_error(logger, f"CSV file not found: {file_path}")
        raise DataValidationError(f"CSV file not found: {file_path}")

    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        plog.log_error(logger, f"Path is not a file: {file_path}")
        raise DataValidationError(f"Path is not a file: {file_path}")

    # Try to read the CSV and check for required columns
    try:
        df = pd.read_csv(file_path, nrows=0)  # Read only headers
        columns = df.columns.tolist()

        # Check for required columns
        required_columns = ["Date", TRANSACTION_AMOUNT_LABEL]
        missing_columns = [col for col in required_columns if col not in columns]

        if missing_columns:
            plog.log_error(logger, f"Missing required columns in CSV: {missing_columns}. Found columns: {columns}")
            raise DataValidationError(f"Missing required columns in CSV file: {missing_columns}. Found columns: {columns}")

        plog.log_info(logger, f"CSV file validation passed: {file_path}")
    except pd.errors.EmptyDataError as e:
        plog.log_error(logger, f"CSV file is empty: {file_path}")
        raise DataValidationError(f"CSV file is empty: {file_path}") from e
    except pd.errors.ParserError as e:
        plog.log_error(logger, f"CSV file parsing error: {e}")
        raise DataValidationError(f"CSV file is not properly formatted: {e}") from e


def validate_excel_file(file_path: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Validate that Excel file exists and has a valid format.

    WARNING: Excel files from untrusted sources may contain malicious formulas or macros.
    Only process Excel files from trusted sources. This function does not validate
    or sanitize Excel cell contents for potential security threats.

    Parameters:
    file_path (str): Path to the Excel file
    logger (logging.Logger, optional): Logger instance for logging messages

    Raises:
    DataValidationError: If the Excel file does not exist, is not a file,
                        has an invalid format, or is corrupted
    """
    # Security warning
    plog.log_info(logger, f"WARNING: Processing Excel file from: {file_path}")
    plog.log_info(logger, "Ensure this file is from a trusted source. Excel files may contain formulas or macros.")

    # Check if file exists
    if not os.path.exists(file_path):
        plog.log_error(logger, f"Excel file not found: {file_path}")
        raise DataValidationError(f"Excel file not found: {file_path}")

    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        plog.log_error(logger, f"Path is not a file: {file_path}")
        raise DataValidationError(f"Path is not a file: {file_path}")

    # Check file extension
    valid_extensions = [".xls", ".xlsx"]
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension not in valid_extensions:
        plog.log_error(logger, f"Invalid Excel file format: {file_extension}. Expected: {valid_extensions}")
        raise DataValidationError(f"Invalid Excel file format: {file_extension}. Expected one of: {valid_extensions}")

    # Try to open the Excel file to ensure it's valid
    try:
        engine = "xlrd" if file_path.endswith(".xls") else "openpyxl"
        pd.ExcelFile(file_path, engine=engine)
        plog.log_info(logger, f"Excel file validation passed: {file_path}")
    except ImportError as e:
        # Missing openpyxl dependency for .xlsx files
        if "openpyxl" in str(e):
            plog.log_error(logger, f"Missing openpyxl dependency for .xlsx file processing: {e}")
            raise DataValidationError(
                f"Processing .xlsx files requires openpyxl. "
                f"Install it with: pip install openpyxl"
            ) from e
        # Other import errors
        plog.log_error(logger, f"Missing dependency for Excel file processing: {e}")
        raise DataValidationError(f"Missing required dependency for Excel processing: {e}") from e
    except xlrd.biffh.XLRDError as e:
        # Corrupted or invalid .xls file
        plog.log_error(logger, f"Excel file is corrupted or invalid (XLS format error): {e}")
        raise DataValidationError(f"Excel file is corrupted or cannot be read: {e}") from e
    except (ValueError, KeyError) as e:
        # Invalid file format or structure issues from openpyxl/pandas
        plog.log_error(logger, f"Excel file is corrupted or invalid (format error): {e}")
        raise DataValidationError(f"Excel file is corrupted or cannot be read: {e}") from e
    except Exception as e:
        # Catch any other unexpected errors and provide context
        # This includes openpyxl exceptions without explicit import
        plog.log_error(logger, f"Excel file validation failed: {e}")
        raise DataValidationError(f"Excel file is corrupted or cannot be read: {e}") from e


def validate_date_range(df: pd.DataFrame, logger: Optional[logging.Logger] = None) -> None:
    """
    Validate date range in the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame with 'Date' column
    logger (logging.Logger, optional): Logger instance for logging messages

    Raises:
    DataValidationError: If date range is invalid (missing Date column,
                        no valid dates, NaT values, or all future dates)
    """
    if "Date" not in df.columns:
        plog.log_error(logger, "Date column not found in DataFrame")
        raise DataValidationError("Date column not found in DataFrame")

    # Check if there are any valid dates
    if df["Date"].isna().all():
        plog.log_error(logger, "No valid dates found in the data")
        raise DataValidationError("No valid dates found in the data")

    start_date = df["Date"].min()
    end_date = df["Date"].max()

    # Check for NaT (Not a Time) values
    if pd.isna(start_date) or pd.isna(end_date):
        plog.log_error(logger, "Invalid dates found in the data (NaT values)")
        raise DataValidationError("Invalid dates found in the data. Please ensure all dates are properly formatted.")

    # Check if dates are in the future (beyond today)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if start_date > today:
        plog.log_error(logger, f"Data contains only future dates. Start date: {start_date}, Today: {today}")
        raise DataValidationError(f"Data contains only future dates. Start date: {start_date.strftime('%Y-%m-%d')}")

    # Log date range info
    plog.log_info(
        logger, f"Date range validation passed. Start: {start_date.strftime('%Y-%m-%d')}, End: {end_date.strftime('%Y-%m-%d')}"
    )


def find_column_name(df_columns: pd.Index, expected_name: str) -> Optional[str]:
    """
    Find a column name that matches the expected name with flexible formatting.

    This function handles variations in spacing and parentheses formatting
    (e.g., 'Withdrawal Amount (INR )' vs 'Withdrawal Amount(INR)').

    Parameters:
    df_columns (pd.Index): The DataFrame column names to search
    expected_name (str): The expected column name with potential formatting variations

    Returns:
    str: The actual column name found in the DataFrame, or None if not found
    """
    # First try exact match
    if expected_name in df_columns:
        return expected_name

    # Normalize the expected name (remove extra spaces around parentheses)
    normalized_expected = expected_name.replace(" (", "(").replace(" )", ")")

    # Try normalized version
    if normalized_expected in df_columns:
        return normalized_expected

    # Try with spaces around parentheses
    spaced_expected = expected_name.replace("(", " (").replace(")", " )")
    if spaced_expected in df_columns:
        return spaced_expected

    # If still not found, try fuzzy matching by checking if the base name matches
    base_name = expected_name.split("(")[0].strip()
    for col in df_columns:
        if col.startswith(base_name) and "(" in col:
            return col

    return None


def chronological_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    processed_df: pd.DataFrame,
    test_size: float = 0.2,
    logger: Optional[logging.Logger] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into training and test sets using strict chronological ordering.

    Ensures no future data leaks into the training set by splitting based on
    temporal position: the first (1 - test_size) fraction of data is used for
    training and the remaining fraction for testing.

    The input data must contain exactly one row per date (strictly increasing
    dates with no duplicates). The upstream pipeline enforces this via
    drop_duplicates and date-range reindexing, but this function validates
    the invariant and raises an error if violated.

    Parameters:
        X: Feature DataFrame (without Date column).
        y: Target Series.
        processed_df: The processed DataFrame containing the 'Date' column,
            aligned with X and y by index.
        test_size: Fraction of data to use for testing (0.0 to 1.0).
        logger: Logger instance for logging messages.

    Returns:
        Tuple of (X_train, X_test, y_train, y_test).

    Raises:
        DataValidationError: If data is not in chronological order or
            contains duplicate dates.
    """
    # Validate strictly increasing chronological order (no duplicate dates).
    # The upstream pipeline (preprocess_and_append_csv / _process_dataframe)
    # guarantees one row per date via drop_duplicates + date-range reindexing.
    # We validate both invariants here as a defensive check.
    dates = processed_df["Date"]
    if not dates.is_monotonic_increasing:
        plog.log_error(logger, "Data is not in chronological order. Cannot perform time-aware split.")
        raise DataValidationError(
            "Data is not in chronological order. "
            "Ensure data is sorted by date before splitting."
        )

    if not dates.is_unique:
        plog.log_error(logger, "Data contains duplicate dates. Each date must have exactly one record.")
        raise DataValidationError(
            "Data contains duplicate dates. The pipeline should aggregate "
            "all amounts for a given date into a single record."
        )

    # Calculate split index
    n_samples = len(X)
    split_idx = n_samples - int(n_samples * test_size)

    # Perform chronological split
    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]

    # Log date boundaries
    train_start = dates.iloc[0].strftime("%Y-%m-%d")
    train_end = dates.iloc[split_idx - 1].strftime("%Y-%m-%d")
    test_start = dates.iloc[split_idx].strftime("%Y-%m-%d")
    test_end = dates.iloc[-1].strftime("%Y-%m-%d")

    plog.log_info(
        logger,
        f"Chronological train/test split: "
        f"{len(X_train)} train samples [{train_start} to {train_end}], "
        f"{len(X_test)} test samples [{test_start} to {test_end}]",
    )

    return X_train, X_test, y_train, y_test


def validate_minimum_data(
    X: pd.DataFrame, min_total: int = 30, min_test: int = 10, logger: Optional[logging.Logger] = None
) -> None:
    """
    Validate that sufficient data exists for training.

    Args:
        X: Feature dataframe
        min_total: Minimum total samples required
        min_test: Minimum test samples required after split
        logger: Logger instance

    Raises:
        DataValidationError: If insufficient data
    """
    total_samples = len(X)

    if total_samples < min_total:
        msg = (
            f"Insufficient data for training: {total_samples} samples found, "
            f"but at least {min_total} samples are recommended for meaningful predictions. "
            f"Please provide more historical transaction data."
        )
        plog.log_error(logger, msg)
        raise DataValidationError(msg)

    # Check if test set will have enough samples
    test_size = config["model_evaluation"]["test_size"]
    expected_test_samples = int(total_samples * test_size)

    if expected_test_samples < min_test:
        msg = (
            f"Insufficient test data: with {total_samples} total samples and "
            f"test_size={test_size}, only {expected_test_samples} test samples "
            f"will be available. At least {min_test} are recommended. "
            f"Consider reducing test_size in config.yaml or adding more data."
        )
        plog.log_error(logger, msg)
        raise DataValidationError(msg)

    plog.log_info(logger, f"Data validation passed: {total_samples} total samples, ~{expected_test_samples} test samples")


def get_quarter_end_date(current_date: datetime) -> datetime:
    """
    Get the end date of the current quarter based on the provided date.

    Parameters:
    current_date (datetime): The current date to calculate the quarter end date.

    Returns:
    datetime: The end date of the current quarter.
    """
    quarter = (current_date.month - 1) // 3 + 1
    return datetime(current_date.year, 3 * quarter, 1) + DateOffset(months=1) - DateOffset(days=1)


def get_training_date_range(
    df: pd.DataFrame, date_column: str = "Date", logger: Optional[logging.Logger] = None
) -> pd.DatetimeIndex:
    """
    Get the complete date range for training data.

    Creates a complete date range from the earliest date in the data
    to yesterday (excluding today to avoid incomplete data).

    The function excludes today's data from the training range because:
    - Today's data is typically incomplete (day hasn't ended yet)
    - Training on incomplete data could introduce bias
    - Historical patterns are more reliable for training

    Parameters:
    df (pd.DataFrame): DataFrame containing the date column
    date_column (str): Name of the date column (default: 'Date')
    logger (logging.Logger, optional): Logger instance for logging messages

    Returns:
    pd.DatetimeIndex: Complete date range for training from earliest date to yesterday

    Raises:
    DataValidationError: If date range is invalid (NaT values found)

    Example:
    >>> df = pd.DataFrame({'Date': pd.date_range('2024-01-01', periods=10)})
    >>> date_range = get_training_date_range(df)
    >>> # Returns date range from 2024-01-01 to yesterday
    """
    # Calculate end date (yesterday at midnight)
    # Exclude today to avoid training on incomplete data
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Get start date from data
    start_date = df[date_column].min()

    # Validate dates
    if pd.isna(start_date) or pd.isna(end_date):
        plog.log_error(logger, "Invalid start or end date found in data")
        raise DataValidationError("Invalid start or end date found. Please check the data.")

    # Log the range
    plog.log_info(
        logger,
        f"Creating complete date range from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
    )

    return pd.date_range(start=start_date, end=end_date)


def _process_dataframe(
    df: pd.DataFrame, logger: Optional[logging.Logger] = None
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Process a DataFrame for training (internal helper function).

    This function performs the core data processing operations without
    reading or writing files, making it reusable and non-destructive.

    Parameters:
    df (pd.DataFrame): DataFrame with 'Date' and transaction amount columns.
    logger (logging.Logger, optional): Logger instance to record log messages. Defaults to None.

    Returns:
    tuple: A tuple containing X_train, y_train, and the processed DataFrame.
    """
    if not pd.to_numeric(df[TRANSACTION_AMOUNT_LABEL], errors="coerce").notnull().all():
        plog.log_error(logger, f"The '{TRANSACTION_AMOUNT_LABEL}' column contains non-numeric values")
        raise DataValidationError(
            f"The '{TRANSACTION_AMOUNT_LABEL}' column contains non-numeric values. Please check the data."
        )

    plog.log_info(logger, "Converting transaction amounts to numeric values")
    df[TRANSACTION_AMOUNT_LABEL] = pd.to_numeric(df[TRANSACTION_AMOUNT_LABEL])
    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.drop_duplicates(subset=["Date"], keep="last")
    plog.log_info(logger, f"Data cleaning completed. Rows after cleaning: {len(df)}")

    # Validate date range
    validate_date_range(df, logger=logger)

    # Use helper function to get complete date range for training
    complete_date_range = get_training_date_range(df, logger=logger)
    df = (df.set_index("Date")
            .reindex(complete_date_range)
            .fillna({TRANSACTION_AMOUNT_LABEL: 0})
            .reset_index()
            .rename(columns={"index": "Date"}))
    plog.log_info(logger, f"Date range filled. Total rows: {len(df)}")

    plog.log_info(logger, "Engineering features: day of week, month, day of month")
    df[DAY_OF_WEEK] = df["Date"].dt.day_name()
    df["Month"] = df["Date"].dt.month
    df["Day of the Month"] = df["Date"].dt.day

    df = pd.get_dummies(df, columns=[DAY_OF_WEEK], drop_first=True)
    plog.log_info(logger, f"Feature engineering completed. Total features: {len(df.columns) - 2}")

    x_train = df.drop(["Date", TRANSACTION_AMOUNT_LABEL], axis=1)
    y_train = df[TRANSACTION_AMOUNT_LABEL]

    return x_train, y_train, df


def preprocess_data(file_path: str, logger: Optional[logging.Logger] = None) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Preprocess input data from a CSV file.

    Parameters:
    file_path (str): The file path to the CSV file containing the input data.
    logger (logging.Logger, optional): Logger instance to record log messages. Defaults to None.

    Returns:
    tuple: A tuple containing X_train, y_train, and the processed DataFrame.
    """
    # Validate CSV file before reading
    validate_csv_file(file_path, logger=logger)

    df = pd.read_csv(file_path)
    return _process_dataframe(df, logger=logger)


def prepare_future_dates(future_date: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DatetimeIndex]:
    """
    Prepare future dates for prediction.

    Parameters:
    future_date (str, optional): The end date for future predictions in 'dd-mm-yyyy' format. Defaults to None.

    Returns:
    tuple: A tuple containing the DataFrame with future dates and the future date range.
    """
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if future_date is None:
        end_date = get_quarter_end_date(start_date)
    else:
        end_date = datetime.strptime(future_date, "%d-%m-%Y")
        if end_date <= start_date:
            raise DataValidationError("Future date must be in the future.")

    future_dates = pd.date_range(start=start_date, end=end_date)
    future_df = pd.DataFrame({"Date": future_dates})

    future_df[DAY_OF_WEEK] = future_df["Date"].dt.day_name().astype("category")
    future_df["Month"] = future_df["Date"].dt.month
    future_df["Day of the Month"] = future_df["Date"].dt.day
    future_df = pd.get_dummies(future_df, columns=[DAY_OF_WEEK], drop_first=True)

    return future_df, future_dates


def _read_and_process_excel_data(excel_path: str, logger: Optional[logging.Logger] = None) -> pd.DataFrame:
    """
    Read and process Excel file to extract daily transaction data.

    Parameters:
    excel_path (str): Path to the Excel file.
    logger (logging.Logger, optional): Logger instance to record log messages.

    Returns:
    pd.DataFrame: DataFrame with Date and transaction amount columns.

    Raises:
    DataValidationError: If required columns are missing or dependencies are not installed.
    """
    # Validate Excel file before reading
    validate_excel_file(excel_path, logger=logger)

    try:
        engine = "xlrd" if excel_path.endswith(".xls") else "openpyxl"
        sheet_names = pd.ExcelFile(excel_path, engine=engine).sheet_names
        plog.log_info(logger, f"Available sheets: {sheet_names}")

        skiprows = config["data_processing"]["skiprows"]
        excel_data = pd.read_excel(excel_path, sheet_name=sheet_names[0], engine=engine, skiprows=skiprows)
    except ImportError as e:
        # Missing openpyxl dependency for .xlsx files
        if "openpyxl" in str(e):
            plog.log_error(logger, f"Missing openpyxl dependency for .xlsx file processing: {e}")
            raise DataValidationError(
                "Processing .xlsx files requires openpyxl. Install it with: pip install openpyxl"
            ) from e
        # Other import errors
        plog.log_error(logger, f"Missing dependency for Excel file processing: {e}")
        raise DataValidationError(f"Missing required dependency for Excel processing: {e}") from e

    excel_data.columns = excel_data.columns.str.strip()
    plog.log_info(logger, f"Columns in the sheet: {excel_data.columns.tolist()}")

    # Find and validate required columns
    value_date_col = find_column_name(excel_data.columns, VALUE_DATE_LABEL)
    if value_date_col is None:
        plog.log_error(logger, f"{VALUE_DATE_LABEL} column not found. Available columns: {excel_data.columns.tolist()}")
        raise DataValidationError(
            f"{VALUE_DATE_LABEL} column not found in Excel file. Available columns: {excel_data.columns.tolist()}"
        )

    plog.log_info(logger, f"Using '{value_date_col}' as {VALUE_DATE_LABEL} column")
    excel_data[value_date_col] = pd.to_datetime(excel_data[value_date_col], dayfirst=True, errors="coerce")
    excel_data = excel_data.dropna(subset=[value_date_col])

    # Rename to standard VALUE_DATE_LABEL for consistency
    if value_date_col != VALUE_DATE_LABEL:
        excel_data = excel_data.rename(columns={value_date_col: VALUE_DATE_LABEL})

    # Find withdrawal and deposit columns
    withdrawal_col = find_column_name(excel_data.columns, "Withdrawal Amount (INR )")
    deposit_col = find_column_name(excel_data.columns, "Deposit Amount (INR )")

    if withdrawal_col is None or deposit_col is None:
        plog.log_error(
            logger,
            f"Required columns not found. Expected: 'Withdrawal Amount (INR )' and 'Deposit Amount (INR )'. "
            f"Found: {excel_data.columns.tolist()}",
        )
        raise DataValidationError(
            f"Required columns not found in Excel file. Available columns: {excel_data.columns.tolist()}"
        )

    plog.log_info(logger, f"Using columns: '{withdrawal_col}' for withdrawals and '{deposit_col}' for deposits")

    # Calculate net expense and aggregate by date
    excel_data["expense"] = excel_data[withdrawal_col].fillna(0) * -1 + excel_data[deposit_col].fillna(0)
    daily_expenses = excel_data.groupby(VALUE_DATE_LABEL)["expense"].sum().reset_index()
    daily_expenses.columns = ["Date", TRANSACTION_AMOUNT_LABEL]

    return daily_expenses


def preprocess_and_append_csv(
    file_path: str, excel_path: Optional[str] = None, logger: Optional[logging.Logger] = None
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Preprocess input data from a CSV file and optionally append data from an Excel file.

    This function reads data from the CSV file and optionally merges it with Excel data,
    then processes it for training.

    Parameters:
    file_path (str): The file path to the CSV file containing the input data.
    excel_path (str, optional): The file path to the Excel file for additional data. Defaults to None.
    logger (logging.Logger, optional): Logger instance to record log messages. Defaults to None.

    Returns:
    tuple: A tuple containing:
        - X_train (pd.DataFrame): Training features
        - y_train (pd.Series): Training labels
        - processed_df (pd.DataFrame): The fully processed DataFrame with features
        - raw_merged_df (pd.DataFrame or None): The raw merged data (only if excel_path provided)
    """
    # Validate CSV file before reading
    validate_csv_file(file_path, logger=logger)

    df = pd.read_csv(file_path)

    # Process and merge Excel data if provided
    if excel_path:
        daily_expenses = _read_and_process_excel_data(excel_path, logger=logger)
        df = pd.concat([df, daily_expenses], ignore_index=True)

    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    # Drop any NaT values created by failed datetime conversion
    df = df.dropna(subset=["Date"])
    df = df.drop_duplicates(subset=["Date"], keep="last")
    df = df.sort_values(by="Date").reset_index(drop=True)

    # Use helper function to get complete date range for training
    complete_date_range = get_training_date_range(df, logger=logger)
    df = (df.set_index("Date")
            .reindex(complete_date_range)
            .fillna({TRANSACTION_AMOUNT_LABEL: 0})
            .reset_index()
            .rename(columns={"index": "Date"}))

    # If Excel data was provided, save the merged data with complete date range for CSV update
    raw_merged_df = None
    if excel_path:
        # Use the df with complete date range (all dates filled with 0 for missing)
        raw_merged_df = df[["Date", TRANSACTION_AMOUNT_LABEL]].copy()
        plog.log_info(logger, f"Raw merged data contains {len(raw_merged_df)} records from {raw_merged_df['Date'].min().strftime('%Y-%m-%d')} to {raw_merged_df['Date'].max().strftime('%Y-%m-%d')}")

    # Process the dataframe and return with raw merged data
    x_train, y_train, processed_df = _process_dataframe(df, logger=logger)
    return x_train, y_train, processed_df, raw_merged_df


def write_predictions(
    predicted_df: pd.DataFrame, output_path: str, logger: Optional[logging.Logger] = None, skip_confirmation: bool = False
) -> None:
    """
    Write predictions to a CSV file with security measures.

    This function:
    - Formats dates in DD/MM/YYYY format
    - Sanitizes data to prevent CSV injection attacks
    - Optionally asks for user confirmation before overwriting

    Parameters:
    predicted_df (DataFrame): The DataFrame containing the predictions.
    output_path (str): The file path to save the predictions.
    logger (logging.Logger, optional): Logger instance used for logging.
    skip_confirmation (bool): If True, skip user confirmation for overwriting. Default: False.

    Returns:
    None

    Raises:
    IOError: If file writing fails
    """
    # Check if file exists and handle accordingly
    if os.path.exists(output_path) and not skip_confirmation:
        # Ask for confirmation
        if not confirm_overwrite(output_path, logger):
            plog.log_info(logger, f"Skipped writing to {output_path}")
            return

    # Create a copy for output formatting
    output_df = predicted_df.copy()

    # Format Date column if it exists and is datetime type
    if "Date" in output_df.columns and pd.api.types.is_datetime64_any_dtype(output_df["Date"]):
        output_df["Date"] = output_df["Date"].dt.strftime("%d/%m/%Y")

    # Sanitize data to prevent CSV injection
    plog.log_info(logger, "Sanitizing data to prevent CSV injection")
    sanitized_df = sanitize_dataframe_for_csv(output_df)

    # Write to CSV
    try:
        sanitized_df.to_csv(output_path, index=False)
        plog.log_info(logger, f"Predictions saved to {output_path}")
    except (IOError, OSError) as e:
        plog.log_error(logger, f"Failed to write predictions to {output_path}: {e}")
        raise IOError(f"Failed to write predictions: {e}")


def update_data_file(
    merged_df: pd.DataFrame, file_path: str, logger: Optional[logging.Logger] = None, skip_confirmation: bool = False
) -> None:
    """
    Update the data file with merged transaction data.

    This function:
    - Creates a backup of the existing file before overwriting
    - Formats dates in DD/MM/YYYY format
    - Sanitizes data to prevent CSV injection attacks
    - Optionally asks for user confirmation before overwriting

    Parameters:
    merged_df (pd.DataFrame): The merged DataFrame with Date and transaction amount columns.
    file_path (str): The file path to update.
    logger (logging.Logger, optional): Logger instance used for logging.
    skip_confirmation (bool): If True, skip user confirmation for overwriting. Default: False.

    Returns:
    None

    Raises:
    IOError: If backup creation or file writing fails
    """
    plog.log_info(logger, f"Updating data file: {file_path}")
    plog.log_info(logger, f"Merged data contains {len(merged_df)} records")

    # Create a copy for output formatting
    output_df = merged_df.copy()
    output_df["Date"] = output_df["Date"].dt.strftime("%d/%m/%Y")

    # Check if file exists and handle accordingly
    if os.path.exists(file_path) and not skip_confirmation:
        # Ask for confirmation
        if not confirm_overwrite(file_path, logger):
            plog.log_info(logger, f"Skipped updating {file_path}")
            return

    # Create backup before overwriting (keep only one previous version)
    if os.path.exists(file_path):
        try:
            # Define backup path (simple name without timestamp - keeps only one backup)
            file_path_obj = Path(file_path)
            backup_path = file_path_obj.with_suffix(f"{file_path_obj.suffix}.backup")

            # Remove old backup if it exists
            if backup_path.exists():
                backup_path.unlink()
                plog.log_info(logger, f"Removed old backup: {backup_path}")

            # Create new backup
            shutil.copy2(file_path, backup_path)
            plog.log_info(logger, f"Created backup: {backup_path}")
        except (IOError, OSError) as e:
            plog.log_error(logger, f"Failed to create backup, aborting update: {e}")
            raise IOError(f"Failed to create backup: {e}")

    # Sanitize data to prevent CSV injection
    plog.log_info(logger, "Sanitizing merged data to prevent CSV injection")
    sanitized_df = sanitize_dataframe_for_csv(output_df)

    # Write to CSV
    try:
        sanitized_df.to_csv(file_path, index=False)
        plog.log_info(logger, f"Successfully updated {file_path}")
        plog.log_info(logger, f"Date range: {merged_df['Date'].min()} to {merged_df['Date'].max()}")
    except (IOError, OSError) as e:
        plog.log_error(logger, f"Failed to update {file_path}: {e}")
        raise IOError(f"Failed to update data file: {e}")
