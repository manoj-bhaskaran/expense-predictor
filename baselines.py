"""
Baseline forecasting utilities for Expense Predictor.

Provides simple sanity-check forecasters (last value, rolling means,
seasonal naive) along with evaluation and reporting helpers.
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import python_logging_framework as plog
from constants import TRANSACTION_AMOUNT_LABEL
from helpers import prepare_future_dates, write_predictions


def _ensure_series_with_dates(series: pd.Series, dates: pd.Series) -> pd.Series:
    """Return a series indexed by dates for time-based baselines."""
    if len(series) != len(dates):
        raise ValueError("Series length must match dates length for baseline evaluation.")
    return pd.Series(series.values, index=pd.to_datetime(dates), name=TRANSACTION_AMOUNT_LABEL)


def _filter_valid(y_true: pd.Series, y_pred: pd.Series) -> Optional[Dict[str, float]]:
    """Filter NaNs and calculate metrics. Returns None when no valid samples."""
    mask = ~(y_true.isna() | y_pred.isna())
    if mask.sum() == 0:
        return None
    y_true_valid = y_true[mask]
    y_pred_valid = y_pred[mask]
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true_valid, y_pred_valid))),
        "mae": float(mean_absolute_error(y_true_valid, y_pred_valid)),
        "r2": float(r2_score(y_true_valid, y_pred_valid)),
    }


def _log_metrics(logger: logging.Logger, label: str, train_metrics: Optional[Dict[str, float]], test_metrics: Optional[Dict[str, float]]) -> None:
    plog.log_info(logger, f"--- {label} ---")
    if train_metrics:
        plog.log_info(logger, "Training Set Performance:")
        plog.log_info(logger, f"  RMSE: {train_metrics['rmse']:.2f}")
        plog.log_info(logger, f"  MAE: {train_metrics['mae']:.2f}")
        plog.log_info(logger, f"  R-squared: {train_metrics['r2']:.4f}")
    else:
        plog.log_info(logger, "Training Set Performance: Not enough history to compute metrics.")

    if test_metrics:
        plog.log_info(logger, "Test Set Performance:")
        plog.log_info(logger, f"  RMSE: {test_metrics['rmse']:.2f}")
        plog.log_info(logger, f"  MAE: {test_metrics['mae']:.2f}")
        plog.log_info(logger, f"  R-squared: {test_metrics['r2']:.4f}")
    else:
        plog.log_info(logger, "Test Set Performance: Not enough history to compute metrics.")


def last_value_predictions(series: pd.Series) -> pd.Series:
    """Predict each point as the previous observed value."""
    return series.shift(1)


def rolling_mean_predictions(series: pd.Series, window_months: int) -> pd.Series:
    """Predict each point using the mean of the previous window_months history."""
    predictions = []
    for current_date in series.index:
        start_date = current_date - DateOffset(months=window_months)
        history = series.loc[(series.index >= start_date) & (series.index < current_date)]
        predictions.append(history.mean() if not history.empty else np.nan)
    return pd.Series(predictions, index=series.index)


def seasonal_naive_predictions(series: pd.Series, years_back: int = 1) -> pd.Series:
    """Predict each point using the value from the same period in previous years."""
    predictions = []
    for current_date in series.index:
        prior_date = current_date - DateOffset(years=years_back)
        predictions.append(series.get(prior_date, np.nan))
    return pd.Series(predictions, index=series.index)


def last_value_forecast(series: pd.Series, forecast_dates: pd.DatetimeIndex) -> np.ndarray:
    """Forecast future dates using the last observed value."""
    last_value = float(series.iloc[-1])
    return np.full(len(forecast_dates), last_value)


def rolling_mean_forecast(series: pd.Series, forecast_dates: pd.DatetimeIndex, window_months: int) -> np.ndarray:
    """Forecast future dates using the rolling mean window up to the latest observed date."""
    last_date = series.index.max()
    start_date = last_date - DateOffset(months=window_months)
    history = series.loc[series.index >= start_date]
    mean_value = float(history.mean()) if not history.empty else float(series.mean())
    return np.full(len(forecast_dates), mean_value)


def seasonal_naive_forecast(
    series: pd.Series, forecast_dates: pd.DatetimeIndex, years_back: int = 1, fallback_to_last: bool = True
) -> np.ndarray:
    """Forecast future dates using the same period in previous years with optional fallback."""
    forecasts = []
    last_value = float(series.iloc[-1])
    for forecast_date in forecast_dates:
        prior_date = forecast_date - DateOffset(years=years_back)
        if prior_date in series.index:
            forecasts.append(float(series.loc[prior_date]))
        elif fallback_to_last:
            forecasts.append(last_value)
        else:
            forecasts.append(np.nan)
    return np.array(forecasts)


def run_baselines(
    y_full: pd.Series,
    processed_dates: pd.Series,
    train_dates: pd.Series,
    test_dates: pd.Series,
    future_date_for_function: str,
    output_dir: str,
    skip_confirmation: bool,
    rolling_windows_months: Iterable[int],
    logger: logging.Logger,
) -> List[Dict[str, float]]:
    """Run baseline forecasts, save predictions, and return metrics."""
    series = _ensure_series_with_dates(y_full, processed_dates)

    _, future_dates = prepare_future_dates(future_date_for_function)
    metrics_records: List[Dict[str, float]] = []

    baseline_configs = [
        {
            "name": "Naive Last Value",
            "key": "naive_last_value",
            "pred_func": last_value_predictions,
            "forecast_func": lambda s: last_value_forecast(s, future_dates),
        }
    ]

    for window in rolling_windows_months:
        baseline_configs.append(
            {
                "name": f"Rolling Mean {window}M",
                "key": f"rolling_mean_{window}m",
                "pred_func": lambda s, w=window: rolling_mean_predictions(s, w),
                "forecast_func": lambda s, w=window: rolling_mean_forecast(s, future_dates, w),
            }
        )

    history_span_days = (series.index.max() - series.index.min()).days
    seasonal_supported = history_span_days >= 365
    if seasonal_supported:
        baseline_configs.append(
            {
                "name": "Seasonal Naive (YoY)",
                "key": "seasonal_naive_yoy",
                "pred_func": lambda s: seasonal_naive_predictions(s, years_back=1),
                "forecast_func": lambda s: seasonal_naive_forecast(s, future_dates, years_back=1, fallback_to_last=True),
            }
        )
    else:
        plog.log_info(logger, "Seasonal naive baseline skipped: less than 12 months of history available.")

    for baseline in baseline_configs:
        pred_series = baseline["pred_func"](series)
        train_index = pd.DatetimeIndex(pd.to_datetime(train_dates))
        test_index = pd.DatetimeIndex(pd.to_datetime(test_dates))
        train_pred = pred_series.loc[train_index]
        test_pred = pred_series.loc[test_index]

        train_metrics = _filter_valid(series.loc[train_index], train_pred)
        test_metrics = _filter_valid(series.loc[test_index], test_pred)

        _log_metrics(logger, baseline["name"], train_metrics, test_metrics)

        metrics_records.append(
            {
                "model": baseline["name"],
                "type": "Baseline",
                "train_rmse": train_metrics["rmse"] if train_metrics else np.nan,
                "train_mae": train_metrics["mae"] if train_metrics else np.nan,
                "train_r2": train_metrics["r2"] if train_metrics else np.nan,
                "test_rmse": test_metrics["rmse"] if test_metrics else np.nan,
                "test_mae": test_metrics["mae"] if test_metrics else np.nan,
                "test_r2": test_metrics["r2"] if test_metrics else np.nan,
            }
        )

        future_predictions = baseline["forecast_func"](series)
        predicted_df = pd.DataFrame(
            {"Date": future_dates, f"Predicted {TRANSACTION_AMOUNT_LABEL}": np.round(future_predictions, 2)}
        )
        output_filename = f"future_predictions_{baseline['key']}.csv"
        output_path = os.path.join(output_dir, output_filename)
        write_predictions(predicted_df, output_path, logger=logger, skip_confirmation=skip_confirmation)

    return metrics_records


def write_comparison_report(
    metrics_records: List[Dict[str, float]], output_dir: str, logger: logging.Logger, filename: str = "model_comparison_report.csv"
) -> str:
    """Write a comparison report ranking models by test MAE and RMSE."""
    if not metrics_records:
        plog.log_info(logger, "No metrics records to write in comparison report.")
        return ""

    report_df = pd.DataFrame(metrics_records)
    report_df = report_df.rename(
        columns={
            "model": "Model",
            "type": "Type",
            "train_rmse": "Train RMSE",
            "train_mae": "Train MAE",
            "train_r2": "Train R2",
            "test_rmse": "Test RMSE",
            "test_mae": "Test MAE",
            "test_r2": "Test R2",
        }
    )

    report_df["Test MAE Rank"] = report_df["Test MAE"].rank(method="min")
    report_df["Test RMSE Rank"] = report_df["Test RMSE"].rank(method="min")
    report_df = report_df.sort_values(by=["Test MAE", "Test RMSE", "Model"], na_position="last")

    output_path = os.path.join(output_dir, filename)
    report_df.to_csv(output_path, index=False)
    plog.log_info(logger, f"Model comparison report saved to {output_path}")
    return output_path
