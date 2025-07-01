import pandas as pd
from pandas.tseries.offsets import DateOffset
from datetime import datetime, timedelta
import xlrd
import python_logging_framework as plog

# Define constants
TRANSACTION_AMOUNT_LABEL = 'Tran Amt'
DAY_OF_WEEK = 'Day of the Week'

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

def preprocess_data(file_path):
    """
    Preprocess input data from a CSV file.

    Parameters:
    file_path (str): The file path to the CSV file containing the input data.

    Returns:
    tuple: A tuple containing X_train, y_train, and the processed DataFrame.
    """
    df = pd.read_csv(file_path)

    if not pd.to_numeric(df[TRANSACTION_AMOUNT_LABEL], errors='coerce').notnull().all():
        raise ValueError(f"The '{TRANSACTION_AMOUNT_LABEL}' column contains non-numeric values. Please check the data.")

    df[TRANSACTION_AMOUNT_LABEL] = pd.to_numeric(df[TRANSACTION_AMOUNT_LABEL])
    df = df.dropna(subset=['Date'])
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df.drop_duplicates(subset=['Date'], keep='last')

    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    start_date = df['Date'].min()
    if pd.isna(start_date) or pd.isna(end_date):
        raise ValueError("Invalid start or end date found. Please check the data.")

    complete_date_range = pd.date_range(start=start_date, end=end_date)
    df = df.set_index('Date').reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()
    df.rename(columns={'index': 'Date'}, inplace=True)

    df[DAY_OF_WEEK] = df['Date'].dt.day_name()
    df['Month'] = df['Date'].dt.month
    df['Day of the Month'] = df['Date'].dt.day

    df = pd.get_dummies(df, columns=[DAY_OF_WEEK], drop_first=True)

    x_train = df.drop(['Date', TRANSACTION_AMOUNT_LABEL], axis=1)
    y_train = df[TRANSACTION_AMOUNT_LABEL]

    return x_train, y_train, df

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

    future_df[DAY_OF_WEEK] = future_df['Date'].dt.day_name()
    future_df['Month'] = future_df['Date'].dt.month
    future_df['Day of the Month'] = future_df['Date'].dt.day

    future_df[DAY_OF_WEEK] = future_df[DAY_OF_WEEK].astype('category')
    future_df = pd.get_dummies(future_df, columns=[DAY_OF_WEEK], drop_first=True)

    return future_df, future_dates

def preprocess_and_append_csv(file_path, excel_path=None, logger=None):
    """
    Preprocess input data from a CSV file and optionally append data from an Excel file.

    Parameters:
    file_path (str): The file path to the CSV file containing the input data.
    excel_path (str, optional): The file path to the Excel file for additional data. Defaults to None.
    logger (logging.Logger, optional): Logger instance to record log messages. Defaults to None.

    Returns:
    tuple: A tuple containing X_train, y_train, and the processed DataFrame.
    """
    df = pd.read_csv(file_path)

    if excel_path:
        engine = 'xlrd' if excel_path.endswith('.xls') else 'openpyxl'
        sheet_names = pd.ExcelFile(excel_path, engine=engine).sheet_names
        plog.log_info(logger, f"Available sheets: {sheet_names}")

        excel_data = pd.read_excel(excel_path, sheet_name=sheet_names[0], engine=engine, skiprows=12)
        excel_data.columns = excel_data.columns.str.strip()
        plog.log_info(logger, f"Columns in the sheet: {excel_data.columns.tolist()}")

        if 'Value Date' in excel_data.columns:
            excel_data['Value Date'] = pd.to_datetime(excel_data['Value Date'], dayfirst=True, errors='coerce')

        excel_data = excel_data.dropna(subset=['Value Date'])
        excel_data['expense'] = excel_data['Withdrawal Amount (INR )'].fillna(0) * -1 + excel_data['Deposit Amount (INR )'].fillna(0)
        daily_expenses = excel_data.groupby('Value Date')['expense'].sum().reset_index()
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
    df.to_csv(file_path, index=False)

    return preprocess_data(file_path)

def write_predictions(predicted_df, output_path, logger=None):
    """
    Write predictions to a CSV file.

    Parameters:
    predicted_df (DataFrame): The DataFrame containing the predictions.
    output_path (str): The file path to save the predictions.
    logger (logging.Logger, optional): Logger instance used for logging.

    Returns:
    None
    """
    predicted_df.to_csv(output_path, index=False)
    print(f"Predictions saved to {output_path}")
    plog.log_info(logger, f"Predictions saved to {output_path}")
