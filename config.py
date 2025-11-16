"""
Configuration module for Expense Predictor.

This module loads and provides access to configuration parameters from config.yaml.
All configurable parameters (magic numbers, hyperparameters) are centralized here.
Configuration values are validated using Pydantic for type safety and early error detection.
"""

import os
from typing import Any, Dict, Literal, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

import python_logging_framework as plog
from exceptions import ConfigurationError

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.yaml")

# Message constants
_DEFAULT_CONFIG_MSG = "Using default configuration."


# Pydantic models for configuration validation
class LoggingConfig(BaseModel):
    """Configuration for logging settings."""

    model_config = {"strict": True}

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


class DataProcessingConfig(BaseModel):
    """Configuration for data processing parameters."""

    model_config = {"strict": True}

    skiprows: int = Field(default=12, ge=0, description="Number of rows to skip when reading data files")


class ModelEvaluationConfig(BaseModel):
    """Configuration for model evaluation parameters."""

    model_config = {"strict": True}

    test_size: float = Field(default=0.2, gt=0.0, lt=1.0, description="Fraction of data to use for testing (must be between 0 and 1)")
    random_state: int = Field(default=42, ge=0, description="Random seed for reproducibility")


class DecisionTreeConfig(BaseModel):
    """Configuration for Decision Tree model hyperparameters."""

    model_config = {"strict": True}

    max_depth: int = Field(default=5, ge=1, description="Maximum depth of the tree")
    min_samples_split: int = Field(default=10, ge=2, description="Minimum samples required to split an internal node")
    min_samples_leaf: int = Field(default=5, ge=1, description="Minimum samples required at a leaf node")
    ccp_alpha: float = Field(default=0.01, ge=0.0, description="Complexity parameter for pruning")
    random_state: int = Field(default=42, ge=0, description="Random seed for reproducibility")


class RandomForestConfig(BaseModel):
    """Configuration for Random Forest model hyperparameters."""

    model_config = {"strict": True}

    n_estimators: int = Field(default=100, ge=1, description="Number of trees in the forest")
    max_depth: int = Field(default=10, ge=1, description="Maximum depth of each tree")
    min_samples_split: int = Field(default=10, ge=2, description="Minimum samples required to split an internal node")
    min_samples_leaf: int = Field(default=5, ge=1, description="Minimum samples required at a leaf node")
    max_features: str = Field(default="sqrt", description="Number of features to consider for best split")
    ccp_alpha: float = Field(default=0.01, ge=0.0, description="Complexity parameter for pruning")
    random_state: int = Field(default=42, ge=0, description="Random seed for reproducibility")

    @field_validator("max_features")
    @classmethod
    def validate_max_features(cls, v: str) -> str:
        """Validate max_features is a valid option."""
        valid_options = ["sqrt", "log2", "auto", None]
        if v not in valid_options and not v.replace(".", "").replace("-", "").isdigit():
            raise ValueError(f"max_features must be one of {valid_options} or a number, got '{v}'")
        return v


class GradientBoostingConfig(BaseModel):
    """Configuration for Gradient Boosting model hyperparameters."""

    model_config = {"strict": True}

    n_estimators: int = Field(default=100, ge=1, description="Number of boosting stages")
    learning_rate: float = Field(default=0.1, gt=0.0, le=1.0, description="Learning rate shrinks contribution of each tree")
    max_depth: int = Field(default=5, ge=1, description="Maximum depth of each tree")
    min_samples_split: int = Field(default=10, ge=2, description="Minimum samples required to split an internal node")
    min_samples_leaf: int = Field(default=5, ge=1, description="Minimum samples required at a leaf node")
    max_features: str = Field(default="sqrt", description="Number of features to consider for best split")
    random_state: int = Field(default=42, ge=0, description="Random seed for reproducibility")

    @field_validator("max_features")
    @classmethod
    def validate_max_features(cls, v: str) -> str:
        """Validate max_features is a valid option."""
        valid_options = ["sqrt", "log2", "auto", None]
        if v not in valid_options and not v.replace(".", "").replace("-", "").isdigit():
            raise ValueError(f"max_features must be one of {valid_options} or a number, got '{v}'")
        return v


class Config(BaseModel):
    """Root configuration model with all sections."""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    data_processing: DataProcessingConfig = Field(default_factory=DataProcessingConfig)
    model_evaluation: ModelEvaluationConfig = Field(default_factory=ModelEvaluationConfig)
    decision_tree: DecisionTreeConfig = Field(default_factory=DecisionTreeConfig)
    random_forest: RandomForestConfig = Field(default_factory=RandomForestConfig)
    gradient_boosting: GradientBoostingConfig = Field(default_factory=GradientBoostingConfig)


# Default configuration (used as fallback if config.yaml is not found or incomplete)
DEFAULT_CONFIG = {
    "logging": {"level": "INFO"},
    "data_processing": {"skiprows": 12},
    "model_evaluation": {"test_size": 0.2, "random_state": 42},
    "decision_tree": {"max_depth": 5, "min_samples_split": 10, "min_samples_leaf": 5, "ccp_alpha": 0.01, "random_state": 42},
    "random_forest": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 10,
        "min_samples_leaf": 5,
        "max_features": "sqrt",
        "ccp_alpha": 0.01,
        "random_state": 42,
    },
    "gradient_boosting": {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 5,
        "min_samples_split": 10,
        "min_samples_leaf": 5,
        "max_features": "sqrt",
        "random_state": 42,
    },
}


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.yaml file with type validation.

    Returns:
        dict: Configuration dictionary with all parameters.
              Falls back to default values if file is not found.

    Raises:
        ConfigurationError: If configuration validation fails with detailed error messages.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                raw_config = yaml.safe_load(f)

                # Merge with defaults to ensure all keys exist
                merged_config = _merge_configs(DEFAULT_CONFIG, raw_config)

                # Validate with Pydantic
                try:
                    validated = Config(**merged_config)
                    return validated.model_dump()
                except ValidationError as e:
                    # Format validation errors for better readability
                    error_messages = []
                    for error in e.errors():
                        field_path = ".".join(str(loc) for loc in error["loc"])
                        error_type = error["type"]
                        error_msg = error["msg"]

                        # Create user-friendly error message
                        if "literal_error" in error_type:
                            expected = error.get("ctx", {}).get("expected", "")
                            error_messages.append(f"Invalid value for '{field_path}': {error_msg} Expected one of: {expected}")
                        elif "greater_than" in error_type or "less_than" in error_type or "greater_than_equal" in error_type or "less_than_equal" in error_type:
                            error_messages.append(f"Invalid value for '{field_path}': {error_msg}")
                        elif "int_parsing" in error_type or "float_parsing" in error_type:
                            input_value = error.get("input", "")
                            expected_type = "integer" if "int" in error_type else "float"
                            error_messages.append(f"Invalid type for '{field_path}': expected {expected_type}, got '{input_value}'")
                        else:
                            error_messages.append(f"Invalid configuration for '{field_path}': {error_msg}")

                    error_summary = "\n  - ".join(error_messages)
                    raise ConfigurationError(f"Configuration validation failed:\n  - {error_summary}") from e

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
        except ConfigurationError:
            # Re-raise configuration errors (these are validation errors)
            raise
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
