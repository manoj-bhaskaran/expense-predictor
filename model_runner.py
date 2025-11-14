"""
Expense Predictor Script - model_runner.py

This script processes transaction data to train and evaluate multiple machine learning models. It predicts future transaction amounts for a specified future date. The predictions are saved as CSV files.

Usage:
    python model_runner.py [--future_date DD/MM/YYYY] [--excel_dir EXCEL_DIRECTORY] [--excel_file EXCEL_FILENAME] [--data_file DATA_FILE] [--log_dir LOG_DIRECTORY] [--output_dir OUTPUT_DIRECTORY]

Command-Line Arguments:
    --future_date : (Optional) The future date for which you want to predict transaction amounts. Format: DD/MM/YYYY
    --excel_dir   : (Optional) The directory where the Excel file is located. Default: current directory
    --excel_file  : (Optional) The name of the Excel file containing additional data.
    --data_file   : (Optional) The path to the CSV file containing transaction data. Default: trandata.csv
    --log_dir     : (Optional) The directory where log files will be saved. Default: logs/
    --output_dir  : (Optional) The directory where prediction files will be saved. Default: current directory

Example:
    python model_runner.py --future_date 31/12/2025 --excel_dir ./data --excel_file transactions.xls --data_file ./trandata.csv

If no future date is provided, the script will use the last day of the current quarter. If no Excel file name is provided, the script will not use an Excel file.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.model_selection import train_test_split
from helpers import preprocess_and_append_csv, prepare_future_dates, write_predictions, get_quarter_end_date
import argparse
from datetime import datetime
import os
import python_logging_framework as plog
import logging

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Expense Predictor')
parser.add_argument('--future_date', type=str, help='Future date for prediction (e.g., 31/12/2025)')
parser.add_argument('--excel_dir', type=str, default='.', help='Directory where the Excel file is located')
parser.add_argument('--excel_file', type=str, help='Name of the Excel file containing additional data')
parser.add_argument('--data_file', type=str, default='trandata.csv', help='Path to the CSV file containing transaction data')
parser.add_argument('--log_dir', type=str, default='logs', help='Directory where log files will be saved')
parser.add_argument('--output_dir', type=str, default='.', help='Directory where prediction files will be saved')
args = parser.parse_args()

# Create log directory if it doesn't exist
log_dir_path = os.path.join(SCRIPT_DIR, args.log_dir) if not os.path.isabs(args.log_dir) else args.log_dir
os.makedirs(log_dir_path, exist_ok=True)

logger = plog.initialise_logger(
    script_name='model_runner.py',
    log_dir=log_dir_path,
    log_level=logging.INFO
)

if args.future_date:
    try:
        future_date = datetime.strptime(args.future_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        future_date_for_function = datetime.strptime(args.future_date, '%d/%m/%Y').strftime('%d-%m-%Y')
    except ValueError:
        plog.log_error(logger, "Incorrect date format, should be DD/MM/YYYY")
        raise
else:
    current_date = datetime.now()
    future_date = get_quarter_end_date(current_date).strftime('%Y-%m-%d')
    future_date_for_function = get_quarter_end_date(current_date).strftime('%d-%m-%Y')

if args.excel_file:
    excel_path = os.path.join(args.excel_dir, args.excel_file)
else:
    excel_path = None

TRANSACTION_AMOUNT_LABEL = 'Tran Amt'

# Handle data file path - support both absolute and relative paths
if os.path.isabs(args.data_file):
    file_path = args.data_file
else:
    file_path = os.path.join(SCRIPT_DIR, args.data_file)

# Preprocesses the transaction CSV and optionally appends Excel data.
# Returns:
#   X: Features for model training
#   y: Target variable for model training
#   df: Full DataFrame after preprocessing
X, y, df = preprocess_and_append_csv(file_path, excel_path=excel_path, logger=logger)

# Split data into training and test sets (80/20 split)
# test_size=0.2 means 20% of data is used for testing
# shuffle=False preserves temporal order to avoid data leakage (train on past, test on future)
# random_state=42 ensures reproducible splits
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False, random_state=42)
plog.log_info(logger, f"Data split: {len(X_train)} training samples, {len(X_test)} test samples")

# Dictionary of models to train and evaluate.
# Each key is a model name, value is an instantiated regressor.
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        ccp_alpha=0.01,
        random_state=42
    ),
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        ccp_alpha=0.01,
        random_state=42
    ),
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        random_state=42
    ),
}

# Train, evaluate, and predict for each model
for model_name, model in models.items():
    plog.log_info(logger, f"--- {model_name} ---")

    # Fit the model on training data
    model.fit(X_train, y_train)

    # Predict on both training and test sets
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    # Calculate training set metrics
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_r2 = r2_score(y_train, y_train_pred)

    # Calculate test set metrics
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    # Log training metrics
    plog.log_info(logger, "Training Set Performance:")
    plog.log_info(logger, f"  RMSE: {train_rmse:.2f}")
    plog.log_info(logger, f"  MAE: {train_mae:.2f}")
    plog.log_info(logger, f"  R-squared: {train_r2:.4f}")

    # Log test set metrics (generalization performance)
    plog.log_info(logger, "Test Set Performance:")
    plog.log_info(logger, f"  RMSE: {test_rmse:.2f}")
    plog.log_info(logger, f"  MAE: {test_mae:.2f}")
    plog.log_info(logger, f"  R-squared: {test_r2:.4f}")

    # Prepare future dates/features for prediction
    # future_df: DataFrame of features for future dates
    # future_dates: List of future date strings
    future_df, future_dates = prepare_future_dates(future_date_for_function)
    future_df = future_df.reindex(columns=X_train.columns, fill_value=0)
    y_predict = model.predict(future_df)
    y_predict = np.round(y_predict, 2)

    # Create DataFrame with predictions and save to CSV
    predicted_df = pd.DataFrame({'Date': future_dates, f'Predicted {TRANSACTION_AMOUNT_LABEL}': y_predict})

    # Handle output directory - support both absolute and relative paths
    if os.path.isabs(args.output_dir):
        output_dir = args.output_dir
    else:
        output_dir = os.path.join(SCRIPT_DIR, args.output_dir)

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f'future_predictions_{model_name.replace(" ", "_").lower()}.csv'
    output_path = os.path.join(output_dir, output_filename)
    write_predictions(predicted_df, output_path, logger=logger)
