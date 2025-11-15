"""
Unit tests for config.py module.

This module tests configuration loading and validation.
"""

import os
import pytest
import tempfile
import yaml
from unittest.mock import patch, mock_open

# Import functions to test
from config import load_config, get_config, _merge_configs, DEFAULT_CONFIG
from exceptions import ConfigurationError


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_default_config_when_file_missing(self, monkeypatch):
        """Test loading default config when config.yaml doesn't exist."""
        # Point to non-existent file
        monkeypatch.setattr('config.CONFIG_FILE', '/nonexistent/config.yaml')
        result = load_config()

        assert result == DEFAULT_CONFIG
        assert 'data_processing' in result
        assert 'model_evaluation' in result

    def test_load_config_from_valid_file(self, monkeypatch):
        """Test loading config from a valid YAML file."""
        # Create temp config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            test_config = {
                'data_processing': {'skiprows': 20},
                'model_evaluation': {'test_size': 0.3, 'random_state': 99}
            }
            yaml.dump(test_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr('config.CONFIG_FILE', temp_file)
            result = load_config()

            # Should have merged with defaults
            assert result['data_processing']['skiprows'] == 20
            assert abs(result['model_evaluation']['test_size'] - 0.3) < 0.001
            assert result['model_evaluation']['random_state'] == 99
        finally:
            os.remove(temp_file)

    def test_load_config_with_invalid_yaml(self, monkeypatch):
        """Test loading config with invalid YAML."""
        # Create temp file with invalid YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:\n  - broken")
            temp_file = f.name

        try:
            monkeypatch.setattr('config.CONFIG_FILE', temp_file)
            result = load_config()

            # Should fall back to defaults
            assert result == DEFAULT_CONFIG
        finally:
            os.remove(temp_file)

    def test_load_config_with_partial_config(self, monkeypatch):
        """Test loading partial config merges with defaults."""
        # Create temp config with only some values
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            partial_config = {
                'data_processing': {'skiprows': 15}
                # Missing other sections
            }
            yaml.dump(partial_config, f)
            temp_file = f.name

        try:
            monkeypatch.setattr('config.CONFIG_FILE', temp_file)
            result = load_config()

            # Should have custom value
            assert result['data_processing']['skiprows'] == 15
            # But also defaults for missing sections
            assert 'model_evaluation' in result
            assert 'decision_tree' in result
        finally:
            os.remove(temp_file)

    def test_load_config_with_permission_error(self, monkeypatch):
        """Test that PermissionError falls back to default config."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("data_processing:\n  skiprows: 10")
            temp_file = f.name

        try:
            monkeypatch.setattr('config.CONFIG_FILE', temp_file)

            # Mock open to raise PermissionError
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                result = load_config()

                # Should fall back to defaults
                assert result == DEFAULT_CONFIG
        finally:
            os.remove(temp_file)

    def test_load_config_with_unexpected_error_raises_configuration_error(self, monkeypatch):
        """Test that unexpected errors raise ConfigurationError."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("data_processing:\n  skiprows: 10")
            temp_file = f.name

        try:
            monkeypatch.setattr('config.CONFIG_FILE', temp_file)

            # Mock yaml.safe_load to raise an unexpected exception
            with patch('yaml.safe_load', side_effect=RuntimeError("Unexpected error")):
                with pytest.raises(ConfigurationError) as exc_info:
                    load_config()

                # Check that the error message contains context
                assert "Unexpected error loading config.yaml" in str(exc_info.value)
                # Check that the original exception is preserved
                assert exc_info.value.__cause__ is not None
        finally:
            os.remove(temp_file)


class TestMergeConfigs:
    """Tests for _merge_configs function."""

    def test_merge_with_none(self):
        """Test merging when custom config is None."""
        default = {'key': 'value'}
        result = _merge_configs(default, None)
        assert result == default

    def test_merge_shallow_dict(self):
        """Test merging shallow dictionaries."""
        default = {'a': 1, 'b': 2}
        custom = {'b': 3, 'c': 4}
        result = _merge_configs(default, custom)

        assert result['a'] == 1
        assert result['b'] == 3
        assert result['c'] == 4

    def test_merge_nested_dict(self):
        """Test merging nested dictionaries."""
        default = {
            'section1': {'param1': 10, 'param2': 20},
            'section2': {'param3': 30}
        }
        custom = {
            'section1': {'param1': 100}  # Override one param
        }
        result = _merge_configs(default, custom)

        assert result['section1']['param1'] == 100
        assert result['section1']['param2'] == 20  # Kept from default
        assert result['section2']['param3'] == 30

    def test_merge_preserves_default(self):
        """Test that merging doesn't modify original default."""
        default = {'key': {'nested': 1}}
        custom = {'key': {'nested': 2}}
        result = _merge_configs(default, custom)

        # Original should be unchanged
        assert default['key']['nested'] == 1
        assert result['key']['nested'] == 2


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
            'data_processing',
            'model_evaluation',
            'decision_tree',
            'random_forest',
            'gradient_boosting'
        ]

        for section in required_sections:
            assert section in result


class TestDefaultConfig:
    """Tests for DEFAULT_CONFIG constant."""

    def test_default_config_structure(self):
        """Test DEFAULT_CONFIG has expected structure."""
        assert 'data_processing' in DEFAULT_CONFIG
        assert 'model_evaluation' in DEFAULT_CONFIG
        assert 'decision_tree' in DEFAULT_CONFIG
        assert 'random_forest' in DEFAULT_CONFIG
        assert 'gradient_boosting' in DEFAULT_CONFIG

    def test_default_config_values(self):
        """Test DEFAULT_CONFIG has reasonable default values."""
        assert DEFAULT_CONFIG['data_processing']['skiprows'] == 12
        assert abs(DEFAULT_CONFIG['model_evaluation']['test_size'] - 0.2) < 0.001
        assert DEFAULT_CONFIG['model_evaluation']['random_state'] == 42

        # Check model defaults are positive
        assert DEFAULT_CONFIG['decision_tree']['max_depth'] > 0
        assert DEFAULT_CONFIG['random_forest']['n_estimators'] > 0
        assert DEFAULT_CONFIG['gradient_boosting']['learning_rate'] > 0
