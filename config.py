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

# Field description constants (to avoid duplication)
_DESC_RANDOM_STATE = "Random seed for reproducibility"
_DESC_MIN_SAMPLES_SPLIT = "Minimum samples required to split an internal node"
_DESC_MIN_SAMPLES_LEAF = "Minimum samples required at a leaf node"


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
    random_state: int = Field(default=42, ge=0, description=_DESC_RANDOM_STATE)
    min_total_samples: int = Field(default=30, ge=1, description="Minimum total samples required for training")
    min_test_samples: int = Field(default=10, ge=1, description="Minimum test samples required after split")


class TargetTransformConfig(BaseModel):
    """Configuration for target variable transformation."""

    model_config = {"strict": True}

    enabled: bool = Field(default=False, description="Enable/disable target variable transformation")
    method: Literal["log1p", "log"] = Field(default="log1p", description="Transformation method (log1p or log)")


class DecisionTreeConfig(BaseModel):
    """Configuration for Decision Tree model hyperparameters."""

    model_config = {"strict": True}

    max_depth: int = Field(default=5, ge=1, description="Maximum depth of the tree")
    min_samples_split: int = Field(default=10, ge=2, description=_DESC_MIN_SAMPLES_SPLIT)
    min_samples_leaf: int = Field(default=5, ge=1, description=_DESC_MIN_SAMPLES_LEAF)
    ccp_alpha: float = Field(default=0.01, ge=0.0, description="Complexity parameter for pruning")
    random_state: int = Field(default=42, ge=0, description=_DESC_RANDOM_STATE)


class RandomForestConfig(BaseModel):
    """Configuration for Random Forest model hyperparameters."""

    model_config = {"strict": True}

    n_estimators: int = Field(default=100, ge=1, description="Number of trees in the forest")
    max_depth: int = Field(default=10, ge=1, description="Maximum depth of each tree")
    min_samples_split: int = Field(default=10, ge=2, description=_DESC_MIN_SAMPLES_SPLIT)
    min_samples_leaf: int = Field(default=5, ge=1, description=_DESC_MIN_SAMPLES_LEAF)
    max_features: str = Field(default="sqrt", description="Number of features to consider for best split")
    ccp_alpha: float = Field(default=0.01, ge=0.0, description="Complexity parameter for pruning")
    random_state: int = Field(default=42, ge=0, description=_DESC_RANDOM_STATE)

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
    min_samples_split: int = Field(default=10, ge=2, description=_DESC_MIN_SAMPLES_SPLIT)
    min_samples_leaf: int = Field(default=5, ge=1, description=_DESC_MIN_SAMPLES_LEAF)
    max_features: str = Field(default="sqrt", description="Number of features to consider for best split")
    random_state: int = Field(default=42, ge=0, description=_DESC_RANDOM_STATE)

    @field_validator("max_features")
    @classmethod
    def validate_max_features(cls, v: str) -> str:
        """Validate max_features is a valid option."""
        valid_options = ["sqrt", "log2", "auto", None]
        if v not in valid_options and not v.replace(".", "").replace("-", "").isdigit():
            raise ValueError(f"max_features must be one of {valid_options} or a number, got '{v}'")
        return v


class DecisionTreeTuningGrid(BaseModel):
    """Constrained tuning grid for Decision Tree."""

    model_config = {"strict": True}

    max_depth: list[int] = Field(default_factory=lambda: [3, 4, 5, 6], min_length=1)
    min_samples_leaf: list[int] = Field(default_factory=lambda: [5, 10, 20], min_length=1)


class RandomForestTuningGrid(BaseModel):
    """Constrained tuning grid for Random Forest."""

    model_config = {"strict": True}

    max_depth: list[int] = Field(default_factory=lambda: [4, 6, 8, 10], min_length=1)
    min_samples_leaf: list[int] = Field(default_factory=lambda: [2, 5, 10], min_length=1)
    subsample: list[float] = Field(default_factory=lambda: [0.6, 0.8, 1.0], min_length=1)

    @field_validator("subsample")
    @classmethod
    def validate_subsample(cls, v: list[float]) -> list[float]:
        """Validate subsample values are in (0, 1]."""
        if any(value <= 0 or value > 1 for value in v):
            raise ValueError("subsample values must be in the (0, 1] range")
        return v


class GradientBoostingTuningGrid(BaseModel):
    """Constrained tuning grid for Gradient Boosting."""

    model_config = {"strict": True}

    max_depth: list[int] = Field(default_factory=lambda: [2, 3, 4, 5], min_length=1)
    min_samples_leaf: list[int] = Field(default_factory=lambda: [5, 10, 20], min_length=1)
    subsample: list[float] = Field(default_factory=lambda: [0.6, 0.8, 1.0], min_length=1)

    @field_validator("subsample")
    @classmethod
    def validate_subsample(cls, v: list[float]) -> list[float]:
        """Validate subsample values are in (0, 1]."""
        if any(value <= 0 or value > 1 for value in v):
            raise ValueError("subsample values must be in the (0, 1] range")
        return v


class TuningConfig(BaseModel):
    """Configuration for constrained hyperparameter tuning."""

    model_config = {"strict": True}

    enabled: bool = Field(default=True, description="Enable constrained hyperparameter tuning")
    time_series_splits: int = Field(default=4, ge=2, description="Number of time-series CV splits")
    top_k_log: int = Field(default=5, ge=1, description="Number of top configurations to log")
    reuse_saved_params: bool = Field(default=True, description="Reuse saved hyperparameters if available")
    persist_path: str = Field(
        default="reports/best_hyperparameters.json",
        description="Relative path under output_dir to persist best hyperparameters",
    )
    decision_tree: DecisionTreeTuningGrid = Field(default_factory=DecisionTreeTuningGrid)
    random_forest: RandomForestTuningGrid = Field(default_factory=RandomForestTuningGrid)
    gradient_boosting: GradientBoostingTuningGrid = Field(default_factory=GradientBoostingTuningGrid)


class BaselinesConfig(BaseModel):
    """Configuration for baseline forecasts."""

    model_config = {"strict": True}

    enabled: bool = True
    rolling_windows_months: list[int] = Field(default_factory=lambda: [3, 6], min_length=1)

    @field_validator("rolling_windows_months")
    @classmethod
    def validate_rolling_windows_months(cls, v: list[int]) -> list[int]:
        """Ensure rolling window sizes are positive integers."""
        if any(window <= 0 for window in v):
            raise ValueError("rolling_windows_months must contain positive integers")
        return v
    

class ProductionConfig(BaseModel):
    """Configuration for production model selection."""

    model_config = {"strict": True}

    default_model: str = Field(
        default="Gradient Boosting",
        description="Default model for production predictions"
    )

    @field_validator("default_model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate that the model name is one of the supported models."""
        valid_models = ["Linear Regression", "Decision Tree", "Random Forest", "Gradient Boosting"]
        if v not in valid_models:
            raise ValueError(f"Invalid model name. Must be one of: {valid_models}")
        return v


class Config(BaseModel):
    """Root configuration model with all sections."""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    data_processing: DataProcessingConfig = Field(default_factory=DataProcessingConfig)
    model_evaluation: ModelEvaluationConfig = Field(default_factory=ModelEvaluationConfig)
    target_transform: TargetTransformConfig = Field(default_factory=TargetTransformConfig)
    decision_tree: DecisionTreeConfig = Field(default_factory=DecisionTreeConfig)
    random_forest: RandomForestConfig = Field(default_factory=RandomForestConfig)
    gradient_boosting: GradientBoostingConfig = Field(default_factory=GradientBoostingConfig)
    tuning: TuningConfig = Field(default_factory=TuningConfig)
    baselines: BaselinesConfig = Field(default_factory=BaselinesConfig)
    production: ProductionConfig = Field(default_factory=ProductionConfig)


# Default configuration (used as fallback if config.yaml is not found or incomplete)
DEFAULT_CONFIG = {
    "logging": {"level": "INFO"},
    "data_processing": {"skiprows": 12},
    "model_evaluation": {"test_size": 0.2, "random_state": 42, "min_total_samples": 30, "min_test_samples": 10},
    "target_transform": {"enabled": False, "method": "log1p"},
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
    "tuning": {
        "enabled": True,
        "time_series_splits": 4,
        "top_k_log": 5,
        "reuse_saved_params": True,
        "persist_path": "reports/best_hyperparameters.json",
        "decision_tree": {"max_depth": [3, 4, 5, 6], "min_samples_leaf": [5, 10, 20]},
        "random_forest": {
            "max_depth": [4, 6, 8, 10],
            "min_samples_leaf": [2, 5, 10],
            "subsample": [0.6, 0.8, 1.0],
        },
        "gradient_boosting": {
            "max_depth": [2, 3, 4, 5],
            "min_samples_leaf": [5, 10, 20],
            "subsample": [0.6, 0.8, 1.0],
        },
    },
    "baselines": {"enabled": True, "rolling_windows_months": [3, 6]},
    "production": {"default_model": "Gradient Boosting"},
}


def _format_validation_error(error: Dict[str, Any]) -> str:
    """
    Format a single Pydantic validation error into a user-friendly message.

    Parameters:
        error (dict): A single error dictionary from Pydantic ValidationError.errors()

    Returns:
        str: A formatted, user-friendly error message
    """
    field_path = ".".join(str(loc) for loc in error["loc"])
    error_type = error["type"]
    error_msg = error["msg"]

    # Create user-friendly error message based on error type
    if "literal_error" in error_type:
        expected = error.get("ctx", {}).get("expected", "")
        return f"Invalid value for '{field_path}': {error_msg} Expected one of: {expected}"
    elif any(keyword in error_type for keyword in ["greater_than", "less_than", "greater_than_equal", "less_than_equal"]):
        return f"Invalid value for '{field_path}': {error_msg}"
    elif "int_parsing" in error_type or "float_parsing" in error_type:
        input_value = error.get("input", "")
        expected_type = "integer" if "int" in error_type else "float"
        return f"Invalid type for '{field_path}': expected {expected_type}, got '{input_value}'"
    else:
        return f"Invalid configuration for '{field_path}': {error_msg}"


def _validate_and_parse_config(merged_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration using Pydantic and return validated dict.

    Parameters:
        merged_config (dict): Merged configuration dictionary

    Returns:
        dict: Validated configuration dictionary

    Raises:
        ConfigurationError: If validation fails with user-friendly error messages
    """
    try:
        validated = Config(**merged_config)
        return validated.model_dump()
    except ValidationError as e:
        # Format all validation errors for better readability
        error_messages = [_format_validation_error(error) for error in e.errors()]
        error_summary = "\n  - ".join(error_messages)
        raise ConfigurationError(f"Configuration validation failed:\n  - {error_summary}") from e


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.yaml file with type validation.

    Returns:
        dict: Configuration dictionary with all parameters.
              Falls back to default values if file is not found.

    Raises:
        ConfigurationError: If configuration validation fails with detailed error messages.
    """
    if not os.path.exists(CONFIG_FILE):
        plog.log_info(None, f"config.yaml not found at {CONFIG_FILE}")
        plog.log_info(None, _DEFAULT_CONFIG_MSG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r") as f:
            raw_config = yaml.safe_load(f)
            merged_config = _merge_configs(DEFAULT_CONFIG, raw_config)
            return _validate_and_parse_config(merged_config)

    except (FileNotFoundError, PermissionError) as e:
        plog.log_error(None, f"Could not access config.yaml: {e}")
        plog.log_info(None, _DEFAULT_CONFIG_MSG)
        return DEFAULT_CONFIG
    except yaml.YAMLError as e:
        plog.log_error(None, f"Invalid YAML in config.yaml: {e}")
        plog.log_info(None, _DEFAULT_CONFIG_MSG)
        return DEFAULT_CONFIG
    except ConfigurationError:
        # Re-raise configuration errors (validation errors with user-friendly messages)
        raise
    except Exception as e:
        plog.log_error(None, f"Unexpected error loading config.yaml: {e}")
        plog.log_error(None, "This is an unexpected error. Please report this issue.")
        raise ConfigurationError(f"Unexpected error loading config.yaml: {e}") from e


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
