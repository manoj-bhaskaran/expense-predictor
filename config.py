"""
Configuration module for Expense Predictor.

This module loads and provides access to configuration parameters from config.yaml.
All configurable parameters (magic numbers, hyperparameters) are centralized here.
"""

import os
from typing import Dict, Any, Optional
import yaml
import python_logging_framework as plog
from exceptions import ConfigurationError

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.yaml')

# Message constants
_DEFAULT_CONFIG_MSG = "Using default configuration."

# Default configuration (used as fallback if config.yaml is not found or incomplete)
DEFAULT_CONFIG = {
    'data_processing': {
        'skiprows': 12
    },
    'model_evaluation': {
        'test_size': 0.2,
        'random_state': 42
    },
    'decision_tree': {
        'max_depth': 5,
        'min_samples_split': 10,
        'min_samples_leaf': 5,
        'ccp_alpha': 0.01,
        'random_state': 42
    },
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 10,
        'min_samples_leaf': 5,
        'max_features': 'sqrt',
        'ccp_alpha': 0.01,
        'random_state': 42
    },
    'gradient_boosting': {
        'n_estimators': 100,
        'learning_rate': 0.1,
        'max_depth': 5,
        'min_samples_split': 10,
        'min_samples_leaf': 5,
        'max_features': 'sqrt',
        'random_state': 42
    }
}


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.yaml file.

    Returns:
        dict: Configuration dictionary with all parameters.
              Falls back to default values if file is not found.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
                # Merge with defaults to ensure all keys exist
                return _merge_configs(DEFAULT_CONFIG, config)
        except (FileNotFoundError, PermissionError) as e:
            # File access issues (permissions, file deleted between check and open)
            plog.log_error(None, f"Could not access config.yaml: {e}")
            plog.log_info(None, _DEFAULT_CONFIG_MSG)
            return DEFAULT_CONFIG
        except yaml.YAMLError as e:
            # Invalid YAML syntax
            plog.log_error(None, f"Invalid YAML in config.yaml: {e}")
            plog.log_info(None, _DEFAULT_CONFIG_MSG)
            return DEFAULT_CONFIG
        except Exception as e:
            # Unexpected errors - log and re-raise to avoid hiding bugs
            plog.log_error(None, f"Unexpected error loading config.yaml: {e}")
            plog.log_error(None, "This is an unexpected error. Please report this issue.")
            raise ConfigurationError(f"Unexpected error loading config.yaml: {e}") from e
    else:
        plog.log_info(None, f"config.yaml not found at {CONFIG_FILE}")
        plog.log_info(None, _DEFAULT_CONFIG_MSG)
        return DEFAULT_CONFIG


def _merge_configs(default: Dict[str, Any], custom: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge custom configuration with default configuration.

    This ensures that if any keys are missing from the custom config,
    the default values are used.

    Parameters:
        default (dict): Default configuration
        custom (dict): Custom configuration from config.yaml

    Returns:
        dict: Merged configuration
    """
    if custom is None:
        return default

    merged = default.copy()
    for key, value in custom.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = _merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged


def get_config() -> Dict[str, Any]:
    """
    Get the configuration dictionary.

    Returns:
        dict: Configuration dictionary with all parameters.
    """
    return load_config()


# Load configuration once when module is imported
config = load_config()
