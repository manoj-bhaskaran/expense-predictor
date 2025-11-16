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

import argparse
import logging
import os
from datetime import datetime
from typing import List, Optional

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

import python_logging_framework as plog
from config import config
from helpers import (
    get_quarter_end_date,
    prepare_future_dates,
    preprocess_and_append_csv,
    validate_minimum_data,
    write_predictions,
)
from security import ALLOWED_CSV_EXTENSIONS, ALLOWED_EXCEL_EXTENSIONS, validate_directory_path, validate_file_path

# Load environment variables from .env file (if it exists)
load_dotenv()

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments for the expense predictor.

    Environment variables can be used to set default values. Command-line arguments
    take precedence over environment variables.

    Supported environment variables:
        - EXPENSE_PREDICTOR_FUTURE_DATE: Default future date for predictions
        - EXPENSE_PREDICTOR_EXCEL_DIR: Default Excel file directory
        - EXPENSE_PREDICTOR_EXCEL_FILE: Default Excel file name
        - EXPENSE_PREDICTOR_DATA_FILE: Default CSV data file path
        - EXPENSE_PREDICTOR_LOG_DIR: Default log directory
        - EXPENSE_PREDICTOR_OUTPUT_DIR: Default output directory
        - EXPENSE_PREDICTOR_SKIP_CONFIRMATION: Skip confirmation prompts (true/false)

    Args:
        args: Optional list of arguments to parse. If None, uses sys.argv.

    Returns:
        argparse.Namespace: Parsed arguments object.
    """
    parser = argparse.ArgumentParser(description="Expense Predictor")
    parser.add_argument(
        "--future_date",
        type=str,
        default=os.getenv("EXPENSE_PREDICTOR_FUTURE_DATE"),
        help="Future date for prediction (e.g., 31/12/2025)",
    )
    parser.add_argument(
        "--excel_dir",
        type=str,
        default=os.getenv("EXPENSE_PREDICTOR_EXCEL_DIR", "."),
        help="Directory where the Excel file is located",
    )
    parser.add_argument(
        "--excel_file",
        type=str,
        default=os.getenv("EXPENSE_PREDICTOR_EXCEL_FILE"),
        help="Name of the Excel file containing additional data",
    )
    parser.add_argument(
        "--data_file",
        type=str,
        default=os.getenv("EXPENSE_PREDICTOR_DATA_FILE", "trandata.csv"),
        help="Path to the CSV file containing transaction data",
    )
    parser.add_argument(
        "--log_dir",
        type=str,
        default=os.getenv("EXPENSE_PREDICTOR_LOG_DIR", "logs"),
        help="Directory where log files will be saved",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=os.getenv("EXPENSE_PREDICTOR_OUTPUT_DIR", "."),
        help="Directory where prediction files will be saved",
    )
    parser.add_argument(
        "--skip_confirmation",
        action="store_true",
        default=os.getenv("EXPENSE_PREDICTOR_SKIP_CONFIRMATION", "false").lower() == "true",
        help="Skip confirmation prompts for overwriting files (useful for automation)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO). Can also be set via EXPENSE_PREDICTOR_LOG_LEVEL environment variable or config.yaml",
    )
    return parser.parse_args(args)


def get_future_date(future_date_arg: Optional[str], logger: logging.Logger) -> str:
    """
    Get the future date for predictions.

    Args:
        future_date_arg: Date string in DD/MM/YYYY format or None.
        logger: Logger instance.

    Returns:
        str: Future date in DD-MM-YYYY format for predictions.
    """
    if future_date_arg:
        try:
            future_date_for_function = datetime.strptime(future_date_arg, "%d/%m/%Y").strftime("%d-%m-%Y")
        except ValueError:
            plog.log_error(logger, "Incorrect date format, should be DD/MM/YYYY")
            raise
    else:
        current_date = datetime.now()
        future_date_for_function = get_quarter_end_date(current_date).strftime("%d-%m-%Y")

    return future_date_for_function


def get_excel_path(excel_dir: str, excel_file: Optional[str], logger: logging.Logger) -> Optional[str]:
    """
    Validate and get Excel file path.

    Args:
        excel_dir: Directory containing Excel file.
        excel_file: Excel filename or None.
        logger: Logger instance.

    Returns:
        str: Validated Excel file path or None.
    """
    if not excel_file:
        return None

    try:
        excel_dir_path = validate_directory_path(excel_dir, must_exist=True, logger=logger)
        excel_file_str = os.path.join(str(excel_dir_path), excel_file)
        excel_file_path = validate_file_path(
            excel_file_str, allowed_extensions=ALLOWED_EXCEL_EXTENSIONS, must_exist=True, logger=logger
        )
        return str(excel_file_path)
    except (ValueError, FileNotFoundError) as e:
        plog.log_error(logger, f"Invalid Excel file path: {e}")
        raise


def get_data_file_path(data_file: str, logger: logging.Logger) -> str:
    """
    Validate and get data file path.

    Args:
        data_file: Path to CSV data file.
        logger: Logger instance.

    Returns:
        str: Validated data file path.
    """
    try:
        if os.path.isabs(data_file):
            data_file_str = data_file
        else:
            data_file_str = os.path.join(SCRIPT_DIR, data_file)

        data_file_path = validate_file_path(
            data_file_str, allowed_extensions=ALLOWED_CSV_EXTENSIONS, must_exist=True, logger=logger
        )
        return str(data_file_path)
    except (ValueError, FileNotFoundError) as e:
        plog.log_error(logger, f"Invalid data file path: {e}")
        raise


def get_log_level(args_log_level: Optional[str]) -> int:
    """
    Determine the log level based on priority order.

    Priority order (highest to lowest):
    1. Command-line argument (--log-level)
    2. Environment variable (EXPENSE_PREDICTOR_LOG_LEVEL)
    3. Configuration file (config.yaml logging.level)
    4. Default (INFO)

    Args:
        args_log_level: Log level from command-line arguments or None.

    Returns:
        int: Logging level constant (e.g., logging.INFO, logging.DEBUG).
    """
    # Priority 1: Command-line argument
    if args_log_level:
        log_level_str = args_log_level
    # Priority 2: Environment variable
    elif os.getenv("EXPENSE_PREDICTOR_LOG_LEVEL"):
        log_level_str = os.getenv("EXPENSE_PREDICTOR_LOG_LEVEL")
    # Priority 3: Configuration file
    elif "logging" in config and "level" in config["logging"]:
        log_level_str = config["logging"]["level"]
    # Priority 4: Default
    else:
        log_level_str = "INFO"

    # Convert string to logging constant with validation
    try:
        log_level = getattr(logging, log_level_str.upper())
        if not isinstance(log_level, int):
            raise AttributeError
    except AttributeError:
        # Invalid log level string, use default
        log_level = logging.INFO
        log_level_str = "INFO"

    return log_level


def train_and_evaluate_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    X: pd.DataFrame,
    y: pd.Series,
    future_date_for_function: str,
    output_dir: str,
    skip_confirmation: bool,
    logger: logging.Logger,
) -> None:
    """
    Train and evaluate all ML models, then generate predictions.

    Args:
        X_train: Training features.
        X_test: Test features.
        y_train: Training labels.
        y_test: Test labels.
        X: Full dataset features.
        y: Full dataset labels.
        future_date_for_function: Future date for predictions.
        output_dir: Directory to save predictions.
        skip_confirmation: Whether to skip file overwrite confirmations.
        logger: Logger instance.
    """
    TRANSACTION_AMOUNT_LABEL = "Tran Amt"

    # Dictionary of models to train and evaluate.
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(
            max_depth=config["decision_tree"]["max_depth"],
            min_samples_split=config["decision_tree"]["min_samples_split"],
            min_samples_leaf=config["decision_tree"]["min_samples_leaf"],
            ccp_alpha=config["decision_tree"]["ccp_alpha"],
            random_state=config["decision_tree"]["random_state"],
        ),
        "Random Forest": RandomForestRegressor(
            n_estimators=config["random_forest"]["n_estimators"],
            max_depth=config["random_forest"]["max_depth"],
            min_samples_split=config["random_forest"]["min_samples_split"],
            min_samples_leaf=config["random_forest"]["min_samples_leaf"],
            max_features=config["random_forest"]["max_features"],
            ccp_alpha=config["random_forest"]["ccp_alpha"],
            random_state=config["random_forest"]["random_state"],
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=config["gradient_boosting"]["n_estimators"],
            learning_rate=config["gradient_boosting"]["learning_rate"],
            max_depth=config["gradient_boosting"]["max_depth"],
            min_samples_split=config["gradient_boosting"]["min_samples_split"],
            min_samples_leaf=config["gradient_boosting"]["min_samples_leaf"],
            max_features=config["gradient_boosting"]["max_features"],
            random_state=config["gradient_boosting"]["random_state"],
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

        # Calculate and log metrics
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_r2 = r2_score(y_train, y_train_pred)

        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_r2 = r2_score(y_test, y_test_pred)

        plog.log_info(logger, "Training Set Performance:")
        plog.log_info(logger, f"  RMSE: {train_rmse:.2f}")
        plog.log_info(logger, f"  MAE: {train_mae:.2f}")
        plog.log_info(logger, f"  R-squared: {train_r2:.4f}")

        plog.log_info(logger, "Test Set Performance:")
        plog.log_info(logger, f"  RMSE: {test_rmse:.2f}")
        plog.log_info(logger, f"  MAE: {test_mae:.2f}")
        plog.log_info(logger, f"  R-squared: {test_r2:.4f}")

        # Retrain on full dataset and make predictions
        plog.log_info(logger, f"Retraining {model_name} on full dataset for production predictions")
        model.fit(X, y)

        future_df, future_dates = prepare_future_dates(future_date_for_function)
        future_df = future_df.reindex(columns=X_train.columns, fill_value=0)
        y_predict = model.predict(future_df)
        y_predict = np.round(y_predict, 2)

        # Save predictions
        predicted_df = pd.DataFrame({"Date": future_dates, f"Predicted {TRANSACTION_AMOUNT_LABEL}": y_predict})
        output_filename = f'future_predictions_{model_name.replace(" ", "_").lower()}.csv'
        output_path = os.path.join(output_dir, output_filename)
        write_predictions(predicted_df, output_path, logger=logger, skip_confirmation=skip_confirmation)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the expense predictor CLI.

    Args:
        args: Optional list of command-line arguments. If None, uses sys.argv.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    # Parse arguments
    parsed_args = parse_args(args)

    # Validate and create log directory with security checks
    try:
        log_dir_path_str = (
            os.path.join(SCRIPT_DIR, parsed_args.log_dir) if not os.path.isabs(parsed_args.log_dir) else parsed_args.log_dir
        )
        log_dir_path_obj = validate_directory_path(log_dir_path_str, create_if_missing=True)
        log_dir_path = str(log_dir_path_obj)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: Invalid log directory path: {e}")
        return 1

    # Determine log level based on priority order
    log_level = get_log_level(parsed_args.log_level)
    
    logger = plog.initialise_logger(script_name="model_runner.py", log_dir=log_dir_path, log_level=log_level)
    
    # Log the selected log level for transparency
    log_level_name = logging.getLevelName(log_level)
    plog.log_info(logger, f"Log level set to: {log_level_name}")

    # Get future date for predictions
    future_date_for_function = get_future_date(parsed_args.future_date, logger)

    # Get Excel file path (if provided)
    excel_path = get_excel_path(parsed_args.excel_dir, parsed_args.excel_file, logger)

    # Get and validate data file path
    file_path = get_data_file_path(parsed_args.data_file, logger)

    # Preprocess data
    X, y, _ = preprocess_and_append_csv(file_path, excel_path=excel_path, logger=logger)

    # Validate minimum data requirements
    min_total_samples = config["model_evaluation"].get("min_total_samples", 30)
    min_test_samples = config["model_evaluation"].get("min_test_samples", 10)
    validate_minimum_data(X, min_total=min_total_samples, min_test=min_test_samples, logger=logger)

    # Split data into training and test sets
    test_size = config["model_evaluation"]["test_size"]
    random_state = config["model_evaluation"]["random_state"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False, random_state=random_state)

    plog.log_info(logger, f"Data split: {len(X_train)} training samples, {len(X_test)} test samples")

    # Validate and create output directory
    try:
        if os.path.isabs(parsed_args.output_dir):
            output_dir_str = parsed_args.output_dir
        else:
            output_dir_str = os.path.join(SCRIPT_DIR, parsed_args.output_dir)

        output_dir_path = validate_directory_path(output_dir_str, create_if_missing=True, logger=logger)
        output_dir = str(output_dir_path)
    except (ValueError, FileNotFoundError) as e:
        plog.log_error(logger, f"Invalid output directory path: {e}")
        raise

    # Train and evaluate all models
    train_and_evaluate_models(
        X_train, X_test, y_train, y_test, X, y, future_date_for_function, output_dir, parsed_args.skip_confirmation, logger
    )

    return 0


if __name__ == "__main__":
    exit(main())
