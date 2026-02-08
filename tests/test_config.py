"""
Unit tests for config.py module.

This module tests configuration loading and validation.
"""

import os
import tempfile
from unittest.mock import mock_open, patch

import pytest
import yaml

# Import functions to test
from config import DEFAULT_CONFIG, _merge_configs, get_config, load_config
from exceptions import ConfigurationError


@pytest.mark.unit
class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_default_config_when_file_missing(self, monkeypatch):
        """Test loading default config when config.yaml doesn't exist."""
        # Point to non-existent file
        monkeypatch.setattr("config.CONFIG_FILE", "/nonexistent/config.yaml")
        result = load_config()

        assert result == DEFAULT_CONFIG
        assert "data_processing" in result
        assert "model_evaluation" in result

    def test_load_config_from_valid_file(self, monkeypatch):
        """Test loading config from a valid YAML file."""
        # Create temp config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            test_config = {"data_processing": {"skiprows": 20}, "model_evaluation": {"test_size": 0.3, "random_state": 99}}
            yaml.dump(test_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            result = load_config()

            # Should have merged with defaults
            assert result["data_processing"]["skiprows"] == 20
            assert abs(result["model_evaluation"]["test_size"] - 0.3) < 0.001
            assert result["model_evaluation"]["random_state"] == 99
        finally:
            os.remove(temp_file)

    def test_load_config_with_invalid_yaml(self, monkeypatch):
        """Test loading config with invalid YAML."""
        # Create temp file with invalid YAML
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content:\n  - broken")
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            result = load_config()

            # Should fall back to defaults
            assert result == DEFAULT_CONFIG
        finally:
            os.remove(temp_file)

    def test_load_config_with_partial_config(self, monkeypatch):
        """Test loading partial config merges with defaults."""
        # Create temp config with only some values
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            partial_config = {
                "data_processing": {"skiprows": 15}
                # Missing other sections
            }
            yaml.dump(partial_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            result = load_config()

            # Should have custom value
            assert result["data_processing"]["skiprows"] == 15
            # But also defaults for missing sections
            assert "model_evaluation" in result
            assert "decision_tree" in result
        finally:
            os.remove(temp_file)

    def test_load_config_with_permission_error(self, monkeypatch):
        """Test that PermissionError falls back to default config."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("data_processing:\n  skiprows: 10")
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)

            # Mock open to raise PermissionError
            with patch("builtins.open", side_effect=PermissionError("Access denied")):
                result = load_config()

                # Should fall back to defaults
                assert result == DEFAULT_CONFIG
        finally:
            os.remove(temp_file)

    def test_load_config_with_unexpected_error_raises_configuration_error(self, monkeypatch):
        """Test that unexpected errors raise ConfigurationError."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("data_processing:\n  skiprows: 10")
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)

            # Mock yaml.safe_load to raise an unexpected exception
            with patch("yaml.safe_load", side_effect=RuntimeError("Unexpected error")):
                with pytest.raises(ConfigurationError) as exc_info:
                    load_config()

                # Check that the error message contains context
                assert "Unexpected error loading config.yaml" in str(exc_info.value)
                # Check that the original exception is preserved
                assert exc_info.value.__cause__ is not None
        finally:
            os.remove(temp_file)


@pytest.mark.unit
class TestMergeConfigs:
    """Tests for _merge_configs function."""

    def test_merge_with_none(self):
        """Test merging when custom config is None."""
        default = {"key": "value"}
        result = _merge_configs(default, None)
        assert result == default

    def test_merge_shallow_dict(self):
        """Test merging shallow dictionaries."""
        default = {"a": 1, "b": 2}
        custom = {"b": 3, "c": 4}
        result = _merge_configs(default, custom)

        assert result["a"] == 1
        assert result["b"] == 3
        assert result["c"] == 4

    def test_merge_nested_dict(self):
        """Test merging nested dictionaries."""
        default = {"section1": {"param1": 10, "param2": 20}, "section2": {"param3": 30}}
        custom = {"section1": {"param1": 100}}  # Override one param
        result = _merge_configs(default, custom)

        assert result["section1"]["param1"] == 100
        assert result["section1"]["param2"] == 20  # Kept from default
        assert result["section2"]["param3"] == 30

    def test_merge_preserves_default(self):
        """Test that merging doesn't modify original default."""
        default = {"key": {"nested": 1}}
        custom = {"key": {"nested": 2}}
        result = _merge_configs(default, custom)

        # Original should be unchanged
        assert default["key"]["nested"] == 1
        assert result["key"]["nested"] == 2


@pytest.mark.unit
class TestGetConfig:
    """Tests for get_config function."""

    def test_get_config_returns_dict(self):
        """Test that get_config returns a dictionary."""
        result = get_config()
        assert isinstance(result, dict)

    def test_get_config_has_required_sections(self):
        """Test that config has all required sections."""
        result = get_config()

        required_sections = [
            "data_processing",
            "model_evaluation",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "tuning",
        ]

        for section in required_sections:
            assert section in result


@pytest.mark.unit
class TestDefaultConfig:
    """Tests for DEFAULT_CONFIG constant."""

    def test_default_config_structure(self):
        """Test DEFAULT_CONFIG has expected structure."""
        assert "data_processing" in DEFAULT_CONFIG
        assert "model_evaluation" in DEFAULT_CONFIG
        assert "decision_tree" in DEFAULT_CONFIG
        assert "random_forest" in DEFAULT_CONFIG
        assert "gradient_boosting" in DEFAULT_CONFIG
        assert "tuning" in DEFAULT_CONFIG

    def test_default_config_values(self):
        """Test DEFAULT_CONFIG has reasonable default values."""
        assert DEFAULT_CONFIG["data_processing"]["skiprows"] == 12
        assert abs(DEFAULT_CONFIG["model_evaluation"]["test_size"] - 0.2) < 0.001
        assert DEFAULT_CONFIG["model_evaluation"]["random_state"] == 42

        # Check model defaults are positive
        assert DEFAULT_CONFIG["decision_tree"]["max_depth"] > 0
        assert DEFAULT_CONFIG["random_forest"]["n_estimators"] > 0
        assert DEFAULT_CONFIG["gradient_boosting"]["learning_rate"] > 0


@pytest.mark.unit
class TestConfigValidation:
    """Tests for configuration validation using Pydantic."""

    def test_valid_config_passes_validation(self, monkeypatch):
        """Test that a valid config passes validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            valid_config = {
                "logging": {"level": "DEBUG"},
                "data_processing": {"skiprows": 10},
                "model_evaluation": {"test_size": 0.3, "random_state": 99},
                "decision_tree": {"max_depth": 10, "min_samples_split": 5, "min_samples_leaf": 2, "ccp_alpha": 0.0, "random_state": 42},
            }
            yaml.dump(valid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            result = load_config()

            # Should load successfully without errors
            assert result["logging"]["level"] == "DEBUG"
            assert result["data_processing"]["skiprows"] == 10
            assert abs(result["model_evaluation"]["test_size"] - 0.3) < 0.001
        finally:
            os.remove(temp_file)

    def test_invalid_logging_level(self, monkeypatch):
        """Test that invalid logging level raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"logging": {"level": "TRACE"}}  # Invalid level
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message is informative
            error_msg = str(exc_info.value)
            assert "logging.level" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_invalid_test_size_type(self, monkeypatch):
        """Test that non-numeric test_size raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"model_evaluation": {"test_size": "0.2"}}  # String instead of float
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message mentions type issue
            error_msg = str(exc_info.value)
            assert "model_evaluation.test_size" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_test_size_out_of_range_high(self, monkeypatch):
        """Test that test_size > 1.0 raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"model_evaluation": {"test_size": 2.0}}  # Out of range
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message mentions range issue
            error_msg = str(exc_info.value)
            assert "model_evaluation.test_size" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_test_size_out_of_range_low(self, monkeypatch):
        """Test that test_size <= 0.0 raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"model_evaluation": {"test_size": 0.0}}  # Out of range
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message mentions range issue
            error_msg = str(exc_info.value)
            assert "model_evaluation.test_size" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_invalid_max_depth_type(self, monkeypatch):
        """Test that non-int max_depth raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"decision_tree": {"max_depth": "five"}}  # String instead of int
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message mentions type issue
            error_msg = str(exc_info.value)
            assert "decision_tree.max_depth" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_invalid_max_depth_value(self, monkeypatch):
        """Test that max_depth < 1 raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"decision_tree": {"max_depth": 0}}  # Must be >= 1
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message mentions validation issue
            error_msg = str(exc_info.value)
            assert "decision_tree.max_depth" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_invalid_min_samples_split(self, monkeypatch):
        """Test that min_samples_split < 2 raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"decision_tree": {"min_samples_split": 1}}  # Must be >= 2
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message
            error_msg = str(exc_info.value)
            assert "decision_tree.min_samples_split" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_invalid_learning_rate_out_of_range(self, monkeypatch):
        """Test that learning_rate > 1.0 raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"gradient_boosting": {"learning_rate": 1.5}}  # Must be <= 1.0
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message
            error_msg = str(exc_info.value)
            assert "gradient_boosting.learning_rate" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_invalid_negative_skiprows(self, monkeypatch):
        """Test that negative skiprows raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"data_processing": {"skiprows": -5}}  # Must be >= 0
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message
            error_msg = str(exc_info.value)
            assert "data_processing.skiprows" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_invalid_random_state_negative(self, monkeypatch):
        """Test that negative random_state raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {"model_evaluation": {"random_state": -1}}  # Must be >= 0
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check error message
            error_msg = str(exc_info.value)
            assert "model_evaluation.random_state" in error_msg
            assert "validation failed" in error_msg.lower()
        finally:
            os.remove(temp_file)

    def test_multiple_validation_errors(self, monkeypatch):
        """Test that multiple validation errors are all reported."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            invalid_config = {
                "logging": {"level": "TRACE"},  # Invalid
                "model_evaluation": {"test_size": 2.0},  # Out of range
                "decision_tree": {"max_depth": "five"},  # Wrong type
            }
            yaml.dump(invalid_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr("config.CONFIG_FILE", temp_file)
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

            # Check that multiple errors are reported
            error_msg = str(exc_info.value)
            assert "validation failed" in error_msg.lower()
            # At least one error should be mentioned
            assert "logging.level" in error_msg or "model_evaluation.test_size" in error_msg or "decision_tree.max_depth" in error_msg
        finally:
            os.remove(temp_file)

    def test_valid_max_features_values(self, monkeypatch):
        """Test that valid max_features values pass validation."""
        valid_values = ["sqrt", "log2", "auto"]

        for value in valid_values:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                valid_config = {"random_forest": {"max_features": value}}
                yaml.dump(valid_config, f)
                temp_file = f.name

            try:
                monkeypatch.setattr("config.CONFIG_FILE", temp_file)
                result = load_config()
                assert result["random_forest"]["max_features"] == value
            finally:
                os.remove(temp_file)
