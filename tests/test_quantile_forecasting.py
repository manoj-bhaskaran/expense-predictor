"""
Unit tests for quantile_forecasting.py module.

Tests cover quantile regression model training, pinball loss calculation,
coverage metrics, and multi-quantile prediction generation.
"""

import os
import tempfile

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import QuantileRegressor

from quantile_forecasting import (
    calculate_coverage,
    evaluate_quantile_model,
    generate_quantile_predictions,
    pinball_loss,
    save_quantile_predictions,
    train_quantile_model,
)


@pytest.mark.unit
class TestPinballLoss:
    """Test pinball loss calculation."""

    def test_pinball_loss_median_perfect(self):
        """Test pinball loss is 0 for perfect median prediction."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        loss = pinball_loss(y_true, y_pred, 0.5)
        assert loss == pytest.approx(0.0)

    def test_pinball_loss_median_over_prediction(self):
        """Test pinball loss for over-prediction at median."""
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([2.0, 3.0, 4.0])  # All predictions 1.0 too high
        loss = pinball_loss(y_true, y_pred, 0.5)
        # For median (q=0.5), over-predictions are penalized by (1-0.5)*error = 0.5*error
        expected = 0.5 * 1.0  # Mean of [0.5, 0.5, 0.5]
        assert loss == pytest.approx(expected)

    def test_pinball_loss_median_under_prediction(self):
        """Test pinball loss for under-prediction at median."""
        y_true = np.array([2.0, 3.0, 4.0])
        y_pred = np.array([1.0, 2.0, 3.0])  # All predictions 1.0 too low
        loss = pinball_loss(y_true, y_pred, 0.5)
        # For median (q=0.5), under-predictions are penalized by q*error = 0.5*error
        expected = 0.5 * 1.0  # Mean of [0.5, 0.5, 0.5]
        assert loss == pytest.approx(expected)

    def test_pinball_loss_upper_quantile(self):
        """Test pinball loss for upper quantile (0.75)."""
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([2.0, 3.0, 4.0])  # All predictions 1.0 too high
        loss = pinball_loss(y_true, y_pred, 0.75)
        # For q=0.75, over-predictions are penalized by (1-0.75)*error = 0.25*error
        expected = 0.25 * 1.0  # Mean of [0.25, 0.25, 0.25]
        assert loss == pytest.approx(expected)

    def test_pinball_loss_lower_quantile(self):
        """Test pinball loss for lower quantile (0.25)."""
        y_true = np.array([2.0, 3.0, 4.0])
        y_pred = np.array([1.0, 2.0, 3.0])  # All predictions 1.0 too low
        loss = pinball_loss(y_true, y_pred, 0.25)
        # For q=0.25, under-predictions are penalized by q*error = 0.25*error
        expected = 0.25 * 1.0  # Mean of [0.25, 0.25, 0.25]
        assert loss == pytest.approx(expected)

    def test_pinball_loss_mixed_errors(self):
        """Test pinball loss with mixed over and under predictions."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0])
        y_pred = np.array([0.5, 2.5, 2.5, 4.5])  # Under, over, under, over
        loss = pinball_loss(y_true, y_pred, 0.5)
        # Errors: [0.5 (under), -0.5 (over), 0.5 (under), -0.5 (over)]
        # Losses: [0.5*0.5, 0.5*0.5, 0.5*0.5, 0.5*0.5] = [0.25, 0.25, 0.25, 0.25]
        expected = 0.25
        assert loss == pytest.approx(expected)


@pytest.mark.unit
class TestCoverage:
    """Test coverage calculation."""

    def test_coverage_perfect(self):
        """Test coverage when exactly the right proportion falls below."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        y_pred = np.array([7.5] * 10)  # Values 1-7 are < 7.5, value 8 is > 7.5
        coverage = calculate_coverage(y_true, y_pred, 0.75)
        # 7 values (1.0-7.0) are <= 7.5, and 8.0-10.0 are > 7.5
        # So coverage is 7/10 = 0.7
        assert coverage == pytest.approx(0.7)

    def test_coverage_all_below(self):
        """Test coverage when all values fall below prediction."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([10.0] * 5)  # All below
        coverage = calculate_coverage(y_true, y_pred, 0.75)
        assert coverage == pytest.approx(1.0)

    def test_coverage_none_below(self):
        """Test coverage when no values fall below prediction."""
        y_true = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
        y_pred = np.array([5.0] * 5)  # None below
        coverage = calculate_coverage(y_true, y_pred, 0.75)
        assert coverage == pytest.approx(0.0)

    def test_coverage_half_below(self):
        """Test coverage when exactly half fall below."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        y_pred = np.array([3.5] * 6)  # 3 below, 3 above
        coverage = calculate_coverage(y_true, y_pred, 0.5)
        assert coverage == pytest.approx(0.5)

    def test_coverage_includes_equal(self):
        """Test that coverage includes values equal to prediction."""
        y_true = np.array([1.0, 2.0, 3.0, 3.0, 4.0, 5.0])
        y_pred = np.array([3.0] * 6)  # 2 below, 2 equal, 2 above
        coverage = calculate_coverage(y_true, y_pred, 0.5)
        # Should count: 1.0, 2.0, 3.0, 3.0 as <= 3.0 = 4/6 = 0.667
        assert coverage == pytest.approx(4.0 / 6.0)


@pytest.mark.unit
class TestTrainQuantileModel:
    """Test quantile model training."""

    def test_train_gradient_boosting_model(self, sample_data, mock_logger):
        """Test training gradient boosting quantile model."""
        X_train, y_train = sample_data
        model = train_quantile_model(X_train, y_train, 0.5, "gradient_boosting", mock_logger)
        assert isinstance(model, GradientBoostingRegressor)
        assert model.loss == "quantile"
        assert model.alpha == 0.5

    def test_train_linear_model(self, sample_data, mock_logger):
        """Test training linear quantile model."""
        X_train, y_train = sample_data
        model = train_quantile_model(X_train, y_train, 0.75, "linear", mock_logger)
        assert isinstance(model, QuantileRegressor)
        assert model.quantile == 0.75

    def test_train_different_quantiles(self, sample_data, mock_logger):
        """Test training models for different quantiles."""
        X_train, y_train = sample_data
        quantiles = [0.25, 0.5, 0.75, 0.9]
        for q in quantiles:
            model = train_quantile_model(X_train, y_train, q, "gradient_boosting", mock_logger)
            assert model.alpha == q

    def test_train_invalid_model_type(self, sample_data, mock_logger):
        """Test that invalid model type raises ValueError."""
        X_train, y_train = sample_data
        with pytest.raises(ValueError, match="Invalid model_type"):
            train_quantile_model(X_train, y_train, 0.5, "invalid_type", mock_logger)


@pytest.mark.unit
class TestEvaluateQuantileModel:
    """Test quantile model evaluation."""

    def test_evaluate_returns_metrics(self, sample_data, mock_logger):
        """Test that evaluation returns expected metrics."""
        X_train, y_train = sample_data
        X_test, y_test = sample_data  # Reuse for simplicity
        model = train_quantile_model(X_train, y_train, 0.5, "linear", mock_logger)
        metrics = evaluate_quantile_model(model, X_test, y_test, 0.5, mock_logger)

        assert "pinball_loss" in metrics
        assert "coverage" in metrics
        assert "coverage_error" in metrics
        assert isinstance(metrics["pinball_loss"], float)
        assert isinstance(metrics["coverage"], float)
        assert isinstance(metrics["coverage_error"], float)

    def test_evaluate_coverage_error(self, sample_data, mock_logger):
        """Test that coverage error is absolute difference from target."""
        X_train, y_train = sample_data
        X_test, y_test = sample_data
        model = train_quantile_model(X_train, y_train, 0.75, "linear", mock_logger)
        metrics = evaluate_quantile_model(model, X_test, y_test, 0.75, mock_logger)

        # Coverage error should be |coverage - 0.75|
        expected_error = abs(metrics["coverage"] - 0.75)
        assert metrics["coverage_error"] == pytest.approx(expected_error)


@pytest.mark.unit
class TestGenerateQuantilePredictions:
    """Test multi-quantile prediction generation."""

    def test_generate_predictions_basic(self, sample_data, mock_logger):
        """Test generating predictions for multiple quantiles."""
        X_train, y_train = sample_data
        X_test, y_test = sample_data
        X_full, y_full = sample_data
        future_df = X_train.iloc[:5]  # Use first 5 rows as future data

        quantiles = [0.5, 0.75, 0.9]
        predictions_df, metrics_list = generate_quantile_predictions(
            X_train, y_train, X_test, y_test, X_full, y_full,
            future_df, quantiles, "linear", mock_logger
        )

        # Check predictions DataFrame shape and columns
        assert predictions_df.shape == (5, 3)  # 5 future dates, 3 quantiles
        assert list(predictions_df.columns) == ["P50", "P75", "P90"]

        # Check metrics list
        assert len(metrics_list) == 3
        for i, metric in enumerate(metrics_list):
            assert metric["quantile"] == quantiles[i]
            assert "pinball_loss" in metric
            assert "coverage" in metric
            assert "coverage_error" in metric

    def test_predictions_increase_with_quantile(self, sample_data, mock_logger):
        """Test that predictions generally increase with higher quantiles."""
        X_train, y_train = sample_data
        X_test, y_test = sample_data
        X_full, y_full = sample_data
        future_df = X_train.iloc[:10]

        quantiles = [0.1, 0.5, 0.9]
        predictions_df, _ = generate_quantile_predictions(
            X_train, y_train, X_test, y_test, X_full, y_full,
            future_df, quantiles, "gradient_boosting", mock_logger
        )

        # Generally, P90 >= P50 >= P10 (may not be strict for all rows due to model variance)
        # Check mean values across all predictions
        mean_p10 = predictions_df["P10"].mean()
        mean_p50 = predictions_df["P50"].mean()
        mean_p90 = predictions_df["P90"].mean()

        assert mean_p50 >= mean_p10
        assert mean_p90 >= mean_p50

    def test_generate_with_gradient_boosting(self, sample_data, mock_logger):
        """Test prediction generation with gradient boosting model."""
        X_train, y_train = sample_data
        X_test, y_test = sample_data
        X_full, y_full = sample_data
        future_df = X_train.iloc[:3]

        quantiles = [0.5, 0.75]
        predictions_df, metrics_list = generate_quantile_predictions(
            X_train, y_train, X_test, y_test, X_full, y_full,
            future_df, quantiles, "gradient_boosting", mock_logger
        )

        assert predictions_df.shape == (3, 2)
        assert list(predictions_df.columns) == ["P50", "P75"]
        assert len(metrics_list) == 2


@pytest.mark.unit
class TestSaveQuantilePredictions:
    """Test saving quantile predictions to CSV."""

    def test_save_creates_file(self, temp_dir, mock_logger):
        """Test that save_quantile_predictions creates a CSV file."""
        predictions_df = pd.DataFrame({
            "P50": [100.0, 110.0, 120.0],
            "P75": [120.0, 130.0, 140.0],
            "P90": [140.0, 150.0, 160.0]
        })
        future_dates = pd.date_range("2024-01-01", periods=3, freq="D")
        output_path = os.path.join(temp_dir, "quantile_predictions.csv")

        save_quantile_predictions(predictions_df, future_dates, output_path, mock_logger)

        assert os.path.exists(output_path)

    def test_save_correct_format(self, temp_dir, mock_logger):
        """Test that saved CSV has correct format."""
        predictions_df = pd.DataFrame({
            "P50": [100.0, 110.0],
            "P75": [120.0, 130.0],
            "P90": [140.0, 150.0]
        })
        future_dates = pd.date_range("2024-02-01", periods=2, freq="D")
        output_path = os.path.join(temp_dir, "quantile_predictions.csv")

        save_quantile_predictions(predictions_df, future_dates, output_path, mock_logger)

        # Read back and verify
        df = pd.read_csv(output_path)
        assert list(df.columns) == ["Date", "P50", "P75", "P90"]
        assert len(df) == 2
        assert df["Date"][0] == "01/02/2024"  # DD/MM/YYYY format
        assert df["Date"][1] == "02/02/2024"

    def test_save_preserves_values(self, temp_dir, mock_logger):
        """Test that saved values match input values."""
        predictions_df = pd.DataFrame({
            "P50": [100.5, 110.25],
            "P75": [120.75, 130.5],
            "P90": [140.0, 150.0]
        })
        future_dates = pd.date_range("2024-03-15", periods=2, freq="D")
        output_path = os.path.join(temp_dir, "quantile_predictions.csv")

        save_quantile_predictions(predictions_df, future_dates, output_path, mock_logger)

        # Read back and verify values
        df = pd.read_csv(output_path)
        assert df["P50"][0] == pytest.approx(100.5)
        assert df["P75"][1] == pytest.approx(130.5)
        assert df["P90"][0] == pytest.approx(140.0)


# Fixtures
@pytest.fixture
def sample_data():
    """Generate simple sample data for testing."""
    np.random.seed(42)
    n_samples = 100

    # Create features
    X = pd.DataFrame({
        "feature1": np.random.randn(n_samples),
        "feature2": np.random.randn(n_samples),
        "feature3": np.random.randn(n_samples)
    })

    # Create target with some relationship to features
    y = pd.Series(
        X["feature1"] * 10 + X["feature2"] * 5 + np.random.randn(n_samples) * 2 + 100,
        name="Tran Amt"
    )

    return X, y


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    import logging
    return logging.getLogger("test")
