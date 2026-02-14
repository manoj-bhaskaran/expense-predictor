"""
Quantile Regression Forecasting Module

This module provides probabilistic forecasts using quantile regression
to support budgeting scenarios with prediction intervals instead of
point estimates.

Features:
- Quantile regression using GradientBoostingRegressor or QuantileRegressor
- Multi-quantile predictions (P50, P75, P90) per forecast period
- Pinball loss evaluation metric
- Coverage metrics validation
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import QuantileRegressor

import python_logging_framework as plog
from config import config


def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray, quantile: float) -> float:
    """
    Calculate pinball loss for quantile predictions.

    The pinball loss (also called quantile loss) is an asymmetric loss function
    used to evaluate quantile predictions. It penalizes over-predictions and
    under-predictions differently based on the quantile level.

    Parameters:
        y_true: True target values
        y_pred: Predicted quantile values
        quantile: Quantile level (e.g., 0.5 for median, 0.75 for 75th percentile)

    Returns:
        float: Average pinball loss across all samples

    Formula:
        loss = mean(max(quantile * (y_true - y_pred), (quantile - 1) * (y_true - y_pred)))
    """
    errors = y_true - y_pred
    loss = np.where(errors >= 0, quantile * errors, (quantile - 1) * errors)
    return float(np.mean(loss))


def calculate_coverage(y_true: np.ndarray, y_pred: np.ndarray, quantile: float) -> float:
    """
    Calculate empirical coverage for a quantile prediction.

    Coverage measures the proportion of actual values that fall below
    the predicted quantile. For a well-calibrated model, the empirical
    coverage should be close to the theoretical quantile level.

    Parameters:
        y_true: True target values
        y_pred: Predicted quantile values
        quantile: Theoretical quantile level (e.g., 0.75)

    Returns:
        float: Empirical coverage rate (proportion of y_true < y_pred)

    Example:
        For quantile=0.75, we expect coverage ≈ 0.75
        (75% of actual values should be below the prediction)
    """
    coverage = np.mean(y_true <= y_pred)
    return float(coverage)


def train_quantile_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    quantile: float,
    model_type: str = "gradient_boosting",
    logger: Optional[logging.Logger] = None,
) -> Any:
    """
    Train a quantile regression model for a specific quantile.

    Parameters:
        X_train: Training features
        y_train: Training target values
        quantile: Quantile to predict (e.g., 0.5, 0.75, 0.90)
        model_type: Type of model ('gradient_boosting' or 'linear')
        logger: Logger instance

    Returns:
        Trained quantile regression model
    """
    plog.log_info(logger, f"Training {model_type} quantile model for q={quantile:.2f}")

    if model_type == "gradient_boosting":
        # Use GradientBoostingRegressor with quantile loss
        gb_config = config.get("gradient_boosting", {})
        model = GradientBoostingRegressor(
            loss="quantile",
            alpha=quantile,
            n_estimators=gb_config.get("n_estimators", 100),
            learning_rate=gb_config.get("learning_rate", 0.1),
            max_depth=gb_config.get("max_depth", 5),
            min_samples_split=gb_config.get("min_samples_split", 10),
            min_samples_leaf=gb_config.get("min_samples_leaf", 5),
            max_features=gb_config.get("max_features", "sqrt"),
            random_state=gb_config.get("random_state", 42),
        )
    elif model_type == "linear":
        # Use QuantileRegressor (linear quantile regression)
        model = QuantileRegressor(
            quantile=quantile,
            alpha=0.0,  # No regularization by default
            solver="highs",  # Use HiGHS solver (faster and more stable)
        )
    else:
        raise ValueError(f"Invalid model_type: {model_type}. Must be 'gradient_boosting' or 'linear'")

    model.fit(X_train, y_train)
    plog.log_info(logger, f"Model trained successfully for q={quantile:.2f}")

    return model


def evaluate_quantile_model(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    quantile: float,
    logger: Optional[logging.Logger] = None,
) -> Dict[str, float]:
    """
    Evaluate a quantile regression model on test data.

    Parameters:
        model: Trained quantile regression model
        X_test: Test features
        y_test: Test target values
        quantile: Quantile level the model was trained for
        logger: Logger instance

    Returns:
        Dictionary with evaluation metrics (pinball_loss, coverage, coverage_error)
    """
    y_pred = model.predict(X_test)

    # Calculate pinball loss
    pb_loss = pinball_loss(y_test.values, y_pred, quantile)

    # Calculate coverage
    coverage = calculate_coverage(y_test.values, y_pred, quantile)

    # Calculate coverage error (deviation from theoretical quantile)
    coverage_error = abs(coverage - quantile)

    metrics = {
        "pinball_loss": pb_loss,
        "coverage": coverage,
        "coverage_error": coverage_error,
    }

    plog.log_info(
        logger,
        f"Quantile {quantile:.2f} - Pinball Loss: {pb_loss:.4f}, "
        f"Coverage: {coverage:.4f} (target: {quantile:.2f}, error: {coverage_error:.4f})"
    )

    return metrics


def generate_quantile_predictions(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    X_full: pd.DataFrame,
    y_full: pd.Series,
    future_df: pd.DataFrame,
    quantiles: List[float],
    model_type: str = "gradient_boosting",
    logger: Optional[logging.Logger] = None,
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generate multi-quantile predictions for future dates.

    This function trains separate quantile regression models for each
    specified quantile and generates predictions for future dates.

    Parameters:
        X_train: Training features
        y_train: Training target values
        X_test: Test features
        y_test: Test target values
        X_full: Full dataset features (for retraining)
        y_full: Full dataset target values (for retraining)
        future_df: Future dates features for prediction
        quantiles: List of quantiles to predict (e.g., [0.50, 0.75, 0.90])
        model_type: Type of model ('gradient_boosting' or 'linear')
        logger: Logger instance

    Returns:
        Tuple of (predictions_df, metrics_list)
        - predictions_df: DataFrame with columns for each quantile
        - metrics_list: List of evaluation metrics for each quantile
    """
    plog.log_info(logger, f"Generating quantile predictions for {len(quantiles)} quantiles")

    predictions = {}
    metrics_list = []

    for quantile in quantiles:
        # Train model on training set
        model = train_quantile_model(X_train, y_train, quantile, model_type, logger)

        # Evaluate on test set
        test_metrics = evaluate_quantile_model(model, X_test, y_test, quantile, logger)
        test_metrics["quantile"] = quantile
        metrics_list.append(test_metrics)

        # Retrain on full dataset for production predictions
        plog.log_info(logger, f"Retraining quantile {quantile:.2f} model on full dataset")
        model = train_quantile_model(X_full, y_full, quantile, model_type, logger)

        # Generate future predictions
        y_pred_future = model.predict(future_df)
        predictions[quantile] = np.round(y_pred_future, 2)

    # Create predictions DataFrame
    predictions_df = pd.DataFrame(predictions)

    # Rename columns to P50, P75, P90 format
    predictions_df.columns = [f"P{int(q * 100)}" for q in quantiles]

    plog.log_info(logger, f"Generated predictions for {len(future_df)} future dates")

    return predictions_df, metrics_list


def save_quantile_predictions(
    predictions_df: pd.DataFrame,
    future_dates: pd.DatetimeIndex,
    output_path: str,
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Save quantile predictions to CSV with proper formatting.

    Parameters:
        predictions_df: DataFrame with quantile predictions (P50, P75, P90 columns)
        future_dates: DatetimeIndex of future dates
        output_path: Path to save CSV file
        logger: Logger instance
    """
    # Combine dates and predictions
    output_df = pd.DataFrame({"Date": future_dates})
    output_df = pd.concat([output_df, predictions_df], axis=1)

    # Format dates
    output_df["Date"] = output_df["Date"].dt.strftime("%d/%m/%Y")

    # Save to CSV
    output_df.to_csv(output_path, index=False)
    plog.log_info(logger, f"Quantile predictions saved to {output_path}")
