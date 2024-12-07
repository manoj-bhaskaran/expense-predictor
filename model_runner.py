"""
Expense Predictor Script - model_runner.py

This script processes transaction data to train and evaluate multiple machine learning models. It predicts future transaction amounts for a specified future date. The predictions are saved as CSV files.

Usage:
    python model_runner.py [--future_date DD/MM/YYYY] [--excel_dir EXCEL_DIRECTORY] [--excel_file EXCEL_FILENAME]

Command-Line Arguments:
    --future_date : (Optional) The future date for which you want to predict transaction amounts. Format: DD/MM/YYYY
    --excel_dir   : (Optional) The directory where the Excel file is located. Default: C:\Users\manoj\Downloads
    --excel_file  : (Optional) The name of the Excel file containing additional data.

Example:
    python model_runner.py --future_date 31/12/2025 --excel_dir C:\Data --excel_file transactions.xls

If no future date is provided, the script will use the last day of the current quarter. If no Excel file name is provided, the script will not use an Excel file.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from helpers import preprocess_and_append_csv, prepare_future_dates, write_predictions, get_quarter_end_date
import argparse
from datetime import datetime
import os

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Expense Predictor')
parser.add_argument('--future_date', type=str, help='Future date for prediction (e.g., 31/12/2025)')
parser.add_argument('--excel_dir', type=str, default=r'C:\\Users\\manoj\\Downloads', help='Directory where the Excel file is located')
parser.add_argument('--excel_file', type=str, help='Name of the Excel file containing additional data')
args = parser.parse_args()

# Use the command-line argument for future_date and convert format if needed
if args.future_date:
    try:
        future_date = datetime.strptime(args.future_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        future_date_for_function = datetime.strptime(args.future_date, '%d/%m/%Y').strftime('%d-%m-%Y')
    except ValueError:
        raise ValueError("Incorrect date format, should be DD/MM/YYYY")
else:
    current_date = datetime.now()
    future_date = get_quarter_end_date(current_date).strftime('%Y-%m-%d')
    future_date_for_function = get_quarter_end_date(current_date).strftime('%d-%m-%Y')

# Construct the Excel file path if excel_file is provided
if args.excel_file:
    excel_path = os.path.join(args.excel_dir, args.excel_file)
elif args.excel_dir and not args.excel_file:
    raise ValueError("Excel directory provided without an Excel file name.")
else:
    excel_path = None

# Define constants
TRANSACTION_AMOUNT_LABEL = 'Tran Amt'

# Define file path for input data
file_path = r'D:\\Python\\Projects\\Expense Predictor\\trandata.csv'  # Use raw string literal

# Preprocess input data
X_train, y_train, df = preprocess_and_append_csv(file_path, excel_path=excel_path)  # Optional Excel path

# Define a dictionary to hold model details
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        ccp_alpha=0.01,  # Added ccp_alpha parameter
        random_state=42
    ),
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",  # Changed max_features from "auto" to "sqrt"
        ccp_alpha=0.01,  # Added ccp_alpha parameter
        random_state=42
    ),
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",  # Add max_features parameter
        random_state=42
    ),
}

# Loop through models and evaluate
for model_name, model in models.items():
    """
    Train and evaluate each model, and make future predictions.

    Parameters:
    model_name (str): The name of the machine learning model.
    model (object): The machine learning model instance.
    """
    print(f"\n--- {model_name} ---")

    # Train the model
    model.fit(X_train, y_train)

    # Model performance on training data
    y_train_predictor = model.predict(X_train)

    # Use mean_squared_error to calculate RMSE
    rmse = np.sqrt(mean_squared_error(y_train, y_train_predictor))
    mae = mean_absolute_error(y_train, y_train_predictor)
    r2 = r2_score(y_train, y_train_predictor)

    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"R-squared: {r2}")

    # Prepare future dates for prediction
    future_df, future_dates = prepare_future_dates(future_date_for_function)

    # Match columns with training data
    future_df = future_df.reindex(columns=X_train.columns, fill_value=0)

    # Make predictions for future dates
    y_predict = model.predict(future_df)

    # Round the predicted transaction amounts to two decimal places
    y_predict = np.round(y_predict, 2)

    # Create a new DataFrame to store predictions with the original dates
    predicted_df = pd.DataFrame({'Date': future_dates, f'Predicted {TRANSACTION_AMOUNT_LABEL}': y_predict})

    # Save predictions to a CSV file
    output_path = rf'D:\\Python\\Projects\\Expense Predictor\\future_predictions_{model_name.replace(" ", "_").lower()}.csv'
    write_predictions(predicted_df, output_path)
