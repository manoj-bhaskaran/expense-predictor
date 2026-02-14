"""
Time-series feature engineering for the Expense Predictor.

This module generates lag features, rolling statistical features, and
calendar-based features from daily expense data to capture seasonality,
momentum, and spending cycles.

Feature generation is deterministic: the same input data always produces
the same output features.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import pandas as pd

import python_logging_framework as plog
from constants import TRANSACTION_AMOUNT_LABEL


def generate_lag_features(
    df: pd.DataFrame,
    target_col: str = TRANSACTION_AMOUNT_LABEL,
    lags: Optional[List[int]] = None,
) -> pd.DataFrame:
    """
    Create lagged versions of the target variable.

    Each lag feature represents the target value from N days prior,
    capturing recent spending momentum and short-term patterns.

    Parameters:
        df: DataFrame with the target column (must be sorted by date).
        target_col: Name of the column to lag.
        lags: Day offsets to create (e.g., [1, 3, 6, 12]).

    Returns:
        DataFrame with new lag columns appended (NaN rows at the top).
    """
    if lags is None:
        lags = [1, 3, 6, 12]

    result = df.copy()
    for lag in lags:
        result[f"lag_{lag}"] = result[target_col].shift(lag)

    return result


def generate_rolling_features(
    df: pd.DataFrame,
    target_col: str = TRANSACTION_AMOUNT_LABEL,
    windows: Optional[List[int]] = None,
) -> pd.DataFrame:
    """
    Create rolling mean and rolling standard deviation features.

    Rolling statistics smooth out daily noise and reveal underlying
    spending trends over different time horizons.

    Parameters:
        df: DataFrame with the target column (must be sorted by date).
        target_col: Name of the column to compute rolling stats on.
        windows: Window sizes in days (e.g., [7, 14, 30]).

    Returns:
        DataFrame with rolling mean and std columns appended.
    """
    if windows is None:
        windows = [7, 14, 30]

    result = df.copy()
    for window in windows:
        result[f"rolling_mean_{window}"] = (
            result[target_col].shift(1).rolling(window=window, min_periods=window).mean()
        )
        result[f"rolling_std_{window}"] = (
            result[target_col].shift(1).rolling(window=window, min_periods=window).std()
        )

    return result


def generate_calendar_features(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    """
    Add calendar-based features derived from the date column.

    Month and Day of the Month already exist in the pipeline.
    This function adds quarter and year to capture broader seasonal
    and annual cycles.

    Parameters:
        df: DataFrame containing a datetime column.
        date_col: Name of the date column.

    Returns:
        DataFrame with quarter and year columns appended.
    """
    result = df.copy()
    result["Quarter"] = result[date_col].dt.quarter
    result["Year"] = result[date_col].dt.year

    return result


def drop_nan_from_features(
    df: pd.DataFrame,
    logger: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """
    Remove rows containing NaN values introduced by lag/rolling features.

    Only rows where any feature column is NaN are dropped; rows where
    only the target is NaN are preserved by design (the upstream pipeline
    fills missing dates with 0).

    Parameters:
        df: DataFrame potentially containing NaN from feature engineering.
        logger: Logger instance for logging messages.

    Returns:
        DataFrame with NaN-containing rows removed.
    """
    rows_before = len(df)
    result = df.dropna()
    rows_dropped = rows_before - len(result)

    if rows_dropped > 0:
        plog.log_info(
            logger,
            f"Dropped {rows_dropped} rows with NaN values from feature engineering "
            f"({rows_before} -> {len(result)} rows)",
        )

    return result.reset_index(drop=True)


def save_feature_list(
    feature_names: List[str],
    output_path: str,
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Persist the list of generated feature names to a JSON artifact.

    This supports debugging and reproducibility by documenting
    the exact feature set used for model training.

    Parameters:
        feature_names: Ordered list of feature column names.
        output_path: File path for the JSON artifact.
        logger: Logger instance for logging messages.
    """
    try:
        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        payload = {
            "feature_count": len(feature_names),
            "features": feature_names,
        }
        with open(output_path, "w") as f:
            json.dump(payload, f, indent=2)

        plog.log_info(logger, f"Saved feature list ({len(feature_names)} features) to {output_path}")
    except OSError as exc:
        plog.log_warning(logger, f"Failed to save feature list to {output_path}: {exc}")


def generate_timeseries_features(
    df: pd.DataFrame,
    ts_config: Dict[str, Any],
    logger: Optional[logging.Logger] = None,
    drop_na: bool = True,
) -> pd.DataFrame:
    """
    Orchestrate all time-series feature generation steps.

    Applies lag features, rolling statistics, and calendar features
    in a deterministic order. Optionally removes NaN rows introduced
    by windowed operations.

    Parameters:
        df: DataFrame with Date and target columns, sorted by date.
        ts_config: Feature engineering configuration dictionary with
            keys ``lags``, ``rolling_windows``, and ``calendar``.
        logger: Logger instance for logging messages.
        drop_na: If True, drop rows with NaN values from feature
            engineering. Set to False when the caller handles NaN
            removal separately (e.g., to keep processed_df aligned).

    Returns:
        DataFrame with all time-series features added.
    """
    lags = ts_config.get("lags", [1, 3, 6, 12])
    rolling_windows = ts_config.get("rolling_windows", [7, 14, 30])
    calendar_enabled = ts_config.get("calendar", True)

    plog.log_info(logger, f"Generating time-series features: lags={lags}, rolling_windows={rolling_windows}, calendar={calendar_enabled}")

    # Lag features
    if lags:
        df = generate_lag_features(df, lags=lags)
        plog.log_info(logger, f"Added {len(lags)} lag features: {[f'lag_{l}' for l in lags]}")

    # Rolling statistics
    if rolling_windows:
        df = generate_rolling_features(df, windows=rolling_windows)
        plog.log_info(
            logger,
            f"Added {len(rolling_windows) * 2} rolling features "
            f"(mean + std for windows {rolling_windows})",
        )

    # Calendar features
    if calendar_enabled:
        df = generate_calendar_features(df)
        plog.log_info(logger, "Added calendar features: Quarter, Year")

    # Optionally drop NaN rows
    if drop_na:
        df = drop_nan_from_features(df, logger=logger)

    return df


def prepare_future_timeseries_features(
    historical_df: pd.DataFrame,
    future_df: pd.DataFrame,
    ts_config: Dict[str, Any],
    logger: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """
    Generate time-series features for future dates using historical data.

    Concatenates the historical tail with future dates, computes lag
    and rolling features across the boundary, then returns only the
    future rows with properly computed features.

    Parameters:
        historical_df: Processed historical DataFrame with Date and target columns.
        future_df: DataFrame of future dates with calendar features already set.
        ts_config: Feature engineering configuration.
        logger: Logger instance for logging messages.

    Returns:
        Future DataFrame with time-series features populated from historical data.
    """
    lags = ts_config.get("lags", [1, 3, 6, 12])
    rolling_windows = ts_config.get("rolling_windows", [7, 14, 30])
    calendar_enabled = ts_config.get("calendar", True)

    # Determine how much historical data we need for the widest window
    max_lookback = 0
    if lags:
        max_lookback = max(max_lookback, max(lags))
    if rolling_windows:
        # rolling needs window + 1 shift
        max_lookback = max(max_lookback, max(rolling_windows) + 1)

    # Take the tail of historical data needed for feature computation
    tail_rows = min(max_lookback, len(historical_df))
    hist_tail = historical_df[["Date", TRANSACTION_AMOUNT_LABEL]].tail(tail_rows).copy()

    # Future dates have no target values; fill with 0 for feature computation
    future_with_target = future_df.copy()
    if TRANSACTION_AMOUNT_LABEL not in future_with_target.columns:
        future_with_target[TRANSACTION_AMOUNT_LABEL] = 0.0

    # Combine historical tail + future dates
    combined = pd.concat([hist_tail, future_with_target[["Date", TRANSACTION_AMOUNT_LABEL]]], ignore_index=True)

    # Generate lag features on the combined data
    if lags:
        combined = generate_lag_features(combined, lags=lags)

    # Generate rolling features on the combined data
    if rolling_windows:
        combined = generate_rolling_features(combined, windows=rolling_windows)

    # Generate calendar features
    if calendar_enabled:
        combined = generate_calendar_features(combined)

    # Extract only the future portion
    future_portion = combined.tail(len(future_df)).copy()

    # Fill any remaining NaN with 0 (for future dates beyond lookback)
    nan_count = future_portion.isna().sum().sum()
    if nan_count > 0:
        plog.log_info(
            logger,
            f"Filled {nan_count} NaN values in future time-series features with 0",
        )
        future_portion = future_portion.fillna(0.0)

    # Drop the target column (not needed for prediction)
    future_portion = future_portion.drop(columns=[TRANSACTION_AMOUNT_LABEL], errors="ignore")

    return future_portion.reset_index(drop=True)
