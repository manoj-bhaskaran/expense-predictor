"""
Expense Predictor Script - model_runner.py

This script processes transaction data to train and evaluate multiple machine learning models. It predicts future transaction amounts for a specified future date. The predictions are saved as CSV files.

Usage:
    python model_runner.py [--future_date DD/MM/YYYY] [--excel_dir EXCEL_DIRECTORY] [--excel_file EXCEL_FILENAME] [--data_file DATA_FILE] [--log_dir LOG_DIRECTORY] [--output_dir OUTPUT_DIRECTORY] [--skip_confirmation] [--skip_baselines]

Command-Line Arguments:
    --future_date        : (Optional) The future date for which you want to predict transaction amounts. Format: DD/MM/YYYY
    --excel_dir          : (Optional) The directory where the Excel file is located. Default: current directory
    --excel_file         : (Optional) The name of the Excel file containing additional data.
    --data_file          : (Optional) The path to the CSV file containing transaction data. Default: trandata.csv
    --log_dir            : (Optional) The directory where log files will be saved. Default: logs/
    --output_dir         : (Optional) The directory where prediction files will be saved. Default: current directory
    --skip_confirmation  : (Optional) Skip confirmation prompts for overwriting files. Useful for automated workflows.
    --skip_baselines     : (Optional) Skip baseline forecasts and reports. Useful for faster runs.

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
import itertools
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.tree import DecisionTreeRegressor

import python_logging_framework as plog
from baselines import run_baselines, write_comparison_report
from config import config
from constants import TRANSACTION_AMOUNT_LABEL
from helpers import (
    apply_target_transform,
    calculate_median_absolute_error,
    calculate_percentile_errors,
    calculate_smape,
    chronological_train_test_split,
    get_quarter_end_date,
    inverse_target_transform,
    prepare_future_dates,
    preprocess_and_append_csv,
    update_data_file,
    validate_minimum_data,
    write_predictions,
)
from security import ALLOWED_CSV_EXTENSIONS, ALLOWED_EXCEL_EXTENSIONS, validate_directory_path, validate_file_path

# Load environment variables from .env file (if it exists)
load_dotenv()

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DECISION_TREE = "Decision Tree"
MODEL_RANDOM_FOREST = "Random Forest"
MODEL_GRADIENT_BOOSTING = "Gradient Boosting"


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
        - EXPENSE_PREDICTOR_SKIP_BASELINES: Skip baseline forecasts (true/false)

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
        "--skip_baselines",
        action="store_true",
        default=os.getenv("EXPENSE_PREDICTOR_SKIP_BASELINES", "false").lower() == "true",
        help="Skip baseline forecasts and comparison report generation",
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
        if not isinstance(log_level_str, str):
            raise AttributeError
        log_level = getattr(logging, log_level_str.upper())
        if not isinstance(log_level, int):
            raise AttributeError
    except AttributeError:
        # Invalid log level string, use default
        log_level = logging.INFO
        log_level_str = "INFO"

    return log_level


def _load_saved_hyperparameters(path: str, logger: logging.Logger) -> Dict[str, dict]:
    """
    Load persisted tuning results from disk.

    Args:
        path: JSON file path containing saved hyperparameters.
        logger: Logger instance for warnings.

    Returns:
        Mapping of model names to saved parameter payloads.
    """
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as handle:
            payload = json.load(handle)
        return payload.get("models", {})
    except (OSError, json.JSONDecodeError) as exc:
        plog.log_warning(logger, f"Failed to load saved hyperparameters from {path}: {exc}")
        return {}


def _persist_hyperparameters(path: str, payload: Dict[str, dict], logger: logging.Logger) -> None:
    """
    Persist tuning results to disk as JSON.

    Args:
        path: Target JSON file path for saved hyperparameters.
        payload: Tuning payload to serialize.
        logger: Logger instance for warnings.
    """
    try:
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(path, "w") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
        plog.log_info(logger, f"Saved best hyperparameters to {path}")
    except OSError as exc:
        plog.log_warning(logger, f"Failed to persist hyperparameters to {path}: {exc}")


def _evaluate_cv_mae(
    model,
    X_train: pd.DataFrame,
    y_train_fit: pd.Series,
    y_train_original: pd.Series,
    splits: int,
    transform_enabled: bool,
    transform_method: str,
) -> float:
    """
    Compute time-series cross-validated MAE for a model.

    Args:
        model: Estimator with fit/predict methods.
        X_train: Training features.
        y_train_fit: Training targets in model-fit space.
        y_train_original: Original-scale targets for MAE scoring.
        splits: Number of time-series splits.
        transform_enabled: Whether target transformation is enabled.
        transform_method: Transformation method name.

    Returns:
        Mean absolute error across splits.
    """
    tscv = TimeSeriesSplit(n_splits=splits)
    scores = []

    for train_idx, val_idx in tscv.split(X_train):
        X_tr = X_train.iloc[train_idx]
        X_val = X_train.iloc[val_idx]
        y_tr = y_train_fit.iloc[train_idx]
        y_val_original = y_train_original.iloc[val_idx]

        model.fit(X_tr, y_tr)
        y_val_pred = model.predict(X_val)
        if transform_enabled:
            y_val_pred = inverse_target_transform(y_val_pred, method=transform_method, logger=None)

        scores.append(mean_absolute_error(y_val_original, y_val_pred))

    return float(np.mean(scores)) if scores else float("nan")


def _tune_model_hyperparameters(
    model_name: str,
    model_builder,
    param_grid: Dict[str, List],
    X_train: pd.DataFrame,
    y_train_fit: pd.Series,
    y_train_original: pd.Series,
    transform_enabled: bool,
    transform_method: str,
    splits: int,
    top_k: int,
    logger: logging.Logger,
) -> Tuple[Dict[str, float], List[dict]]:
    """
    Perform grid search over hyperparameters with time-series CV MAE.

    Args:
        model_name: Display name for logging.
        model_builder: Callable that builds a model from params.
        param_grid: Parameter grid to evaluate.
        X_train: Training features.
        y_train_fit: Training targets in model-fit space.
        y_train_original: Original-scale targets for MAE scoring.
        transform_enabled: Whether target transformation is enabled.
        transform_method: Transformation method name.
        splits: Number of time-series splits.
        top_k: Number of top configurations to log.
        logger: Logger instance.

    Returns:
        Best parameter set and full results list.
    """
    if not param_grid:
        plog.log_warning(logger, f"No tuning grid configured for {model_name}. Skipping tuning.")
        return {}, []

    results: List[dict] = []
    grid_keys = list(param_grid.keys())
    grid_values = [param_grid[key] for key in grid_keys]

    for values in itertools.product(*grid_values):
        params = dict(zip(grid_keys, values))
        model = model_builder(**params)

        cv_mae = _evaluate_cv_mae(
            model,
            X_train,
            y_train_fit,
            y_train_original,
            splits,
            transform_enabled,
            transform_method,
        )

        results.append({"params": params, "cv_mae": cv_mae})

    results.sort(key=lambda item: item["cv_mae"])
    top_results = results[:top_k]

    if top_results:
        plog.log_info(logger, f"Top {len(top_results)} {model_name} configurations by CV MAE:")
        for rank, item in enumerate(top_results, start=1):
            plog.log_info(
                logger,
                f"  {rank}. cv_mae={item['cv_mae']:.4f}, params={item['params']}",
            )

    best_params = top_results[0]["params"] if top_results else {}
    return best_params, results


def _prepare_tuning_context(
    X_train: pd.DataFrame,
    output_dir: str,
    logger: logging.Logger,
) -> Tuple[dict, bool, int, int, str, Dict[str, dict], Dict[str, Any]]:
    """
    Assemble tuning configuration, saved parameters, and payload scaffolding.

    Args:
        X_train: Training features used to derive split limits.
        output_dir: Output directory for persisted results.
        logger: Logger instance.

    Returns:
        Tuning config, enabled flag, max splits, top-k logging count, persist path,
        saved parameters, and tuning payload dictionary.
    """
    tuning_config = config.get("tuning", {})
    tuning_enabled = bool(tuning_config.get("enabled", False))
    tuning_splits = int(tuning_config.get("time_series_splits", 4))
    top_k = int(tuning_config.get("top_k_log", 5))
    persist_relative_path = tuning_config.get("persist_path", "reports/best_hyperparameters.json")
    persist_path = os.path.join(output_dir, persist_relative_path)
    saved_params: Dict[str, dict] = {}

    if tuning_enabled and tuning_config.get("reuse_saved_params", False):
        saved_params = _load_saved_hyperparameters(persist_path, logger)
        if saved_params:
            plog.log_info(logger, "Loaded saved hyperparameters for reuse.")

    max_splits = min(tuning_splits, max(len(X_train) - 1, 0))
    if tuning_enabled and max_splits < 2:
        plog.log_warning(logger, "Not enough training samples for time-series tuning. Skipping tuning.")
        tuning_enabled = False

    tuning_payload: Dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "selection_metric": "cv_mae",
        "cv_metric": "mae",
        "models": {},
    }

    return tuning_config, tuning_enabled, max_splits, top_k, persist_path, saved_params, tuning_payload


def _apply_transform_if_needed(
    y_train: pd.Series,
    y_test: pd.Series,
    y_full: pd.Series,
    transform_enabled: bool,
    transform_method: str,
    logger: logging.Logger,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Apply optional target transformation to train, test, and full targets.

    Args:
        y_train: Training targets.
        y_test: Test targets.
        y_full: Full dataset targets.
        transform_enabled: Whether transformation is enabled.
        transform_method: Transformation method name.
        logger: Logger instance.

    Returns:
        Transformed training, test, and full targets.
    """
    if transform_enabled:
        plog.log_info(logger, f"Target transformation enabled: {transform_method}")
        y_train = apply_target_transform(y_train, method=transform_method, logger=logger)
        y_test = apply_target_transform(y_test, method=transform_method, logger=logger)
        y_full = apply_target_transform(y_full, method=transform_method, logger=logger)
    else:
        plog.log_info(logger, "Target transformation disabled (using original scale)")

    return y_train, y_test, y_full


def _build_model_specs(tuning_config: dict) -> Dict[str, dict]:
    """
    Build model specifications and tuning defaults.

    Args:
        tuning_config: Tuning configuration from config.

    Returns:
        Mapping of model names to spec dictionaries.
    """
    def build_decision_tree(**params: float) -> DecisionTreeRegressor:
        return DecisionTreeRegressor(
            max_depth=int(params["max_depth"]),
            min_samples_split=config["decision_tree"]["min_samples_split"],
            min_samples_leaf=int(params["min_samples_leaf"]),
            ccp_alpha=config["decision_tree"]["ccp_alpha"],
            random_state=config["decision_tree"]["random_state"],
        )

    def build_random_forest(**params: float) -> RandomForestRegressor:
        subsample = float(params["subsample"])
        return RandomForestRegressor(
            n_estimators=config["random_forest"]["n_estimators"],
            max_depth=int(params["max_depth"]),
            min_samples_split=config["random_forest"]["min_samples_split"],
            min_samples_leaf=int(params["min_samples_leaf"]),
            max_features=config["random_forest"]["max_features"],
            ccp_alpha=config["random_forest"]["ccp_alpha"],
            random_state=config["random_forest"]["random_state"],
            max_samples=subsample,
        )

    def build_gradient_boosting(**params: float) -> GradientBoostingRegressor:
        return GradientBoostingRegressor(
            n_estimators=config["gradient_boosting"]["n_estimators"],
            learning_rate=config["gradient_boosting"]["learning_rate"],
            max_depth=int(params["max_depth"]),
            min_samples_split=config["gradient_boosting"]["min_samples_split"],
            min_samples_leaf=int(params["min_samples_leaf"]),
            max_features=config["gradient_boosting"]["max_features"],
            random_state=config["gradient_boosting"]["random_state"],
            subsample=float(params["subsample"]),
        )

    return {
        "Linear Regression": {"model": LinearRegression()},
        MODEL_DECISION_TREE: {
            "builder": build_decision_tree,
            "grid": tuning_config.get("decision_tree", {}),
            "defaults": {
                "max_depth": config["decision_tree"]["max_depth"],
                "min_samples_leaf": config["decision_tree"]["min_samples_leaf"],
            },
        },
        MODEL_RANDOM_FOREST: {
            "builder": build_random_forest,
            "grid": tuning_config.get("random_forest", {}),
            "defaults": {
                "max_depth": config["random_forest"]["max_depth"],
                "min_samples_leaf": config["random_forest"]["min_samples_leaf"],
                "subsample": 1.0,
            },
        },
        MODEL_GRADIENT_BOOSTING: {
            "builder": build_gradient_boosting,
            "grid": tuning_config.get("gradient_boosting", {}),
            "defaults": {
                "max_depth": config["gradient_boosting"]["max_depth"],
                "min_samples_leaf": config["gradient_boosting"]["min_samples_leaf"],
                "subsample": 1.0,
            },
        },
    }


def _select_model_for_training(
    model_name: str,
    spec: dict,
    tuning_enabled: bool,
    saved_params: Dict[str, dict],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    y_train_original: pd.Series,
    transform_enabled: bool,
    transform_method: str,
    max_splits: int,
    top_k: int,
    tuning_payload: Dict[str, dict],
    logger: logging.Logger,
):
    """
    Select and configure a model, optionally tuning hyperparameters.

    Args:
        model_name: Display name for logging.
        spec: Model spec with builder and defaults.
        tuning_enabled: Whether tuning is enabled.
        saved_params: Previously saved tuning params keyed by model.
        X_train: Training features.
        y_train: Training targets in model-fit space.
        y_train_original: Original-scale training targets for MAE scoring.
        transform_enabled: Whether target transformation is enabled.
        transform_method: Transformation method name.
        max_splits: Maximum time-series splits.
        top_k: Number of top configurations to log.
        tuning_payload: Payload to record best config.
        logger: Logger instance.

    Returns:
        Configured model instance.
    """
    model = spec.get("model")
    if model is not None:
        return model

    tuned_params: Dict[str, float] = {}
    tuning_result: Optional[dict] = None

    if tuning_enabled and model_name in [MODEL_DECISION_TREE, MODEL_RANDOM_FOREST, MODEL_GRADIENT_BOOSTING]:
        if saved_params.get(model_name):
            tuning_result = saved_params[model_name]
            tuned_params = tuning_result.get("params", {})
            plog.log_info(logger, f"Using saved hyperparameters for {model_name}: {tuned_params}")
        else:
            tuned_params, tuning_results = _tune_model_hyperparameters(
                model_name=model_name,
                model_builder=spec["builder"],
                param_grid=spec["grid"],
                X_train=X_train,
                y_train_fit=y_train,
                y_train_original=y_train_original,
                transform_enabled=transform_enabled,
                transform_method=transform_method,
                splits=max_splits,
                top_k=top_k,
                logger=logger,
            )
            if tuning_results:
                best = tuning_results[0]
                tuning_result = {
                    "params": tuned_params,
                    "cv_mae": best["cv_mae"],
                }

    if not tuned_params:
        if tuning_enabled and model_name in [MODEL_DECISION_TREE, MODEL_RANDOM_FOREST, MODEL_GRADIENT_BOOSTING]:
            plog.log_warning(logger, f"Falling back to default hyperparameters for {model_name}.")
        tuned_params = spec["defaults"]

    model = spec["builder"](**tuned_params)
    if tuning_result:
        tuning_payload["models"][model_name] = tuning_result
    return model


def _collect_metrics(
    y_train_original: pd.Series,
    y_test_original: pd.Series,
    y_train_pred: np.ndarray,
    y_test_pred: np.ndarray,
) -> Dict[str, float]:
    """
    Compute training and test metrics on original-scale targets.

    Args:
        y_train_original: Original-scale training targets.
        y_test_original: Original-scale test targets.
        y_train_pred: Predicted values for training data.
        y_test_pred: Predicted values for test data.

    Returns:
        Dictionary of metric values.
    """
    train_rmse = np.sqrt(mean_squared_error(y_train_original, y_train_pred))
    train_mae = mean_absolute_error(y_train_original, y_train_pred)
    train_r2 = r2_score(y_train_original, y_train_pred)

    test_rmse = np.sqrt(mean_squared_error(y_test_original, y_test_pred))
    test_mae = mean_absolute_error(y_test_original, y_test_pred)
    test_r2 = r2_score(y_test_original, y_test_pred)

    y_test_array = np.asarray(y_test_original.to_numpy())
    y_test_pred_array = np.asarray(y_test_pred)
    test_medae = calculate_median_absolute_error(y_test_array, y_test_pred_array)
    test_smape = calculate_smape(y_test_array, y_test_pred_array)
    test_percentiles = calculate_percentile_errors(y_test_array, y_test_pred_array)

    return {
        "train_rmse": float(train_rmse),
        "train_mae": float(train_mae),
        "train_r2": float(train_r2),
        "test_rmse": float(test_rmse),
        "test_mae": float(test_mae),
        "test_r2": float(test_r2),
        "test_medae": float(test_medae),
        "test_smape": float(test_smape),
        "test_p50": float(test_percentiles["P50"]),
        "test_p75": float(test_percentiles["P75"]),
        "test_p90": float(test_percentiles["P90"]),
    }


def _log_metrics(logger: logging.Logger, metrics: Dict[str, float]) -> None:
    """
    Log metric summary to the configured logger.

    Args:
        logger: Logger instance.
        metrics: Metric values from model evaluation.
    """
    plog.log_info(logger, "Training Set Performance:")
    plog.log_info(logger, f"  RMSE: {metrics['train_rmse']:.2f}")
    plog.log_info(logger, f"  MAE: {metrics['train_mae']:.2f}")
    plog.log_info(logger, f"  R-squared: {metrics['train_r2']:.4f}")

    plog.log_info(logger, "Test Set Performance (Standard Metrics):")
    plog.log_info(logger, f"  RMSE: {metrics['test_rmse']:.2f}")
    plog.log_info(logger, f"  MAE: {metrics['test_mae']:.2f}")
    plog.log_info(logger, f"  R-squared: {metrics['test_r2']:.4f}")

    plog.log_info(logger, "Test Set Performance (Robust Metrics):")
    plog.log_info(logger, f"  Median Absolute Error: {metrics['test_medae']:.2f}")
    plog.log_info(logger, f"  SMAPE: {metrics['test_smape']:.2f}%")
    plog.log_info(
        logger,
        "  Error Distribution - P50: {:.2f}, P75: {:.2f}, P90: {:.2f}".format(
            metrics["test_p50"],
            metrics["test_p75"],
            metrics["test_p90"],
        ),
    )


def _make_future_predictions(
    model,
    X_full: pd.DataFrame,
    y_full: pd.Series,
    X_train_columns: pd.Index,
    future_date_for_function: str,
    transform_enabled: bool,
    transform_method: str,
    logger: logging.Logger,
) -> Tuple[pd.DatetimeIndex, np.ndarray]:
    """
    Fit on full data and generate future predictions.

    Args:
        model: Estimator with fit/predict methods.
        X_full: Full dataset features.
        y_full: Full dataset targets.
        X_train_columns: Feature columns used in training.
        future_date_for_function: End date for future prediction range.
        transform_enabled: Whether target transformation is enabled.
        transform_method: Transformation method name.
        logger: Logger instance.

    Returns:
        Tuple of future dates and predicted values.
    """
    model.fit(X_full, y_full)
    future_df, future_dates = prepare_future_dates(future_date_for_function)
    future_df = future_df.reindex(columns=X_train_columns, fill_value=0)
    y_predict = model.predict(future_df)

    if transform_enabled:
        y_predict = inverse_target_transform(y_predict, method=transform_method, logger=logger)

    return future_dates, np.round(y_predict, 2)


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
) -> List[dict]:
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
    transform_enabled = config.get("target_transform", {}).get("enabled", False)
    transform_method = config.get("target_transform", {}).get("method", "log1p")

    (
        tuning_config,
        tuning_enabled,
        max_splits,
        top_k,
        persist_path,
        saved_params,
        tuning_payload,
    ) = _prepare_tuning_context(X_train, output_dir, logger)

    # Store original target values for untransformed metrics
    y_train_original = y_train.copy()
    y_test_original = y_test.copy()

    y_train, y_test, y = _apply_transform_if_needed(
        y_train,
        y_test,
        y,
        transform_enabled,
        transform_method,
        logger,
    )

    model_specs = _build_model_specs(tuning_config)

    metrics_records: List[dict] = []

    # Train, evaluate, and predict for each model
    for model_name, spec in model_specs.items():
        plog.log_info(logger, f"--- {model_name} ---")

        model = _select_model_for_training(
            model_name,
            spec,
            tuning_enabled,
            saved_params,
            X_train,
            y_train,
            y_train_original,
            transform_enabled,
            transform_method,
            max_splits,
            top_k,
            tuning_payload,
            logger,
        )

        # Fit the model on training data
        model.fit(X_train, y_train)

        # Predict on both training and test sets
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        if transform_enabled:
            y_train_pred_original = inverse_target_transform(y_train_pred, method=transform_method, logger=logger)
            y_test_pred_original = inverse_target_transform(y_test_pred, method=transform_method, logger=logger)
        else:
            y_train_pred_original = y_train_pred
            y_test_pred_original = y_test_pred

        metrics = _collect_metrics(
            y_train_original,
            y_test_original,
            y_train_pred_original,
            y_test_pred_original,
        )
        _log_metrics(logger, metrics)

        metrics_records.append({"model": model_name, "type": "ML", **metrics})

        plog.log_info(logger, f"Retraining {model_name} on full dataset for production predictions")
        future_dates, y_predict = _make_future_predictions(
            model,
            X,
            y,
            X_train.columns,
            future_date_for_function,
            transform_enabled,
            transform_method,
            logger,
        )

        # Save predictions
        predicted_df = pd.DataFrame({"Date": future_dates, f"Predicted {TRANSACTION_AMOUNT_LABEL}": y_predict})
        output_filename = f'future_predictions_{model_name.replace(" ", "_").lower()}.csv'
        output_path = os.path.join(output_dir, output_filename)
        write_predictions(predicted_df, output_path, logger=logger, skip_confirmation=skip_confirmation)

    if tuning_payload["models"]:
        _persist_hyperparameters(persist_path, tuning_payload, logger)

    return metrics_records


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
    X, y, processed_df, raw_merged_df = preprocess_and_append_csv(file_path, excel_path=excel_path, logger=logger)

    # If Excel data was provided, update the data file with merged data
    if raw_merged_df is not None:
        plog.log_info(logger, "Excel data was provided. Updating data file with merged transaction data.")
        update_data_file(raw_merged_df, file_path, logger=logger, skip_confirmation=parsed_args.skip_confirmation)

    # Validate minimum data requirements
    min_total_samples = config["model_evaluation"].get("min_total_samples", 30)
    min_test_samples = config["model_evaluation"].get("min_test_samples", 10)
    validate_minimum_data(X, min_total=min_total_samples, min_test=min_test_samples, logger=logger)

    # Split data into training and test sets using chronological ordering
    test_size = config["model_evaluation"]["test_size"]
    X_train, X_test, y_train, y_test = chronological_train_test_split(
        X, y, processed_df, test_size=test_size, logger=logger
    )

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
    ml_metrics = train_and_evaluate_models(
        X_train, X_test, y_train, y_test, X, y, future_date_for_function, output_dir, parsed_args.skip_confirmation, logger
    )

    baseline_metrics: List[dict] = []
    baselines_enabled = config.get("baselines", {}).get("enabled", True) and not parsed_args.skip_baselines
    if baselines_enabled:
        split_idx = len(y_train)
        processed_dates = processed_df["Date"]
        train_dates = processed_dates.iloc[:split_idx]
        test_dates = processed_dates.iloc[split_idx:]
        baseline_metrics = run_baselines(
            y_full=y,
            processed_dates=processed_dates,
            train_dates=train_dates,
            test_dates=test_dates,
            future_date_for_function=future_date_for_function,
            output_dir=output_dir,
            skip_confirmation=parsed_args.skip_confirmation,
            rolling_windows_months=config["baselines"]["rolling_windows_months"],
            logger=logger,
        )
    else:
        plog.log_info(logger, "Baseline forecasts disabled via config or CLI flag.")

    write_comparison_report(ml_metrics + baseline_metrics, output_dir, logger)

    return 0


if __name__ == "__main__":
    exit(main())
