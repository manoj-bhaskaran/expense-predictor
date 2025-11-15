"""
Unit tests for python_logging_framework module.

This module tests logging initialization and utility functions.
"""

import logging
import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import functions to test
import python_logging_framework as plog


class TestInitialiseLogger:
    """Tests for initialise_logger function."""

    def test_initialise_logger_default_params(self):
        """Test logger initialization with default parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = plog.initialise_logger('test_script', log_dir=temp_dir)

            assert logger is not None
            assert isinstance(logger, logging.Logger)
            assert logger.name == 'test_script'
            assert logger.level == logging.INFO
            assert len(logger.handlers) == 2  # File and console handlers

    def test_initialise_logger_custom_log_level(self):
        """Test logger initialization with custom log level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = plog.initialise_logger('test_custom_level', log_dir=temp_dir, log_level=logging.DEBUG)

            assert logger.level == logging.DEBUG
            # Check that handlers also have the custom level
            for handler in logger.handlers:
                assert handler.level == logging.DEBUG

    def test_initialise_logger_creates_log_directory(self):
        """Test that logger creates log directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_base:
            log_dir = os.path.join(temp_base, 'new_logs')
            assert not os.path.exists(log_dir)

            _ = plog.initialise_logger('test_script', log_dir=log_dir)

            assert os.path.exists(log_dir)
            assert os.path.isdir(log_dir)

    def test_initialise_logger_creates_log_file(self):
        """Test that logger creates a log file in the specified directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _ = plog.initialise_logger('test_logfile', log_dir=temp_dir)

            # Find log files in the directory
            log_files = [f for f in os.listdir(temp_dir) if f.startswith('test_logfile_')]
            assert len(log_files) == 1
            assert log_files[0].endswith('.log')

    def test_initialise_logger_no_duplicate_handlers(self):
        """Test that calling initialise_logger twice doesn't add duplicate handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger1 = plog.initialise_logger('test_script', log_dir=temp_dir)
            initial_handler_count = len(logger1.handlers)

            logger2 = plog.initialise_logger('test_script', log_dir=temp_dir)

            # Should return the same logger without adding new handlers
            assert logger1 is logger2
            assert len(logger2.handlers) == initial_handler_count

    def test_initialise_logger_handler_types(self):
        """Test that logger has both FileHandler and StreamHandler."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = plog.initialise_logger('test_script', log_dir=temp_dir)

            handler_types = [type(h).__name__ for h in logger.handlers]
            assert 'FileHandler' in handler_types
            assert 'StreamHandler' in handler_types

    def test_initialise_logger_formatter(self):
        """Test that logger handlers have proper formatting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = plog.initialise_logger('test_script', log_dir=temp_dir)

            for handler in logger.handlers:
                formatter = handler.formatter
                assert formatter is not None
                # Check that format string includes expected components
                format_string = formatter._fmt
                assert '%(asctime)s' in format_string
                assert '%(name)s' in format_string
                assert '%(levelname)s' in format_string
                assert '%(message)s' in format_string


class TestLogInfo:
    """Tests for log_info function."""

    def test_log_info_with_logger(self):
        """Test log_info with a valid logger."""
        logger = MagicMock(spec=logging.Logger)
        message = "Test info message"

        plog.log_info(logger, message)

        logger.info.assert_called_once_with(message)

    def test_log_info_without_logger(self, capsys):
        """Test log_info without a logger (prints to stdout)."""
        message = "Test info message"

        plog.log_info(None, message)

        captured = capsys.readouterr()
        assert f"INFO: {message}" in captured.out

    def test_log_info_with_logger_none(self, capsys):
        """Test log_info with None logger falls back to print."""
        message = "Test message"

        plog.log_info(None, message)

        captured = capsys.readouterr()
        assert f"INFO: {message}" in captured.out


class TestLogError:
    """Tests for log_error function."""

    def test_log_error_with_logger(self):
        """Test log_error with a valid logger."""
        logger = MagicMock(spec=logging.Logger)
        message = "Test error message"

        plog.log_error(logger, message)

        logger.error.assert_called_once_with(message)

    def test_log_error_without_logger(self, capsys):
        """Test log_error without a logger (prints to stdout)."""
        message = "Test error message"

        plog.log_error(None, message)

        captured = capsys.readouterr()
        assert f"ERROR: {message}" in captured.out

    def test_log_error_with_logger_none(self, capsys):
        """Test log_error with None logger falls back to print."""
        message = "Test error"

        plog.log_error(None, message)

        captured = capsys.readouterr()
        assert f"ERROR: {message}" in captured.out


class TestLogWarning:
    """Tests for log_warning function."""

    def test_log_warning_with_logger(self):
        """Test log_warning with a valid logger."""
        logger = MagicMock(spec=logging.Logger)
        message = "Test warning message"

        plog.log_warning(logger, message)

        logger.warning.assert_called_once_with(message)

    def test_log_warning_without_logger(self, capsys):
        """Test log_warning without a logger (prints to stdout)."""
        message = "Test warning message"

        plog.log_warning(None, message)

        captured = capsys.readouterr()
        assert f"WARNING: {message}" in captured.out

    def test_log_warning_with_logger_none(self, capsys):
        """Test log_warning with None logger falls back to print."""
        message = "Test warning"

        plog.log_warning(None, message)

        captured = capsys.readouterr()
        assert f"WARNING: {message}" in captured.out


class TestLogDebug:
    """Tests for log_debug function."""

    def test_log_debug_with_logger(self):
        """Test log_debug with a valid logger."""
        logger = MagicMock(spec=logging.Logger)
        message = "Test debug message"

        plog.log_debug(logger, message)

        logger.debug.assert_called_once_with(message)

    def test_log_debug_without_logger(self, capsys):
        """Test log_debug without a logger (prints to stdout)."""
        message = "Test debug message"

        plog.log_debug(None, message)

        captured = capsys.readouterr()
        assert f"DEBUG: {message}" in captured.out

    def test_log_debug_with_logger_none(self, capsys):
        """Test log_debug with None logger falls back to print."""
        message = "Test debug"

        plog.log_debug(None, message)

        captured = capsys.readouterr()
        assert f"DEBUG: {message}" in captured.out


class TestLoggingIntegration:
    """Integration tests for logging framework."""

    def test_full_logging_workflow(self):
        """Test complete logging workflow: init logger and log messages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize logger
            logger = plog.initialise_logger('integration_test', log_dir=temp_dir)

            # Log messages at different levels
            plog.log_debug(logger, "Debug message")
            plog.log_info(logger, "Info message")
            plog.log_warning(logger, "Warning message")
            plog.log_error(logger, "Error message")

            # Find the log file
            log_files = [f for f in os.listdir(temp_dir) if f.startswith('integration_test_')]
            assert len(log_files) == 1

            # Read log file and verify messages were written
            log_file_path = os.path.join(temp_dir, log_files[0])
            with open(log_file_path, 'r') as f:
                log_content = f.read()

            # Debug won't be logged (default level is INFO)
            assert "Debug message" not in log_content
            # These should be logged
            assert "Info message" in log_content
            assert "Warning message" in log_content
            assert "Error message" in log_content

    def test_logging_with_debug_level(self):
        """Test that debug messages are logged when level is DEBUG."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize logger with DEBUG level
            logger = plog.initialise_logger('debug_test', log_dir=temp_dir, log_level=logging.DEBUG)

            # Log debug message
            plog.log_debug(logger, "Debug message")

            # Find the log file
            log_files = [f for f in os.listdir(temp_dir) if f.startswith('debug_test_')]
            assert len(log_files) == 1

            # Read log file and verify debug message was written
            log_file_path = os.path.join(temp_dir, log_files[0])
            with open(log_file_path, 'r') as f:
                log_content = f.read()

            assert "Debug message" in log_content

    def test_log_file_naming_convention(self):
        """Test that log files follow the expected naming convention."""
        with tempfile.TemporaryDirectory() as temp_dir:
            script_name = 'my_script'
            _ = plog.initialise_logger(script_name, log_dir=temp_dir)

            # Find log files
            log_files = [f for f in os.listdir(temp_dir) if f.startswith(script_name)]
            assert len(log_files) == 1

            # Verify naming pattern: script_name_YYYY-MM-DD_HH-MM-SS.log
            log_file = log_files[0]
            assert log_file.startswith(f'{script_name}_')
            assert log_file.endswith('.log')
            # Should have timestamp in format YYYY-MM-DD_HH-MM-SS
            assert len(log_file.replace(f'{script_name}_', '').replace('.log', '')) == 19  # Length of timestamp
