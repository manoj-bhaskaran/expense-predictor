"""
Baseline forecasting utilities for Expense Predictor.

Provides simple sanity-check forecasters (last value, rolling means,
seasonal naive) along with evaluation and reporting helpers.
"""

from __future__ import annotations

import logging
import os
from typing import Callable, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import python_logging_framework as plog
from constants import TRANSACTION_AMOUNT_LABEL
from helpers import prepare_future_dates, write_predictions

TEST_MAE_COLUMN = "Test MAE"
TEST_RMSE_COLUMN = "Test RMSE"


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
    r2_value = np.nan if mask.sum() < 2 else r2_score(y_true_valid, y_pred_valid)
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true_valid, y_pred_valid))),
        "mae": float(mean_absolute_error(y_true_valid, y_pred_valid)),
        "r2": float(r2_value),
    }


def _log_metrics(logger: logging.Logger, label: str, train_metrics: Optional[Dict[str, float]], test_metrics: Optional[Dict[str, float]]) -> None:
    """
    Log baseline training and test metrics.

    Args:
        logger: Logger instance.
        label: Baseline label for log headings.
        train_metrics: Training metrics or None when unavailable.
        test_metrics: Test metrics or None when unavailable.
    """
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


def _build_baseline_configs(
    rolling_windows_months: Iterable[int],
    future_dates: pd.DatetimeIndex,
    series: pd.Series,
    logger: logging.Logger,
) -> List[Dict[str, Callable]]:
    """
    Build baseline configuration objects for evaluation and forecasting.

    Args:
        rolling_windows_months: Rolling window sizes to include.
        future_dates: Future dates used by forecast functions.
        series: Full historical series for availability checks.
        logger: Logger instance.

    Returns:
        List of baseline configuration dictionaries.
    """
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
    if history_span_days >= 365:
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

    return baseline_configs


def _evaluate_baseline(
    baseline: Dict[str, Callable],
    series: pd.Series,
    train_index: pd.DatetimeIndex,
    test_index: pd.DatetimeIndex,
    future_dates: pd.DatetimeIndex,
    output_dir: str,
    skip_confirmation: bool,
    logger: logging.Logger,
) -> Dict[str, float]:
    """
    Evaluate a single baseline, save predictions, and return metrics.

    Args:
        baseline: Baseline config with prediction and forecast callables.
        series: Full historical series indexed by date.
        train_index: Datetime index for training range.
        test_index: Datetime index for test range.
        future_dates: Future dates for forecasting output.
        output_dir: Directory to write prediction files.
        skip_confirmation: Whether to skip file overwrite confirmations.
        logger: Logger instance.

    Returns:
        Metrics dictionary for the baseline.
    """
    pred_series = baseline["pred_func"](series)
    train_pred = pred_series.loc[train_index]
    test_pred = pred_series.loc[test_index]

    train_metrics = _filter_valid(series.loc[train_index], train_pred)
    test_metrics = _filter_valid(series.loc[test_index], test_pred)

    _log_metrics(logger, baseline["name"], train_metrics, test_metrics)

    future_predictions = baseline["forecast_func"](series)
    predicted_df = pd.DataFrame(
        {"Date": future_dates, f"Predicted {TRANSACTION_AMOUNT_LABEL}": np.round(future_predictions, 2)}
    )
    output_filename = f"future_predictions_{baseline['key']}.csv"
    output_path = os.path.join(output_dir, output_filename)
    write_predictions(predicted_df, output_path, logger=logger, skip_confirmation=skip_confirmation)

    return {
        "model": baseline["name"],
        "type": "Baseline",
        "train_rmse": train_metrics["rmse"] if train_metrics else np.nan,
        "train_mae": train_metrics["mae"] if train_metrics else np.nan,
        "train_r2": train_metrics["r2"] if train_metrics else np.nan,
        "test_rmse": test_metrics["rmse"] if test_metrics else np.nan,
        "test_mae": test_metrics["mae"] if test_metrics else np.nan,
        "test_r2": test_metrics["r2"] if test_metrics else np.nan,
    }


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

    train_index = pd.DatetimeIndex(pd.to_datetime(train_dates))
    test_index = pd.DatetimeIndex(pd.to_datetime(test_dates))
    baseline_configs = _build_baseline_configs(rolling_windows_months, future_dates, series, logger)

    return [
        _evaluate_baseline(
            baseline,
            series,
            train_index,
            test_index,
            future_dates,
            output_dir,
            skip_confirmation,
            logger,
        )
        for baseline in baseline_configs
    ]


def write_comparison_report(
    metrics_records: List[Dict[str, float]],
    output_dir: str,
    logger: logging.Logger,
    filename: str = "model_comparison_report.csv",
    subdir: str = "reports",
) -> str:
    """
    Write a comprehensive comparison report ranking models by test MAE and RMSE.
    
    Generates:
    1. CSV file with ranked model metrics
    2. Markdown summary with recommendation and rationale
    3. Flags models with negative R² scores
    
    Args:
        metrics_records: List of dictionaries containing model metrics
        output_dir: Directory where reports will be saved
        logger: Logger instance
        filename: Name of the CSV output file
        subdir: Subdirectory for reports (default: "reports")
    
    Returns:
        str: Path to the generated CSV report
    """
    from datetime import datetime
    
    if not metrics_records:
        plog.log_info(logger, "No metrics records to write in comparison report.")
        return ""
    
    # Create DataFrame from metrics
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
    
    # Add ranking columns
    report_df["Test MAE Rank"] = report_df[TEST_MAE_COLUMN].rank(method="min")
    report_df["Test RMSE Rank"] = report_df[TEST_RMSE_COLUMN].rank(method="min")
    
    # Flag negative R² models
    report_df["R2 Warning"] = report_df["Test R2"].apply(
        lambda x: "NEGATIVE_R2" if pd.notna(x) and x < 0 else ""
    )
    
    # Sort by performance
    report_df = report_df.sort_values(
        by=[TEST_MAE_COLUMN, TEST_RMSE_COLUMN, "Model"], 
        na_position="last"
    )
    
    # Create reports directory
    report_dir = os.path.join(output_dir, subdir)
    os.makedirs(report_dir, exist_ok=True)
    
    # 1. Save CSV report
    csv_output_path = os.path.join(report_dir, filename)
    report_df.to_csv(csv_output_path, index=False)
    plog.log_info(logger, f"Model comparison CSV saved to {csv_output_path}")
    
    # 2. Generate Markdown summary
    md_filename = "model_comparison_summary.md"
    md_output_path = os.path.join(report_dir, md_filename)
    
    # Get best model (first row after sorting)
    best_model_row = report_df.iloc[0]
    best_model_name = best_model_row["Model"]
    best_mae = best_model_row[TEST_MAE_COLUMN]
    best_rmse = best_model_row[TEST_RMSE_COLUMN]
    best_r2 = best_model_row["Test R2"]
    
    # Count negative R² models
    negative_r2_count = (report_df["Test R2"] < 0).sum()
    
    # Get top 3 models for display
    top_3_models = report_df.head(3)
    
    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write("# Model Comparison Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Models Evaluated:** {len(report_df)}\n\n")
        
        f.write("---\n\n")
        
        # Recommendation section
        f.write("## Recommended Production Model\n\n")
        f.write(f"**Model:** `{best_model_name}`\n\n")
        
        # Performance metrics
        f.write("### Performance Metrics\n\n")
        f.write(f"- **Test MAE:** {best_mae:.2f}\n")
        f.write(f"- **Test RMSE:** {best_rmse:.2f}\n")
        if pd.notna(best_r2):
            f.write(f"- **Test R²:** {best_r2:.4f}\n\n")
        else:
            f.write(f"- **Test R²:** N/A\n\n")
        
        # Rationale
        f.write("### Rationale\n\n")
        f.write(f"The **{best_model_name}** model was selected based on the following criteria:\n\n")
        f.write(f"1. **Lowest Mean Absolute Error (MAE):** {best_mae:.2f}\n")
        f.write(f"   - This indicates the model has the best average prediction accuracy on unseen test data\n\n")
        f.write(f"2. **Strong Generalization Performance**\n")
        f.write(f"   - Test RMSE: {best_rmse:.2f}\n")
        if pd.notna(best_r2):
            f.write(f"   - Test R²: {best_r2:.4f}\n\n")
        
        # Warnings if applicable
        if pd.notna(best_r2):
            if best_r2 < 0:
                f.write("**WARNING:** The recommended model has a negative R² score, ")
                f.write("indicating predictions are worse than a simple mean baseline. ")
                f.write("Consider:\n")
                f.write("- Collecting more training data\n")
                f.write("- Feature engineering improvements\n")
                f.write("- Alternative modeling approaches\n\n")
            elif best_r2 < 0.3:
                f.write("**NOTE:** The R² score is relatively low (< 0.3), ")
                f.write("suggesting limited predictive power. Consider collecting more data or ")
                f.write("engineering additional features.\n\n")
        
        f.write("---\n\n")
        
        # Top 3 models section
        f.write("## Top 3 Models\n\n")
        f.write("| Rank | Model | Type | Test MAE | Test RMSE | Test R² |\n")
        f.write("|------|-------|------|----------|-----------|----------|\n")
        
        for idx, (_, row) in enumerate(top_3_models.iterrows(), 1):
            model_name = row["Model"]
            model_type = row.get("Type", "ML")
            mae = row[TEST_MAE_COLUMN]
            rmse = row[TEST_RMSE_COLUMN]
            r2 = row["Test R2"]
            
            # Add warning emoji if R² is negative
            r2_display = f"{r2:.4f}" if pd.notna(r2) else "N/A"
            warning = " ⚠️" if pd.notna(r2) and r2 < 0 else ""
            
            f.write(f"| {idx} | {model_name} | {model_type} | {mae:.2f} | {rmse:.2f} | {r2_display}{warning} |\n")
        
        f.write("\n")
        
        # Warning summary if there are negative R² models
        if negative_r2_count > 0:
            f.write(f"**Warning:** {negative_r2_count} model(s) have negative R² scores (marked with ⚠️)\n\n")
        
        f.write("---\n\n")
        
        # Complete rankings section
        f.write("## Complete Model Rankings\n\n")
        f.write("| Rank | Model | Type | Test MAE | Test RMSE | Test R² | Train MAE | Train RMSE | Train R² | Warning |\n")
        f.write("|------|-------|------|----------|-----------|---------|-----------|------------|----------|----------|\n")
        
        for idx, (_, row) in enumerate(report_df.iterrows(), 1):
            model_name = row["Model"]
            model_type = row.get("Type", "ML")
            test_mae = row[TEST_MAE_COLUMN]
            test_rmse = row[TEST_RMSE_COLUMN]
            test_r2 = row["Test R2"]
            train_mae = row.get("Train MAE", np.nan)
            train_rmse = row.get("Train RMSE", np.nan)
            train_r2 = row.get("Train R2", np.nan)
            warning = row.get("R2 Warning", "")
            
            # Format values
            test_r2_str = f"{test_r2:.4f}" if pd.notna(test_r2) else "N/A"
            train_mae_str = f"{train_mae:.2f}" if pd.notna(train_mae) else "N/A"
            train_rmse_str = f"{train_rmse:.2f}" if pd.notna(train_rmse) else "N/A"
            train_r2_str = f"{train_r2:.4f}" if pd.notna(train_r2) else "N/A"
            
            f.write(f"| {idx} | {model_name} | {model_type} | {test_mae:.2f} | {test_rmse:.2f} | ")
            f.write(f"{test_r2_str} | {train_mae_str} | {train_rmse_str} | {train_r2_str} | {warning} |\n")
        
        f.write("\n---\n\n")
        
        # Instructions for switching models
        f.write("## How to Switch Production Models\n\n")
        f.write("To change the default production model:\n\n")
        f.write("1. Open `config.yaml` in your project root\n")
        f.write("2. Locate the `production` section\n")
        f.write("3. Update the `default_model` field\n\n")
        f.write("**Valid model options:**\n")
        f.write("- `Linear Regression`\n")
        f.write("- `Decision Tree`\n")
        f.write("- `Random Forest`\n")
        f.write("- `Gradient Boosting`\n\n")
        f.write("**Example configuration:**\n")
        f.write("```yaml\n")
        f.write("production:\n")
        f.write(f"  default_model: \"{best_model_name}\"\n")
        f.write("```\n\n")
        f.write("After updating the configuration, the selected model will be used for all future predictions.\n\n")
        
        f.write("---\n\n")
        f.write("*This report was automatically generated by the Expense Predictor system.*\n")
    
    plog.log_info(logger, f"Model comparison summary saved to {md_output_path}")
    plog.log_info(logger, f"Best performing model: {best_model_name} (Test MAE: {best_mae:.2f})")
    
    return csv_output_path
