"""
Custom exception classes for Expense Predictor.

This module defines a hierarchy of custom exceptions for better error handling
and debugging throughout the application. Using specific exceptions instead of
generic ones helps identify the exact nature of errors and makes debugging easier.

Exception Hierarchy:
    ExpensePredictorError (base)
    ├── DataValidationError
    ├── ConfigurationError
    └── ModelTrainingError

Usage:
    from exceptions import DataValidationError, ConfigurationError

    # Raise a specific exception
    if not os.path.exists(file_path):
        raise DataValidationError(f"CSV file not found: {file_path}")

    # Preserve exception context with 'from'
    try:
        config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config.yaml: {e}") from e
"""


class ExpensePredictorError(Exception):
    """
    Base exception class for all Expense Predictor errors.

    All custom exceptions in this application inherit from this base class.
    This allows catching all application-specific errors with a single
    except clause if needed.

    Example:
        try:
            # Application code
            pass
        except ExpensePredictorError as e:
            # Catches all application-specific errors
            logger.error(f"Application error: {e}")
    """
    pass


class DataValidationError(ExpensePredictorError):
    """
    Raised when data validation fails.

    This exception is raised when input data (CSV, Excel, or processed data)
    fails validation checks. Common scenarios include:
    - Missing required files
    - Invalid file formats
    - Missing required columns
    - Invalid data types
    - Corrupted files
    - Invalid date ranges

    Example:
        if not os.path.exists(file_path):
            raise DataValidationError(f"CSV file not found: {file_path}")

        if 'Date' not in df.columns:
            raise DataValidationError("Missing required column: Date")
    """
    pass


class ConfigurationError(ExpensePredictorError):
    """
    Raised when configuration is invalid or cannot be loaded.

    This exception is raised when there are issues with configuration files
    or configuration parameters. Common scenarios include:
    - Invalid YAML syntax in config.yaml
    - Missing required configuration keys
    - Invalid configuration values
    - Permission errors accessing config files

    Example:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config.yaml: {e}") from e

        if config['test_size'] < 0 or config['test_size'] > 1:
            raise ConfigurationError("test_size must be between 0 and 1")
    """
    pass


class ModelTrainingError(ExpensePredictorError):
    """
    Raised when model training fails.

    This exception is raised when there are errors during the model training
    process. Common scenarios include:
    - Insufficient training data
    - Invalid hyperparameters
    - Numerical instability
    - Memory errors during training
    - Feature alignment issues

    Example:
        if len(X_train) < 10:
            raise ModelTrainingError("Insufficient training data: need at least 10 samples")

        try:
            model.fit(X_train, y_train)
        except ValueError as e:
            raise ModelTrainingError(f"Model training failed: {e}") from e
    """
    pass
