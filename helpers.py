from datetime import datetime, timedelta
import pandas as pd

# Define constants
TRANSACTION_AMOUNT_LABEL = 'Tran Amt'
# Define a constant for 'Day of the Week'
DAY_OF_WEEK = 'Day of the Week'

# Function to get the end date of the current quarter
def get_quarter_end_date(current_date):
    quarter = (current_date.month - 1) // 3 + 1
    return datetime(current_date.year, 3 * quarter, 1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)

# Function to preprocess input data
def preprocess_data(file_path):
    df = pd.read_csv(file_path)

    # Check if TRANSACTION_AMOUNT_LABEL column is numeric
    if not pd.to_numeric(df[TRANSACTION_AMOUNT_LABEL], errors='coerce').notnull().all():
        raise ValueError(f"The '{TRANSACTION_AMOUNT_LABEL}' column contains non-numeric values. Please check the data.")

    # Convert TRANSACTION_AMOUNT_LABEL column to numeric type
    df[TRANSACTION_AMOUNT_LABEL] = pd.to_numeric(df[TRANSACTION_AMOUNT_LABEL])

    # Convert 'Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')

    # Set end date to the previous day of the execution date
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)  # Ensure end_date is set to the beginning of the day

    # Create a complete date range from the minimum date to the end date (previous day)
    complete_date_range = pd.date_range(start=df['Date'].min(), end=end_date)

    # Reindex the dataframe to include all dates and fill missing TRANSACTION_AMOUNT_LABEL with 0
    df = df.set_index('Date').reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()
    df.rename(columns={'index': 'Date'}, inplace=True)

    # Derive 'Day of the Week' from the 'Date' column
    df[DAY_OF_WEEK] = df['Date'].dt.day_name()

    # Add 'Month' and 'Day of the Month' columns
    df['Month'] = df['Date'].dt.month
    df['Day of the Month'] = df['Date'].dt.day

    # Create dummy variables for 'Day of the Week' in the existing data
    df = pd.get_dummies(df, columns=[DAY_OF_WEEK], drop_first=True)

    # Prepare x_train and y_train using the historical data
    x_train = df.drop(['Date', TRANSACTION_AMOUNT_LABEL], axis=1)
    y_train = df[TRANSACTION_AMOUNT_LABEL]

    return x_train, y_train, df

# Function to prepare future dates
def prepare_future_dates():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Set start_date to the beginning of today
    end_of_quarter = get_quarter_end_date(start_date)

    # Create a date range for future predictions
    future_dates = pd.date_range(start=start_date, end=end_of_quarter)

    # Create a DataFrame for future dates
    future_df = pd.DataFrame({'Date': future_dates})

    # Add 'Day of the Week', 'Month', and 'Day of the Month' columns
    future_df[DAY_OF_WEEK] = future_df['Date'].dt.day_name()
    future_df['Month'] = future_df['Date'].dt.month
    future_df['Day of the Month'] = future_df['Date'].dt.day

    # Convert 'Day of the Week' to categorical for consistency with training data
    future_df[DAY_OF_WEEK] = future_df[DAY_OF_WEEK].astype('category')

    # Create dummy variables for 'Day of the Week' in the future data
    future_df = pd.get_dummies(future_df, columns=[DAY_OF_WEEK], drop_first=True)

    return future_df, future_dates

# Function to write predictions to CSV
def write_predictions(predicted_df, output_path):
    # Save the future predictions to a CSV file
    predicted_df.to_csv(output_path, index=False)
    print(f"Predictions saved to {output_path}")