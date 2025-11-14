import pandas as pd
from pandas.tseries.offsets import DateOffset
from datetime import datetime, timedelta
import xlrd
import python_logging_framework as plog
from config import config
import os
from security import sanitize_dataframe_for_csv, create_backup, confirm_overwrite

# Define constants
TRANSACTION_AMOUNT_LABEL = 'Tran Amt'
DAY_OF_WEEK = 'Day of the Week'
VALUE_DATE_LABEL = 'Value Date'

def validate_csv_file(file_path, logger=None):
    """
    Validate that CSV file exists and has required columns.

    Parameters:
    file_path (str): Path to the CSV file
    logger (logging.Logger, optional): Logger instance for logging messages

    Raises:
    FileNotFoundError: If the CSV file does not exist
    ValueError: If required columns are missing
    """
    # Check if file exists
    if not os.path.exists(file_path):
        plog.log_error(logger, f"CSV file not found: {file_path}")
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        plog.log_error(logger, f"Path is not a file: {file_path}")
        raise ValueError(f"Path is not a file: {file_path}")

    # Try to read the CSV and check for required columns
    try:
        df = pd.read_csv(file_path, nrows=0)  # Read only headers
        columns = df.columns.tolist()

        # Check for required columns
        required_columns = ['Date', TRANSACTION_AMOUNT_LABEL]
        missing_columns = [col for col in required_columns if col not in columns]

        if missing_columns:
            plog.log_error(logger, f"Missing required columns in CSV: {missing_columns}. Found columns: {columns}")
            raise ValueError(f"Missing required columns in CSV file: {missing_columns}. Found columns: {columns}")

        plog.log_info(logger, f"CSV file validation passed: {file_path}")
    except pd.errors.EmptyDataError:
        plog.log_error(logger, f"CSV file is empty: {file_path}")
        raise ValueError(f"CSV file is empty: {file_path}")
    except pd.errors.ParserError as e:
        plog.log_error(logger, f"CSV file parsing error: {e}")
        raise ValueError(f"CSV file is not properly formatted: {e}")

def validate_excel_file(file_path, logger=None):
    """
    Validate that Excel file exists and has a valid format.

    WARNING: Excel files from untrusted sources may contain malicious formulas or macros.
    Only process Excel files from trusted sources. This function does not validate
    or sanitize Excel cell contents for potential security threats.

    Parameters:
    file_path (str): Path to the Excel file
    logger (logging.Logger, optional): Logger instance for logging messages

    Raises:
    FileNotFoundError: If the Excel file does not exist
    ValueError: If the file is not a valid Excel format
    """
    # Security warning
    plog.log_info(logger, f"WARNING: Processing Excel file from: {file_path}")
    plog.log_info(logger, "Ensure this file is from a trusted source. Excel files may contain formulas or macros.")

    # Check if file exists
    if not os.path.exists(file_path):
        plog.log_error(logger, f"Excel file not found: {file_path}")
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        plog.log_error(logger, f"Path is not a file: {file_path}")
        raise ValueError(f"Path is not a file: {file_path}")

    # Check file extension
    valid_extensions = ['.xls', '.xlsx']
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension not in valid_extensions:
        plog.log_error(logger, f"Invalid Excel file format: {file_extension}. Expected: {valid_extensions}")
        raise ValueError(f"Invalid Excel file format: {file_extension}. Expected one of: {valid_extensions}")

    # Try to open the Excel file to ensure it's valid
    try:
        engine = 'xlrd' if file_path.endswith('.xls') else 'openpyxl'
        pd.ExcelFile(file_path, engine=engine)
        plog.log_info(logger, f"Excel file validation passed: {file_path}")
    except Exception as e:
        plog.log_error(logger, f"Excel file is corrupted or invalid: {e}")
        raise ValueError(f"Excel file is corrupted or cannot be read: {e}")

def validate_date_range(df, logger=None):
    """
    Validate date range in the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame with 'Date' column
    logger (logging.Logger, optional): Logger instance for logging messages

    Raises:
    ValueError: If date range is invalid
    """
    if 'Date' not in df.columns:
        plog.log_error(logger, "Date column not found in DataFrame")
        raise ValueError("Date column not found in DataFrame")

    # Check if there are any valid dates
    if df['Date'].isna().all():
        plog.log_error(logger, "No valid dates found in the data")
        raise ValueError("No valid dates found in the data")

    start_date = df['Date'].min()
    end_date = df['Date'].max()

    # Check for NaT (Not a Time) values
    if pd.isna(start_date) or pd.isna(end_date):
        plog.log_error(logger, "Invalid dates found in the data (NaT values)")
        raise ValueError("Invalid dates found in the data. Please ensure all dates are properly formatted.")

    # Check if dates are in the future (beyond today)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if start_date > today:
        plog.log_error(logger, f"Data contains only future dates. Start date: {start_date}, Today: {today}")
        raise ValueError(f"Data contains only future dates. Start date: {start_date.strftime('%Y-%m-%d')}")

    # Log date range info
    plog.log_info(logger, f"Date range validation passed. Start: {start_date.strftime('%Y-%m-%d')}, End: {end_date.strftime('%Y-%m-%d')}")

def find_column_name(df_columns, expected_name):
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
    normalized_expected = expected_name.replace(' (', '(').replace(' )', ')')
    
    # Try normalized version
    if normalized_expected in df_columns:
        return normalized_expected
    
    # Try with spaces around parentheses
    spaced_expected = expected_name.replace('(', ' (').replace(')', ' )')
    if spaced_expected in df_columns:
        return spaced_expected
    
    # If still not found, try fuzzy matching by checking if the base name matches
    base_name = expected_name.split('(')[0].strip()
    for col in df_columns:
        if col.startswith(base_name) and '(' in col:
            return col
    
    return None

def get_quarter_end_date(current_date):
    """
    Get the end date of the current quarter based on the provided date.

    Parameters:
    current_date (datetime): The current date to calculate the quarter end date.

    Returns:
    datetime: The end date of the current quarter.
    """
    quarter = (current_date.month - 1) // 3 + 1
    return datetime(current_date.year, 3 * quarter, 1) + DateOffset(months=1) - DateOffset(days=1)

def _process_dataframe(df, logger=None):
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
    if not pd.to_numeric(df[TRANSACTION_AMOUNT_LABEL], errors='coerce').notnull().all():
        plog.log_error(logger, f"The '{TRANSACTION_AMOUNT_LABEL}' column contains non-numeric values")
        raise ValueError(f"The '{TRANSACTION_AMOUNT_LABEL}' column contains non-numeric values. Please check the data.")

    plog.log_info(logger, "Converting transaction amounts to numeric values")
    df[TRANSACTION_AMOUNT_LABEL] = pd.to_numeric(df[TRANSACTION_AMOUNT_LABEL])
    df = df.dropna(subset=['Date'])
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df.drop_duplicates(subset=['Date'], keep='last')
    plog.log_info(logger, f"Data cleaning completed. Rows after cleaning: {len(df)}")

    # Validate date range
    validate_date_range(df, logger=logger)

    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    start_date = df['Date'].min()
    if pd.isna(start_date) or pd.isna(end_date):
        plog.log_error(logger, "Invalid start or end date found in data")
        raise ValueError("Invalid start or end date found. Please check the data.")

    plog.log_info(logger, f"Creating complete date range from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    complete_date_range = pd.date_range(start=start_date, end=end_date)
    df = df.set_index('Date').reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()
    df.rename(columns={'index': 'Date'}, inplace=True)
    plog.log_info(logger, f"Date range filled. Total rows: {len(df)}")

    plog.log_info(logger, "Engineering features: day of week, month, day of month")
    df[DAY_OF_WEEK] = df['Date'].dt.day_name()
    df['Month'] = df['Date'].dt.month
    df['Day of the Month'] = df['Date'].dt.day

    df = pd.get_dummies(df, columns=[DAY_OF_WEEK], drop_first=True)
    plog.log_info(logger, f"Feature engineering completed. Total features: {len(df.columns) - 2}")

    x_train = df.drop(['Date', TRANSACTION_AMOUNT_LABEL], axis=1)
    y_train = df[TRANSACTION_AMOUNT_LABEL]

    return x_train, y_train, df

def preprocess_data(file_path, logger=None):
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

def prepare_future_dates(future_date=None):
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
            raise ValueError("Future date must be in the future.")
        
    future_dates = pd.date_range(start=start_date, end=end_date)
    future_df = pd.DataFrame({'Date': future_dates})

    future_df[DAY_OF_WEEK] = future_df['Date'].dt.day_name().astype('category')
    future_df['Month'] = future_df['Date'].dt.month
    future_df['Day of the Month'] = future_df['Date'].dt.day
    future_df = pd.get_dummies(future_df, columns=[DAY_OF_WEEK], drop_first=True)

    return future_df, future_dates

def preprocess_and_append_csv(file_path, excel_path=None, logger=None):
    """
    Preprocess input data from a CSV file and optionally append data from an Excel file.

    This function reads data from the CSV file and optionally merges it with Excel data,
    then processes it for training. The original CSV file is NOT modified.

    Parameters:
    file_path (str): The file path to the CSV file containing the input data.
    excel_path (str, optional): The file path to the Excel file for additional data. Defaults to None.
    logger (logging.Logger, optional): Logger instance to record log messages. Defaults to None.

    Returns:
    tuple: A tuple containing X_train, y_train, and the processed DataFrame.
    """
    # Validate CSV file before reading
    validate_csv_file(file_path, logger=logger)

    df = pd.read_csv(file_path)

    if excel_path:
        # Validate Excel file before reading
        validate_excel_file(excel_path, logger=logger)
        engine = 'xlrd' if excel_path.endswith('.xls') else 'openpyxl'
        sheet_names = pd.ExcelFile(excel_path, engine=engine).sheet_names
        plog.log_info(logger, f"Available sheets: {sheet_names}")

        skiprows = config['data_processing']['skiprows']
        excel_data = pd.read_excel(excel_path, sheet_name=sheet_names[0], engine=engine, skiprows=skiprows)
        excel_data.columns = excel_data.columns.str.strip()
        plog.log_info(logger, f"Columns in the sheet: {excel_data.columns.tolist()}")

        value_date_col = find_column_name(excel_data.columns, VALUE_DATE_LABEL)
        if value_date_col is None:
            plog.log_error(logger, f"{VALUE_DATE_LABEL} column not found. Available columns: {excel_data.columns.tolist()}")
            raise KeyError(f"{VALUE_DATE_LABEL} column not found in Excel file. Available columns: {excel_data.columns.tolist()}")

        plog.log_info(logger, f"Using '{value_date_col}' as {VALUE_DATE_LABEL} column")
        excel_data[value_date_col] = pd.to_datetime(excel_data[value_date_col], dayfirst=True, errors='coerce')

        excel_data = excel_data.dropna(subset=[value_date_col])
        # Rename to standard VALUE_DATE_LABEL for consistency in downstream processing
        if value_date_col != VALUE_DATE_LABEL:
            excel_data = excel_data.rename(columns={value_date_col: VALUE_DATE_LABEL})

        # Find the actual column names with flexible matching
        withdrawal_col = find_column_name(excel_data.columns, 'Withdrawal Amount (INR )')
        deposit_col = find_column_name(excel_data.columns, 'Deposit Amount (INR )')

        if withdrawal_col is None or deposit_col is None:
            plog.log_error(logger, f"Required columns not found. Expected: 'Withdrawal Amount (INR )' and 'Deposit Amount (INR )'. Found: {excel_data.columns.tolist()}")
            raise KeyError(f"Required columns not found in Excel file. Available columns: {excel_data.columns.tolist()}")

        plog.log_info(logger, f"Using columns: '{withdrawal_col}' for withdrawals and '{deposit_col}' for deposits")
        excel_data['expense'] = excel_data[withdrawal_col].fillna(0) * -1 + excel_data[deposit_col].fillna(0)
        daily_expenses = excel_data.groupby(VALUE_DATE_LABEL)['expense'].sum().reset_index()
        daily_expenses.columns = ['Date', 'expense']
        daily_expenses.rename(columns={'expense': TRANSACTION_AMOUNT_LABEL}, inplace=True)
        df = pd.concat([df, daily_expenses], ignore_index=True)

    df = df.dropna(subset=['Date'])
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.drop_duplicates(subset=['Date'], keep='last')
    df = df.sort_values(by='Date').reset_index(drop=True)

    start_date = df['Date'].min()
    end_date = datetime.now() - timedelta(days=1)
    complete_date_range = pd.date_range(start=start_date, end=end_date)
    df = df.set_index('Date').reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()
    df.rename(columns={'index': 'Date'}, inplace=True)

    # Process the dataframe directly without modifying the input file
    return _process_dataframe(df, logger=logger)

def write_predictions(predicted_df, output_path, logger=None, skip_confirmation=False):
    """
    Write predictions to a CSV file with security measures.

    This function:
    - Sanitizes data to prevent CSV injection attacks
    - Creates a backup if the file already exists
    - Optionally asks for user confirmation before overwriting

    Parameters:
    predicted_df (DataFrame): The DataFrame containing the predictions.
    output_path (str): The file path to save the predictions.
    logger (logging.Logger, optional): Logger instance used for logging.
    skip_confirmation (bool): If True, skip user confirmation for overwriting. Default: False.

    Returns:
    None

    Raises:
    IOError: If backup creation or file writing fails
    """
    # Check if file exists and handle accordingly
    if os.path.exists(output_path) and not skip_confirmation:
        # Ask for confirmation
        if not confirm_overwrite(output_path, logger):
            plog.log_info(logger, f"Skipped writing to {output_path}")
            return

        # Create backup before overwriting
        try:
            backup_path = create_backup(output_path, logger)
            if backup_path:
                plog.log_info(logger, f"Created backup: {backup_path}")
        except IOError as e:
            plog.log_error(logger, f"Failed to create backup, aborting write: {e}")
            raise

    # Sanitize data to prevent CSV injection
    plog.log_info(logger, "Sanitizing data to prevent CSV injection")
    sanitized_df = sanitize_dataframe_for_csv(predicted_df)

    # Write to CSV
    try:
        sanitized_df.to_csv(output_path, index=False)
        plog.log_info(logger, f"Predictions saved to {output_path}")
    except (IOError, OSError) as e:
        plog.log_error(logger, f"Failed to write predictions to {output_path}: {e}")
        raise IOError(f"Failed to write predictions: {e}")
