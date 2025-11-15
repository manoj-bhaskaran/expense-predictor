"""
Security utilities for the Expense Predictor application.

This module provides functions for:
- Path validation and sanitization to prevent path injection attacks
- File extension validation
- CSV injection prevention
- Backup creation before file modifications
"""

import os
from pathlib import Path
from typing import Optional, Any
import shutil
import logging
import pandas as pd
import python_logging_framework as plog


# Allowed file extensions
ALLOWED_CSV_EXTENSIONS = ['.csv']
ALLOWED_EXCEL_EXTENSIONS = ['.xls', '.xlsx']
ALLOWED_DATA_EXTENSIONS = ALLOWED_CSV_EXTENSIONS + ALLOWED_EXCEL_EXTENSIONS


def validate_and_resolve_path(
    path_str: str,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_dir: bool = False,
    allowed_extensions: Optional[list] = None,
    logger: Optional[logging.Logger] = None
) -> Path:
    """
    Validate and resolve a file system path to prevent path injection attacks.

    This function:
    - Resolves relative paths to absolute paths
    - Normalizes path separators
    - Detects path traversal attempts (../)
    - Validates file extensions if specified
    - Checks existence and type if required

    Parameters:
    path_str (str): The path string to validate
    must_exist (bool): If True, path must exist
    must_be_file (bool): If True, path must be a file
    must_be_dir (bool): If True, path must be a directory
    allowed_extensions (list, optional): List of allowed file extensions (e.g., ['.csv', '.xls'])
    logger (logging.Logger, optional): Logger instance for logging messages

    Returns:
    Path: A validated and resolved pathlib.Path object

    Raises:
    ValueError: If the path is invalid or fails validation checks
    FileNotFoundError: If must_exist=True and path doesn't exist
    """
    if not path_str or not isinstance(path_str, str):
        plog.log_error(logger, "Path must be a non-empty string")
        raise ValueError("Path must be a non-empty string")

    # Strip whitespace and quotes
    path_str = path_str.strip().strip('"').strip("'")

    try:
        # Convert to Path object and resolve to absolute path
        path = Path(path_str).resolve()
    except (ValueError, OSError) as e:
        plog.log_error(logger, f"Invalid path format: {path_str} - {e}")
        raise ValueError(f"Invalid path format: {path_str}")

    # Security check: Detect suspicious path patterns
    path_parts = str(path).split(os.sep)
    if '..' in path_parts:
        plog.log_error(logger, f"Path traversal detected in path: {path_str}")
        raise ValueError(f"Path traversal detected: {path_str}")

    # Check if path exists (if required)
    if must_exist and not path.exists():
        plog.log_error(logger, f"Path does not exist: {path}")
        raise FileNotFoundError(f"Path does not exist: {path}")

    # Check if path is a file (if required)
    if must_be_file:
        if path.exists() and not path.is_file():
            plog.log_error(logger, f"Path is not a file: {path}")
            raise ValueError(f"Path is not a file: {path}")

    # Check if path is a directory (if required)
    if must_be_dir:
        if path.exists() and not path.is_dir():
            plog.log_error(logger, f"Path is not a directory: {path}")
            raise ValueError(f"Path is not a directory: {path}")

    # Validate file extension (if specified)
    if allowed_extensions:
        ext = path.suffix.lower()
        if ext not in allowed_extensions:
            plog.log_error(logger, f"Invalid file extension: {ext}. Allowed: {allowed_extensions}")
            raise ValueError(f"Invalid file extension: {ext}. Allowed extensions: {allowed_extensions}")

    plog.log_info(logger, f"Path validated successfully: {path}")
    return path


def validate_file_path(
    path_str: str,
    allowed_extensions: Optional[list] = None,
    must_exist: bool = True,
    logger: Optional[logging.Logger] = None
) -> Path:
    """
    Validate a file path with extension checking.

    Parameters:
    path_str (str): The file path to validate
    allowed_extensions (list, optional): List of allowed file extensions
    must_exist (bool): If True, file must exist
    logger (logging.Logger, optional): Logger instance for logging messages

    Returns:
    Path: A validated and resolved pathlib.Path object

    Raises:
    ValueError: If the path is invalid or has wrong extension
    FileNotFoundError: If must_exist=True and file doesn't exist
    """
    return validate_and_resolve_path(
        path_str,
        must_exist=must_exist,
        must_be_file=must_exist,  # Only check if file when must_exist is True
        allowed_extensions=allowed_extensions,
        logger=logger
    )


def validate_directory_path(
    path_str: str,
    must_exist: bool = False,
    create_if_missing: bool = False,
    logger: Optional[logging.Logger] = None
) -> Path:
    """
    Validate a directory path and optionally create it.

    Parameters:
    path_str (str): The directory path to validate
    must_exist (bool): If True, directory must exist
    create_if_missing (bool): If True, create directory if it doesn't exist
    logger (logging.Logger, optional): Logger instance for logging messages

    Returns:
    Path: A validated and resolved pathlib.Path object

    Raises:
    ValueError: If the path is invalid
    FileNotFoundError: If must_exist=True and directory doesn't exist
    """
    path = validate_and_resolve_path(
        path_str,
        must_exist=False,  # We'll handle existence separately
        must_be_dir=must_exist,
        logger=logger
    )

    if create_if_missing and not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
            plog.log_info(logger, f"Created directory: {path}")
        except OSError as e:
            plog.log_error(logger, f"Failed to create directory {path}: {e}")
            raise ValueError(f"Failed to create directory {path}: {e}")
    elif must_exist and not path.exists():
        plog.log_error(logger, f"Directory does not exist: {path}")
        raise FileNotFoundError(f"Directory does not exist: {path}")

    return path


def sanitize_csv_value(value: Any) -> str:
    """
    Sanitize a value before writing to CSV to prevent CSV injection attacks.

    CSV injection occurs when a formula (starting with =, +, -, @, tab, or carriage return)
    is injected into a CSV field and executed by spreadsheet applications.

    Parameters:
    value: The value to sanitize (can be any type)

    Returns:
    str: The sanitized value safe for CSV output
    """
    if value is None:
        return ''

    # Convert to string
    value_str = str(value)

    # Check for potentially dangerous formula characters at the start
    dangerous_chars = ['=', '+', '-', '@', '\t', '\r', '\n']

    if value_str and value_str[0] in dangerous_chars:
        # Prefix with single quote to prevent formula execution
        # This is a standard CSV injection mitigation technique
        return "'" + value_str

    return value_str


def sanitize_dataframe_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sanitize all values in a DataFrame before writing to CSV.

    This function applies CSV injection prevention to all DataFrame values
    by prefixing potential formula characters with a single quote.

    Parameters:
    df (pd.DataFrame): The DataFrame to sanitize

    Returns:
    pd.DataFrame: A sanitized copy of the DataFrame
    """

    # Create a copy to avoid modifying the original
    df_sanitized = df.copy()

    # Apply sanitization to all columns
    for col in df_sanitized.columns:
        df_sanitized[col] = df_sanitized[col].apply(sanitize_csv_value)

    return df_sanitized


def create_backup(file_path: str, logger: Optional[logging.Logger] = None) -> Optional[str]:
    """
    Create a backup of a file before modifying it.

    The backup file will have a .backup extension and timestamp.

    Parameters:
    file_path (str): Path to the file to backup
    logger (logging.Logger, optional): Logger instance for logging messages

    Returns:
    str: Path to the backup file, or None if file doesn't exist

    Raises:
    IOError: If backup creation fails
    """
    path = Path(file_path)

    if not path.exists():
        plog.log_info(logger, f"No existing file to backup: {file_path}")
        return None

    # Create backup filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = path.with_suffix(f'{path.suffix}.backup_{timestamp}')

    try:
        shutil.copy2(file_path, backup_path)
        plog.log_info(logger, f"Backup created: {backup_path}")
        return str(backup_path)
    except (IOError, OSError) as e:
        plog.log_error(logger, f"Failed to create backup of {file_path}: {e}")
        raise IOError(f"Failed to create backup of {file_path}: {e}")


def confirm_overwrite(file_path: str, logger: Optional[logging.Logger] = None) -> bool:
    """
    Ask user for confirmation before overwriting a file.

    Parameters:
    file_path (str): Path to the file that will be overwritten
    logger (logging.Logger, optional): Logger instance for logging messages

    Returns:
    bool: True if user confirms, False otherwise
    """
    path = Path(file_path)

    if not path.exists():
        # File doesn't exist, no need to confirm
        return True

    plog.log_info(logger, f"File exists: {file_path}")

    # Prompt user for confirmation
    try:
        response = input(f"File '{file_path}' already exists. Overwrite? [y/N]: ").strip().lower()
        confirmed = response in ['y', 'yes']

        if confirmed:
            plog.log_info(logger, f"User confirmed overwrite of {file_path}")
        else:
            plog.log_info(logger, f"User declined overwrite of {file_path}")

        return confirmed
    except (EOFError, KeyboardInterrupt):
        plog.log_info(logger, "User cancelled operation")
        return False
