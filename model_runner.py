"""
Expense Predictor Script - model_runner.py

This script processes transaction data to train and evaluate multiple machine learning models. It predicts future transaction amounts for a specified future date. The predictions are saved as CSV files.

Usage:
    python model_runner.py [--future_date DD/MM/YYYY] [--excel_dir EXCEL_DIRECTORY] [--excel_file EXCEL_FILENAME] [--data_file DATA_FILE] [--log_dir LOG_DIRECTORY] [--output_dir OUTPUT_DIRECTORY] [--skip_confirmation]

Command-Line Arguments:
    --future_date        : (Optional) The future date for which you want to predict transaction amounts. Format: DD/MM/YYYY
    --excel_dir          : (Optional) The directory where the Excel file is located. Default: current directory
    --excel_file         : (Optional) The name of the Excel file containing additional data.
    --data_file          : (Optional) The path to the CSV file containing transaction data. Default: trandata.csv
    --log_dir            : (Optional) The directory where log files will be saved. Default: logs/
    --output_dir         : (Optional) The directory where prediction files will be saved. Default: current directory
    --skip_confirmation  : (Optional) Skip confirmation prompts for overwriting files. Useful for automated workflows.

Example:
    python model_runner.py --future_date 31/12/2025 --excel_dir ./data --excel_file transactions.xls --data_file ./trandata.csv

Example (automated mode, no prompts):
    python model_runner.py --future_date 31/12/2025 --data_file ./trandata.csv --skip_confirmation

Security Features:
    - Path validation to prevent path traversal attacks
    - File extension validation for CSV and Excel files
    - CSV injection prevention in output files
    - Automatic backups before overwriting existing files
    - User confirmation prompts for file overwrites (unless --skip_confirmation is used)

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
from config import config
from security import (
    validate_file_path,
    validate_directory_path,
    ALLOWED_CSV_EXTENSIONS,
    ALLOWED_EXCEL_EXTENSIONS
)

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
parser.add_argument('--skip_confirmation', action='store_true', help='Skip confirmation prompts for overwriting files (useful for automation)')
args = parser.parse_args()

# Validate and create log directory with security checks
try:
    log_dir_path_str = os.path.join(SCRIPT_DIR, args.log_dir) if not os.path.isabs(args.log_dir) else args.log_dir
    log_dir_path_obj = validate_directory_path(log_dir_path_str, create_if_missing=True)
    log_dir_path = str(log_dir_path_obj)
except (ValueError, FileNotFoundError) as e:
    print(f"Error: Invalid log directory path: {e}")
    exit(1)

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
    # Validate excel_dir and excel_file with security checks
    try:
        excel_dir_path = validate_directory_path(args.excel_dir, must_exist=True, logger=logger)
        excel_file_str = os.path.join(str(excel_dir_path), args.excel_file)
        excel_file_path = validate_file_path(
            excel_file_str,
            allowed_extensions=ALLOWED_EXCEL_EXTENSIONS,
            must_exist=True,
            logger=logger
        )
        excel_path = str(excel_file_path)
    except (ValueError, FileNotFoundError) as e:
        plog.log_error(logger, f"Invalid Excel file path: {e}")
        raise
else:
    excel_path = None

TRANSACTION_AMOUNT_LABEL = 'Tran Amt'

# Validate data file path with security checks
try:
    if os.path.isabs(args.data_file):
        data_file_str = args.data_file
    else:
        data_file_str = os.path.join(SCRIPT_DIR, args.data_file)

    data_file_path = validate_file_path(
        data_file_str,
        allowed_extensions=ALLOWED_CSV_EXTENSIONS,
        must_exist=True,
        logger=logger
    )
    file_path = str(data_file_path)
except (ValueError, FileNotFoundError) as e:
    plog.log_error(logger, f"Invalid data file path: {e}")
    raise

# Preprocesses the transaction CSV and optionally appends Excel data.
# Returns:
#   X: Features for model training
#   y: Target variable for model training
#   df: Full DataFrame after preprocessing
X, y, df = preprocess_and_append_csv(file_path, excel_path=excel_path, logger=logger)

# Split data into training and test sets (configurable split ratio)
# test_size from config (default: 0.2 means 20% of data is used for testing)
# shuffle=False preserves temporal order to avoid data leakage (train on past, test on future)
# random_state from config ensures reproducible splits
test_size = config['model_evaluation']['test_size']
random_state = config['model_evaluation']['random_state']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False, random_state=random_state)

plog.log_info(logger, f"Data split: {len(X_train)} training samples, {len(X_test)} test samples")

# Dictionary of models to train and evaluate.
# Each key is a model name, value is an instantiated regressor.
# Hyperparameters are loaded from config.yaml for easy tuning.
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(
        max_depth=config['decision_tree']['max_depth'],
        min_samples_split=config['decision_tree']['min_samples_split'],
        min_samples_leaf=config['decision_tree']['min_samples_leaf'],
        ccp_alpha=config['decision_tree']['ccp_alpha'],
        random_state=config['decision_tree']['random_state']
    ),
    "Random Forest": RandomForestRegressor(
        n_estimators=config['random_forest']['n_estimators'],
        max_depth=config['random_forest']['max_depth'],
        min_samples_split=config['random_forest']['min_samples_split'],
        min_samples_leaf=config['random_forest']['min_samples_leaf'],
        max_features=config['random_forest']['max_features'],
        ccp_alpha=config['random_forest']['ccp_alpha'],
        random_state=config['random_forest']['random_state']
    ),
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=config['gradient_boosting']['n_estimators'],
        learning_rate=config['gradient_boosting']['learning_rate'],
        max_depth=config['gradient_boosting']['max_depth'],
        min_samples_split=config['gradient_boosting']['min_samples_split'],
        min_samples_leaf=config['gradient_boosting']['min_samples_leaf'],
        max_features=config['gradient_boosting']['max_features'],
        random_state=config['gradient_boosting']['random_state']
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

    # Retrain on full dataset for production predictions
    plog.log_info(logger, f"Retraining {model_name} on full dataset for production predictions")
    model.fit(X, y)
    # Prepare future dates/features for prediction
    # future_df: DataFrame of features for future dates
    # future_dates: List of future date strings
    future_df, future_dates = prepare_future_dates(future_date_for_function)
    future_df = future_df.reindex(columns=X_train.columns, fill_value=0)
    y_predict = model.predict(future_df)
    y_predict = np.round(y_predict, 2)

    # Create DataFrame with predictions and save to CSV
    predicted_df = pd.DataFrame({'Date': future_dates, f'Predicted {TRANSACTION_AMOUNT_LABEL}': y_predict})

    # Validate and create output directory with security checks
    try:
        if os.path.isabs(args.output_dir):
            output_dir_str = args.output_dir
        else:
            output_dir_str = os.path.join(SCRIPT_DIR, args.output_dir)

        output_dir_path = validate_directory_path(
            output_dir_str,
            create_if_missing=True,
            logger=logger
        )
        output_dir = str(output_dir_path)
    except (ValueError, FileNotFoundError) as e:
        plog.log_error(logger, f"Invalid output directory path: {e}")
        raise
    output_filename = f'future_predictions_{model_name.replace(" ", "_").lower()}.csv'
    output_path = os.path.join(output_dir, output_filename)
    write_predictions(predicted_df, output_path, logger=logger, skip_confirmation=args.skip_confirmation)
