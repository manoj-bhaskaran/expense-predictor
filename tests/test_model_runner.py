"""
Integration tests for model_runner.py module.

This module tests the complete model training and prediction pipeline,
including data loading, preprocessing, model training, and prediction output.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import shutil

# Import main components
from helpers import preprocess_and_append_csv, prepare_future_dates
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.model_selection import train_test_split
from config import config


class TestDataPreprocessingPipeline:
    """Test the full data preprocessing pipeline."""

    def test_preprocess_csv_pipeline(self, sample_csv_path, mock_logger):
        """Test preprocessing CSV data through full pipeline."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Verify data shapes
        assert X is not None
        assert y is not None
        assert df is not None
        assert len(X) == len(y)

        # Verify feature engineering
        assert 'Month' in X.columns
        assert 'Day of the Month' in X.columns

        # Verify no Date or Tran Amt in features
        assert 'Date' not in X.columns
        assert 'Tran Amt' not in X.columns

        # Verify target variable
        assert y.name == 'Tran Amt'

    def test_preprocess_fills_missing_dates(self, temp_dir, mock_logger):
        """Test that preprocessing fills in missing dates with zeros."""
        # Create CSV with gaps in dates
        csv_path = os.path.join(temp_dir, 'gap_dates.csv')
        df = pd.DataFrame({
            'Date': ['01/01/2024', '05/01/2024', '10/01/2024'],  # Gaps between dates
            'Tran Amt': [100.0, 200.0, 300.0]
        })
        df.to_csv(csv_path, index=False)

        X, y, processed_df = preprocess_and_append_csv(csv_path, logger=mock_logger)

        # Should have filled in all dates from first to yesterday
        start_date = datetime(2024, 1, 1)
        end_date = datetime.now() - timedelta(days=1)
        expected_days = (end_date - start_date).days + 1

        assert len(processed_df) == expected_days
        # Missing dates should be filled with 0
        assert (y == 0).sum() > 0  # Some values should be zero

    def test_preprocess_removes_duplicates(self, temp_dir, mock_logger):
        """Test that preprocessing removes duplicate dates (keeps last)."""
        csv_path = os.path.join(temp_dir, 'duplicate_dates.csv')
        df = pd.DataFrame({
            'Date': ['01/01/2024', '01/01/2024', '02/01/2024'],
            'Tran Amt': [100.0, 200.0, 150.0]  # Duplicate date with different amounts
        })
        df.to_csv(csv_path, index=False)

        X, y, processed_df = preprocess_and_append_csv(csv_path, logger=mock_logger)

        # Check that duplicate was removed and last value was kept
        # The processed dataframe will have many rows due to date filling
        # But the original date should have the last value (200.0)
        jan_1_value = processed_df[processed_df['Date'] == '2024-01-01']['Tran Amt'].iloc[0]
        assert jan_1_value == 200.0


class TestModelTrainingPipeline:
    """Test model training functionality."""

    def test_linear_regression_training(self, sample_csv_path, mock_logger):
        """Test Linear Regression model training."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Train model
        model = LinearRegression()
        model.fit(X, y)

        # Make predictions
        y_pred = model.predict(X)

        # Verify predictions exist and have correct shape
        assert y_pred is not None
        assert len(y_pred) == len(y)
        assert not np.isnan(y_pred).any()

    def test_decision_tree_training(self, sample_csv_path, mock_logger):
        """Test Decision Tree model training with config parameters."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Train model with config parameters
        model = DecisionTreeRegressor(
            max_depth=config['decision_tree']['max_depth'],
            min_samples_split=config['decision_tree']['min_samples_split'],
            min_samples_leaf=config['decision_tree']['min_samples_leaf'],
            random_state=config['decision_tree']['random_state']
        )
        model.fit(X, y)

        # Make predictions
        y_pred = model.predict(X)

        # Verify predictions
        assert y_pred is not None
        assert len(y_pred) == len(y)

    def test_random_forest_training(self, sample_csv_path, mock_logger):
        """Test Random Forest model training with config parameters."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Train model
        model = RandomForestRegressor(
            n_estimators=config['random_forest']['n_estimators'],
            max_depth=config['random_forest']['max_depth'],
            random_state=config['random_forest']['random_state']
        )
        model.fit(X, y)

        # Make predictions
        y_pred = model.predict(X)

        # Verify predictions
        assert y_pred is not None
        assert len(y_pred) == len(y)

    def test_gradient_boosting_training(self, sample_csv_path, mock_logger):
        """Test Gradient Boosting model training with config parameters."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Train model
        model = GradientBoostingRegressor(
            n_estimators=config['gradient_boosting']['n_estimators'],
            learning_rate=config['gradient_boosting']['learning_rate'],
            max_depth=config['gradient_boosting']['max_depth'],
            random_state=config['gradient_boosting']['random_state']
        )
        model.fit(X, y)

        # Make predictions
        y_pred = model.predict(X)

        # Verify predictions
        assert y_pred is not None
        assert len(y_pred) == len(y)


class TestTrainTestSplit:
    """Test train/test split functionality."""

    def test_train_test_split_ratio(self, sample_csv_path, mock_logger):
        """Test that train/test split uses correct ratio from config."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        test_size = config['model_evaluation']['test_size']
        random_state = config['model_evaluation']['random_state']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False, random_state=random_state
        )

        # Check split sizes (allow for rounding differences)
        total_size = len(X)
        test_ratio = len(X_test) / total_size

        # Test size should be approximately equal to configured test_size
        assert abs(test_ratio - test_size) < 0.01  # Within 1%
        assert len(X_train) + len(X_test) == total_size

    def test_train_test_split_temporal_order(self, sample_csv_path, mock_logger):
        """Test that split preserves temporal order (shuffle=False)."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        test_size = config['model_evaluation']['test_size']
        random_state = config['model_evaluation']['random_state']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False, random_state=random_state
        )

        # Verify indices are sequential (train comes before test)
        assert X_train.index[-1] < X_test.index[0]


class TestModelEvaluation:
    """Test model evaluation metrics."""

    def test_evaluation_metrics_calculation(self, sample_csv_path, mock_logger):
        """Test that evaluation metrics are calculated correctly."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Train simple model
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)

        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)

        # Verify metrics are valid
        assert rmse >= 0
        assert mae >= 0
        assert -1 <= r2 <= 1  # R² can be negative for very bad models
        assert not np.isnan(rmse)
        assert not np.isnan(mae)
        assert not np.isnan(r2)

    def test_metrics_on_train_and_test_sets(self, sample_csv_path, mock_logger):
        """Test metrics calculation on both train and test sets."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        test_size = config['model_evaluation']['test_size']
        random_state = config['model_evaluation']['random_state']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False, random_state=random_state
        )

        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict on both sets
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        # Calculate train metrics
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_r2 = r2_score(y_train, y_train_pred)

        # Calculate test metrics
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_r2 = r2_score(y_test, y_test_pred)

        # Verify all metrics are valid
        assert train_rmse >= 0 and test_rmse >= 0
        assert train_mae >= 0 and test_mae >= 0
        assert not np.isnan(train_r2) and not np.isnan(test_r2)


class TestFuturePredictionPipeline:
    """Test the future prediction generation pipeline."""

    def test_future_prediction_generation(self, sample_csv_path, mock_logger):
        """Test complete future prediction pipeline."""
        # Load and preprocess data
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Train model
        model = LinearRegression()
        model.fit(X, y)

        # Prepare future dates
        custom_date = (datetime.now() + timedelta(days=30)).strftime("%d-%m-%Y")
        future_df, future_dates = prepare_future_dates(custom_date)

        # Align features
        future_df_aligned = future_df.reindex(columns=X.columns, fill_value=0)

        # Make predictions
        y_predict = model.predict(future_df_aligned)

        # Verify predictions
        assert y_predict is not None
        assert len(y_predict) == len(future_dates)
        assert not np.isnan(y_predict).any()

    def test_prediction_output_format(self, sample_csv_path, mock_logger):
        """Test that prediction output has correct format."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Train model
        model = LinearRegression()
        model.fit(X, y)

        # Prepare future dates
        custom_date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")
        future_df, future_dates = prepare_future_dates(custom_date)
        future_df_aligned = future_df.reindex(columns=X.columns, fill_value=0)

        # Make predictions
        y_predict = model.predict(future_df_aligned)
        y_predict = np.round(y_predict, 2)

        # Create output DataFrame
        predicted_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted Tran Amt': y_predict
        })

        # Verify format
        assert 'Date' in predicted_df.columns
        assert 'Predicted Tran Amt' in predicted_df.columns
        assert len(predicted_df) == len(future_dates)

        # Verify rounding to 2 decimal places
        for value in predicted_df['Predicted Tran Amt']:
            decimal_places = len(str(value).split('.')[-1]) if '.' in str(value) else 0
            assert decimal_places <= 2

    def test_feature_alignment(self, sample_csv_path, mock_logger):
        """Test that future features are correctly aligned with training features."""
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # Prepare future dates
        future_df, future_dates = prepare_future_dates()

        # Align features
        future_df_aligned = future_df.reindex(columns=X.columns, fill_value=0)

        # Verify all training columns exist in future data
        assert set(X.columns) == set(future_df_aligned.columns)

        # Verify column order is the same
        assert list(X.columns) == list(future_df_aligned.columns)


class TestFullEndToEndPipeline:
    """Test the complete end-to-end pipeline."""

    def test_complete_pipeline(self, sample_csv_path, temp_dir, mock_logger):
        """Test complete pipeline from CSV to prediction output."""
        # 1. Load and preprocess data
        X, y, df = preprocess_and_append_csv(sample_csv_path, logger=mock_logger)

        # 2. Split data
        test_size = config['model_evaluation']['test_size']
        random_state = config['model_evaluation']['random_state']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False, random_state=random_state
        )

        # 3. Train model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # 4. Evaluate on test set
        y_test_pred = model.predict(X_test)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        assert test_rmse >= 0

        # 5. Retrain on full dataset
        model.fit(X, y)

        # 6. Prepare future dates
        custom_date = (datetime.now() + timedelta(days=14)).strftime("%d-%m-%Y")
        future_df, future_dates = prepare_future_dates(custom_date)

        # 7. Make future predictions
        future_df_aligned = future_df.reindex(columns=X.columns, fill_value=0)
        y_predict = model.predict(future_df_aligned)
        y_predict = np.round(y_predict, 2)

        # 8. Create output
        predicted_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted Tran Amt': y_predict
        })

        # 9. Save to file
        output_path = os.path.join(temp_dir, 'test_predictions.csv')
        predicted_df.to_csv(output_path, index=False)

        # 10. Verify output file
        assert os.path.exists(output_path)
        result_df = pd.read_csv(output_path)
        assert len(result_df) == len(future_dates)
        assert 'Date' in result_df.columns
        assert 'Predicted Tran Amt' in result_df.columns


class TestConfigIntegration:
    """Test integration with configuration system."""

    def test_config_parameters_loaded(self):
        """Test that config parameters are loaded correctly."""
        # Verify data processing config
        assert 'data_processing' in config
        assert 'skiprows' in config['data_processing']

        # Verify model evaluation config
        assert 'model_evaluation' in config
        assert 'test_size' in config['model_evaluation']
        assert 'random_state' in config['model_evaluation']

        # Verify model configs
        assert 'decision_tree' in config
        assert 'random_forest' in config
        assert 'gradient_boosting' in config

    def test_config_values_valid(self):
        """Test that config values are within valid ranges."""
        # Test size should be between 0 and 1
        assert 0 < config['model_evaluation']['test_size'] < 1

        # Random state should be non-negative
        assert config['model_evaluation']['random_state'] >= 0

        # Model parameters should be positive
        assert config['random_forest']['n_estimators'] > 0
        assert config['gradient_boosting']['learning_rate'] > 0
