"""
Unit tests for the feature_engineering module.

Tests cover lag features, rolling statistical features, calendar features,
NaN handling, feature list persistence, and the orchestrator function.
"""

import json
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from feature_engineering import (
    drop_nan_from_features,
    generate_calendar_features,
    generate_lag_features,
    generate_rolling_features,
    generate_timeseries_features,
    prepare_future_timeseries_features,
    save_feature_list,
)


@pytest.fixture
def daily_df():
    """Create a simple daily expense DataFrame for testing."""
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    np.random.seed(42)
    amounts = np.random.uniform(0, 200, size=60)
    return pd.DataFrame({"Date": dates, "Tran Amt": amounts})


@pytest.fixture
def mock_logger(mocker):
    """Create a mock logger."""
    return mocker.MagicMock()


class TestLagFeatures:
    """Tests for generate_lag_features."""

    def test_default_lags(self, daily_df):
        result = generate_lag_features(daily_df)
        assert "lag_1" in result.columns
        assert "lag_3" in result.columns
        assert "lag_6" in result.columns
        assert "lag_12" in result.columns

    def test_custom_lags(self, daily_df):
        result = generate_lag_features(daily_df, lags=[2, 5])
        assert "lag_2" in result.columns
        assert "lag_5" in result.columns
        assert "lag_1" not in result.columns

    def test_lag_values_correct(self, daily_df):
        result = generate_lag_features(daily_df, lags=[1])
        # Row 1's lag_1 should equal row 0's target
        assert result["lag_1"].iloc[1] == daily_df["Tran Amt"].iloc[0]

    def test_lag_introduces_nan(self, daily_df):
        result = generate_lag_features(daily_df, lags=[3])
        assert result["lag_3"].iloc[:3].isna().all()
        assert result["lag_3"].iloc[3:].notna().all()

    def test_original_columns_preserved(self, daily_df):
        result = generate_lag_features(daily_df, lags=[1])
        assert "Date" in result.columns
        assert "Tran Amt" in result.columns

    def test_deterministic(self, daily_df):
        r1 = generate_lag_features(daily_df, lags=[1, 3])
        r2 = generate_lag_features(daily_df, lags=[1, 3])
        pd.testing.assert_frame_equal(r1, r2)


class TestRollingFeatures:
    """Tests for generate_rolling_features."""

    def test_default_windows(self, daily_df):
        result = generate_rolling_features(daily_df)
        for w in [7, 14, 30]:
            assert f"rolling_mean_{w}" in result.columns
            assert f"rolling_std_{w}" in result.columns

    def test_custom_windows(self, daily_df):
        result = generate_rolling_features(daily_df, windows=[5])
        assert "rolling_mean_5" in result.columns
        assert "rolling_std_5" in result.columns

    def test_rolling_uses_shifted_values(self, daily_df):
        """Rolling stats should use shift(1) to avoid data leakage."""
        result = generate_rolling_features(daily_df, windows=[3])
        # The rolling mean at row 3 should be the mean of rows 0, 1, 2 (shifted by 1)
        expected = daily_df["Tran Amt"].iloc[0:3].mean()
        assert abs(result["rolling_mean_3"].iloc[3] - expected) < 1e-10

    def test_rolling_nan_count(self, daily_df):
        """First window rows should be NaN due to shift + min_periods."""
        result = generate_rolling_features(daily_df, windows=[7])
        # shift(1) makes row 0 NaN, then rolling(7, min_periods=7) needs 7 valid values
        # So rows 0-7 should be NaN (8 rows)
        assert result["rolling_mean_7"].iloc[:7].isna().all()

    def test_deterministic(self, daily_df):
        r1 = generate_rolling_features(daily_df, windows=[7])
        r2 = generate_rolling_features(daily_df, windows=[7])
        pd.testing.assert_frame_equal(r1, r2)


class TestCalendarFeatures:
    """Tests for generate_calendar_features."""

    def test_adds_quarter_and_year(self, daily_df):
        result = generate_calendar_features(daily_df)
        assert "Quarter" in result.columns
        assert "Year" in result.columns

    def test_quarter_values(self):
        dates = pd.DataFrame({
            "Date": pd.to_datetime(["2024-01-15", "2024-04-15", "2024-07-15", "2024-10-15"])
        })
        result = generate_calendar_features(dates)
        assert list(result["Quarter"]) == [1, 2, 3, 4]

    def test_year_values(self):
        dates = pd.DataFrame({
            "Date": pd.to_datetime(["2023-06-15", "2024-06-15"])
        })
        result = generate_calendar_features(dates)
        assert list(result["Year"]) == [2023, 2024]


class TestDropNanFromFeatures:
    """Tests for drop_nan_from_features."""

    def test_drops_nan_rows(self, mock_logger):
        df = pd.DataFrame({"a": [np.nan, 1.0, 2.0], "b": [1.0, 2.0, 3.0]})
        result = drop_nan_from_features(df, logger=mock_logger)
        assert len(result) == 2
        assert result["a"].notna().all()

    def test_resets_index(self, mock_logger):
        df = pd.DataFrame({"a": [np.nan, np.nan, 1.0], "b": [1.0, 2.0, 3.0]})
        result = drop_nan_from_features(df, logger=mock_logger)
        assert list(result.index) == [0]

    def test_no_nan_no_change(self, mock_logger):
        df = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]})
        result = drop_nan_from_features(df, logger=mock_logger)
        assert len(result) == 2


class TestSaveFeatureList:
    """Tests for save_feature_list."""

    def test_saves_json(self, mock_logger):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "features.json")
            save_feature_list(["a", "b", "c"], path, logger=mock_logger)

            with open(path) as f:
                data = json.load(f)
            assert data["feature_count"] == 3
            assert data["features"] == ["a", "b", "c"]

    def test_creates_directories(self, mock_logger):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "sub", "dir", "features.json")
            save_feature_list(["x"], path, logger=mock_logger)
            assert os.path.exists(path)


class TestGenerateTimeseriesFeatures:
    """Tests for the generate_timeseries_features orchestrator."""

    def test_all_features_added(self, daily_df, mock_logger):
        ts_config = {"lags": [1, 3], "rolling_windows": [5], "calendar": True}
        result = generate_timeseries_features(daily_df, ts_config, logger=mock_logger)
        assert "lag_1" in result.columns
        assert "lag_3" in result.columns
        assert "rolling_mean_5" in result.columns
        assert "rolling_std_5" in result.columns
        assert "Quarter" in result.columns
        assert "Year" in result.columns

    def test_nan_rows_dropped_by_default(self, daily_df, mock_logger):
        ts_config = {"lags": [1], "rolling_windows": [5], "calendar": True}
        result = generate_timeseries_features(daily_df, ts_config, logger=mock_logger)
        assert result.isna().sum().sum() == 0

    def test_nan_rows_preserved_when_drop_na_false(self, daily_df, mock_logger):
        ts_config = {"lags": [3], "rolling_windows": [], "calendar": False}
        result = generate_timeseries_features(daily_df, ts_config, logger=mock_logger, drop_na=False)
        assert result["lag_3"].iloc[:3].isna().all()

    def test_deterministic(self, daily_df, mock_logger):
        ts_config = {"lags": [1, 3], "rolling_windows": [7], "calendar": True}
        r1 = generate_timeseries_features(daily_df.copy(), ts_config, logger=mock_logger)
        r2 = generate_timeseries_features(daily_df.copy(), ts_config, logger=mock_logger)
        pd.testing.assert_frame_equal(r1, r2)

    def test_fewer_rows_after_nan_removal(self, daily_df, mock_logger):
        ts_config = {"lags": [1], "rolling_windows": [10], "calendar": True}
        result = generate_timeseries_features(daily_df, ts_config, logger=mock_logger)
        assert len(result) < len(daily_df)

    def test_empty_lags_and_windows(self, daily_df, mock_logger):
        ts_config = {"lags": [], "rolling_windows": [], "calendar": True}
        result = generate_timeseries_features(daily_df, ts_config, logger=mock_logger)
        assert "Quarter" in result.columns
        assert len(result) == len(daily_df)


class TestPrepareFutureTimeseriesFeatures:
    """Tests for prepare_future_timeseries_features."""

    def test_future_has_lag_features(self, daily_df, mock_logger):
        future_dates = pd.date_range("2024-03-02", periods=5, freq="D")
        future_df = pd.DataFrame({"Date": future_dates})
        ts_config = {"lags": [1, 3], "rolling_windows": [], "calendar": False}

        result = prepare_future_timeseries_features(
            daily_df, future_df, ts_config, logger=mock_logger
        )
        assert "lag_1" in result.columns
        assert "lag_3" in result.columns
        assert len(result) == 5

    def test_future_has_no_nan(self, daily_df, mock_logger):
        future_dates = pd.date_range("2024-03-02", periods=10, freq="D")
        future_df = pd.DataFrame({"Date": future_dates})
        ts_config = {"lags": [1, 3], "rolling_windows": [7], "calendar": True}

        result = prepare_future_timeseries_features(
            daily_df, future_df, ts_config, logger=mock_logger
        )
        assert result.isna().sum().sum() == 0

    def test_future_lag_uses_historical_values(self, daily_df, mock_logger):
        future_dates = pd.date_range("2024-03-02", periods=3, freq="D")
        future_df = pd.DataFrame({"Date": future_dates})
        ts_config = {"lags": [1], "rolling_windows": [], "calendar": False}

        result = prepare_future_timeseries_features(
            daily_df, future_df, ts_config, logger=mock_logger
        )
        # First future row's lag_1 should be the last historical target value
        expected = daily_df["Tran Amt"].iloc[-1]
        assert abs(result["lag_1"].iloc[0] - expected) < 1e-10

    def test_target_not_in_output(self, daily_df, mock_logger):
        future_dates = pd.date_range("2024-03-02", periods=3, freq="D")
        future_df = pd.DataFrame({"Date": future_dates})
        ts_config = {"lags": [1], "rolling_windows": [], "calendar": False}

        result = prepare_future_timeseries_features(
            daily_df, future_df, ts_config, logger=mock_logger
        )
        assert "Tran Amt" not in result.columns

    def test_calendar_features_in_future(self, daily_df, mock_logger):
        future_dates = pd.date_range("2024-04-01", periods=3, freq="D")
        future_df = pd.DataFrame({"Date": future_dates})
        ts_config = {"lags": [], "rolling_windows": [], "calendar": True}

        result = prepare_future_timeseries_features(
            daily_df, future_df, ts_config, logger=mock_logger
        )
        assert "Quarter" in result.columns
        assert result["Quarter"].iloc[0] == 2
