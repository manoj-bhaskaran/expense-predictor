# Expense Predictor

[![Tests](https://github.com/manoj-bhaskaran/expense-predictor/actions/workflows/test.yml/badge.svg)](https://github.com/manoj-bhaskaran/expense-predictor/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/manoj-bhaskaran/expense-predictor/branch/main/graph/badge.svg)](https://codecov.io/gh/manoj-bhaskaran/expense-predictor)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A machine learning-based expense prediction system that analyzes historical transaction data to forecast future expenses. The project uses multiple regression models to predict transaction amounts for specified future dates.

## Features

- **Multiple ML Models**: Supports Linear Regression, Decision Tree, Random Forest, and Gradient Boosting algorithms
- **Flexible Data Input**: Works with CSV transaction data and optionally integrates Excel bank statements
- **Robust Input Validation**: Validates file existence, format, required columns, and date ranges before processing
- **Security Features**: Path injection protection, file extension validation, CSV injection prevention, and automatic backups
- **Automated Predictions**: Generates predictions for custom future dates or automatically for the current quarter end
- **Comprehensive Logging**: Built-in logging framework for tracking operations and debugging
- **Performance Metrics**: Evaluates models using RMSE, MAE, and R-squared metrics
- **Portable**: Supports both absolute and relative file paths for flexible deployment
- **Data Protection**: Automatic backups and user confirmation before overwriting files
- **Complete CI/CD Pipeline**: Automated testing, code quality checks, and security scanning

## Requirements

- Python 3.9 or higher (tested on Python 3.9, 3.10, 3.11, and 3.12)
- See `requirements.txt` for pinned package dependencies

## Excel File Support

The Expense Predictor supports both legacy and modern Excel file formats with automatic format detection:

| Format | File Extension | Supported Via | Use Case |
|--------|----------------|---------------|----------|
| **Excel 97-2003** | `.xls` | xlrd 2.0.1 | Legacy bank statements and older Excel files |
| **Excel 2007+** | `.xlsx` | openpyxl 3.1.2 | Modern Excel files (recommended) |

### How It Works

- The application **automatically detects** the file format based on the file extension
- `.xls` files are processed using the `xlrd` library
- `.xlsx` files are processed using the `openpyxl` library
- Both formats are fully supported and require no additional configuration

### Important Notes

- **xlrd 2.0.0+** dropped support for `.xlsx` files due to security concerns
- For `.xlsx` files, `openpyxl` is required (automatically installed with the package)
- Both dependencies are included in `requirements.txt` for seamless installation
- The format is detected automatically - no manual configuration needed

### Example Usage

```bash
# Process legacy .xls file
expense-predictor --data_file trandata.csv --excel_file bank_statement.xls

# Process modern .xlsx file
expense-predictor --data_file trandata.csv --excel_file bank_statement.xlsx
```

Both commands work identically - the application handles the format detection internally.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/manoj-bhaskaran/expense-predictor.git
cd expense-predictor
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install development dependencies (optional)

```bash
pip install -r requirements-dev.txt
```

## Configuration

The project supports two types of configuration:

### 1. Model and Data Processing Configuration (config.yaml)

The `config.yaml` file allows you to customize model hyperparameters and data processing settings without modifying code. This file is automatically loaded when the application starts.

**Configuration Categories:**

- **Data Processing**: Control Excel file parsing (e.g., `skiprows` for bank statements)
- **Model Evaluation**: Set train/test split ratio and random seed for reproducibility
- **Model Hyperparameters**: Fine-tune each machine learning model's parameters

**Example configuration:**

```yaml
data_processing:
  skiprows: 12 # Number of header rows to skip in Excel files

model_evaluation:
  test_size: 0.2 # 20% of data for testing
  random_state: 42 # Seed for reproducibility

decision_tree:
  max_depth: 5
  min_samples_split: 10
  # ... more parameters
```

See `config.yaml` for the complete list of configurable parameters with detailed explanations.

**Type Validation:**

As of version 1.19.0, all configuration values are validated using Pydantic for type safety and early error detection. If you provide invalid types or out-of-range values, you'll receive clear error messages at startup:

```
ConfigurationError: Configuration validation failed:
  - Invalid type for 'decision_tree.max_depth': expected integer, got 'five'
  - Invalid value for 'model_evaluation.test_size': Input should be less than 1
```

**Validation Rules:**
- `logging.level`: Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL
- `skiprows`: Must be non-negative integer
- `test_size`: Must be between 0.0 and 1.0 (exclusive)
- `random_state`: Must be non-negative integer
- Model hyperparameters: Must be appropriate types with valid ranges (see config.py for details)

**Note:** If `config.yaml` is missing, the system will use sensible defaults and continue running. If the file exists but contains invalid values, the application will fail fast with a clear error message.

### 2. Environment Variables (.env file)

The project supports environment variables for setting default values. This is useful for:
- Setting default paths without command-line arguments
- Configuring different environments (dev, staging, prod)
- Keeping sensitive paths out of version control
- Automated workflows and CI/CD pipelines

**Setup:**

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred defaults
nano .env
```

**Supported Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `EXPENSE_PREDICTOR_DATA_FILE` | Path to CSV file with transaction data | `trandata.csv` |
| `EXPENSE_PREDICTOR_EXCEL_DIR` | Directory containing Excel file | `.` (current directory) |
| `EXPENSE_PREDICTOR_EXCEL_FILE` | Name of Excel file with additional data | None |
| `EXPENSE_PREDICTOR_LOG_DIR` | Directory for log files | `logs` |
| `EXPENSE_PREDICTOR_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `EXPENSE_PREDICTOR_OUTPUT_DIR` | Directory for prediction output files | `.` (current directory) |
| `EXPENSE_PREDICTOR_FUTURE_DATE` | Future date for predictions (DD/MM/YYYY) | End of current quarter |
| `EXPENSE_PREDICTOR_SKIP_CONFIRMATION` | Skip file overwrite confirmations (`true`/`false`) | `false` |
| `EXPENSE_PREDICTOR_SKIP_BASELINES` | Skip baseline forecasts and comparison report (`true`/`false`) | `false` |

**Example .env file:**

```bash
# Development environment
EXPENSE_PREDICTOR_DATA_FILE=./test_data/sample.csv
EXPENSE_PREDICTOR_LOG_DIR=./dev_logs
EXPENSE_PREDICTOR_LOG_LEVEL=DEBUG
EXPENSE_PREDICTOR_OUTPUT_DIR=./dev_predictions
EXPENSE_PREDICTOR_SKIP_CONFIRMATION=true
EXPENSE_PREDICTOR_SKIP_BASELINES=false
```

**Configuration Priority (highest to lowest):**

1. **Command-line arguments** - Override everything
2. **Environment variables** - Set via `.env` file
3. **Configuration file** - `config.yaml` settings
4. **Default values** - Built-in defaults

**Example:**

```bash
# Uses .env values for all settings
python model_runner.py

# Overrides .env data_file but uses other .env values
python model_runner.py --data_file ./other_data.csv
```

### 3. Runtime Configuration (Command-Line Arguments)

Command-line arguments provide the highest priority configuration and can override both environment variables and config file settings.

## Usage

The Expense Predictor can be run in two ways:

### Method 1: As an Installed Package (Recommended)

After installing the package with `pip install .` or `pip install -e .`, you can use the `expense-predictor` command:

**Basic Usage:**
```bash
expense-predictor --data_file trandata.csv
```

**Advanced Usage:**
```bash
expense-predictor \
  --future_date 31/12/2025 \
  --data_file ./data/trandata.csv \
  --excel_dir ./data \
  --excel_file bank_statement.xls \
  --log_dir ./logs \
  --output_dir ./predictions
```

### Method 2: As a Python Script

You can also run the script directly without installation:

**Basic Usage:**
```bash
python model_runner.py --data_file trandata.csv
```

**Advanced Usage:**
```bash
python model_runner.py \
  --future_date 31/12/2025 \
  --data_file ./data/trandata.csv \
  --excel_dir ./data \
  --excel_file bank_statement.xls \
  --log_dir ./logs \
  --output_dir ./predictions
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--future_date` | Future date for prediction (format: DD/MM/YYYY) | End of current quarter |
| `--data_file` | Path to CSV file containing transaction data | `trandata.csv` |
| `--excel_dir` | Directory containing Excel file | `.` (current directory) |
| `--excel_file` | Name of Excel file with additional data | None |
| `--log_dir` | Directory for log files | `logs` |
| `--log_level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `--output_dir` | Directory for prediction output files | `.` (current directory) |
| `--skip_confirmation` | Skip confirmation prompts when overwriting files (for automation) | False |
| `--skip_baselines` | Skip baseline forecasts and comparison report generation | False |

### Baselines and Comparison Report

The runner also produces simple baseline forecasts alongside ML models:

- **Naive last value**
- **Rolling mean** (3-month and 6-month windows)
- **Seasonal naive** (same period last year, when enough history is available)

Baseline predictions are saved in the same output directory as other models. A
`reports/model_comparison_report.csv` file ranks all models (ML + baselines) by test MAE and RMSE.
Disable baselines with `--skip_baselines` or set `baselines.enabled: false` in `config.yaml`.

## Automatic Transaction Data Updates

The Expense Predictor **automatically updates** your `trandata.csv` file when you provide an Excel file containing new transaction data. This eliminates the need for manual data consolidation and keeps your transaction history up to date.

### How It Works

When you run the predictor with an Excel file:

1. **Reads existing data**: Loads the current `trandata.csv` file
2. **Processes Excel file**: Extracts transaction data from the Excel file
3. **Merges and deduplicates**: Combines both datasets, removing duplicates (keeps newer data)
4. **Updates trandata.csv**: Automatically saves the merged data back to `trandata.csv`
5. **Continues with predictions**: Uses the merged data to train models and generate predictions

This happens automatically as part of the normal prediction workflow—no separate steps required!

### Example Usage

**Windows Example:**
```bash
python model_runner.py --future_date 21/12/2026 --excel_dir "C:\users\manoj\Downloads" --excel_file "OpTransactionHistory21-12-2025 (4).xls" --data_file trandata.csv
```

**Linux/Mac Example:**
```bash
python model_runner.py --future_date 31/12/2026 --excel_dir ./data --excel_file transactions.xlsx --data_file trandata.csv
```

After running this command:
- Your `trandata.csv` will be updated with the new Excel data
- A backup will be created (e.g., `trandata.csv.backup`) - only one previous version is kept
- The predictor will use the merged data to generate predictions

### Safety Features

- **Automatic backups**: Creates a backup before updating (e.g., `trandata.csv.backup`), keeping only one previous version
- **User confirmation**: Asks for confirmation before overwriting (unless using `--skip_confirmation`)
- **Duplicate handling**: Automatically removes duplicate dates, keeping the most recent data
- **CSV injection prevention**: Sanitizes data to prevent CSV injection attacks
- **Data validation**: Validates file formats, required columns, and date ranges before processing

### Workflow Example

```bash
# Run once with Excel file - updates trandata.csv and generates predictions
python model_runner.py --future_date 21/12/2026 --excel_dir "C:\users\manoj\Downloads" --excel_file "OpTransactionHistory.xls"

# Future runs can use just the CSV file (already updated)
python model_runner.py --future_date 31/03/2027
```

### Automated Mode

Use `--skip_confirmation` to bypass prompts (useful for automation):

```bash
python model_runner.py --future_date 21/12/2026 --excel_file transactions.xls --skip_confirmation
```

## Logging

The Expense Predictor provides configurable logging to help with debugging, monitoring, and operational visibility.

### Log Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Detailed information for diagnosing problems | Development and troubleshooting |
| `INFO` | General informational messages (default) | Normal operation monitoring |
| `WARNING` | Warning messages for potentially problematic situations | Production monitoring |
| `ERROR` | Error messages for serious problems | Production error tracking |
| `CRITICAL` | Critical errors that may cause the program to fail | System failures |

### Setting Log Level

There are three ways to configure the log level, in priority order (highest to lowest):

#### 1. Command-Line Argument (Highest Priority)

```bash
# Debug mode - most verbose
python model_runner.py --log-level DEBUG --data_file data.csv

# Normal mode (default)
python model_runner.py --data_file data.csv

# Quiet mode - warnings and errors only
python model_runner.py --log-level WARNING --data_file data.csv

# Very quiet - errors only
python model_runner.py --log-level ERROR --data_file data.csv
```

#### 2. Environment Variable

```bash
# Set environment variable
export EXPENSE_PREDICTOR_LOG_LEVEL=DEBUG
python model_runner.py --data_file data.csv

# Or in .env file
echo "EXPENSE_PREDICTOR_LOG_LEVEL=DEBUG" >> .env
```

#### 3. Configuration File (Lowest Priority)

```yaml
# config.yaml
logging:
  level: DEBUG
```

### Examples by Environment

#### Development Environment
```bash
# Maximum verbosity for debugging
python model_runner.py --log-level DEBUG --data_file sample.csv
```

#### Production Environment
```bash
# Reduce log noise, focus on warnings and errors
python model_runner.py --log-level WARNING --data_file production.csv
```

#### CI/CD Pipeline
```bash
# Minimal output for clean CI logs
python model_runner.py --log-level ERROR --data_file test.csv
```

### Log Output

The application logs to both the console and log files in the specified log directory (`--log_dir`). Log files are named with timestamps for easy identification.

**Example log output:**
```
2025-11-16 10:30:15,123 - model_runner.py - INFO - Log level set to: DEBUG
2025-11-16 10:30:15,124 - model_runner.py - INFO - Processing data file: ./data/sample.csv
2025-11-16 10:30:15,125 - model_runner.py - DEBUG - Validating file path: ./data/sample.csv
```

## Data Requirements

The system validates minimum data requirements before training to ensure meaningful predictions:

- **Minimum samples:** 30 transactions recommended for meaningful predictions
- **Minimum test samples:** 10 transactions in test set (20% of data)
- For best results, provide at least 100+ historical transactions
- More data = better predictions

These thresholds are configurable in `config.yaml` under `model_evaluation`:
- `min_total_samples`: Minimum total samples required (default: 30)
- `min_test_samples`: Minimum test samples required (default: 10)

If your data doesn't meet these requirements, the system will:
- Display a clear error message explaining the issue
- Suggest how much more data is needed
- Recommend adjusting the test_size in config.yaml if appropriate

### Input Data Format

#### CSV Transaction Data (trandata.csv)

The CSV file should contain at least two columns:

- `Date`: Transaction date (supports various date formats)
- `Tran Amt`: Transaction amount (numeric)

Example:

```csv
Date,Tran Amt
01/01/2024,150.00
02/01/2024,75.50
03/01/2024,200.00
```

#### Excel Bank Statement (optional)

If using an Excel file, it should contain:

- `Value Date`: Transaction date
- `Withdrawal Amount (INR )`: Withdrawal amounts
- `Deposit Amount (INR )`: Deposit amounts

The script will automatically process these columns and merge them with CSV data.

### Output

The script generates prediction CSV files for each model:

- `future_predictions_linear_regression.csv`
- `future_predictions_decision_tree.csv`
- `future_predictions_random_forest.csv`
- `future_predictions_gradient_boosting.csv`

Each file contains:

- `Date`: Future dates
- `Predicted Tran Amt`: Predicted transaction amounts

## Documentation

Comprehensive documentation is available:

- **[README.md](README.md)** - This file - overview, installation, and usage
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture, design decisions, and model selection rationale
- **[MODELS.md](MODELS.md)** - Model evaluation guide and hyperparameter tuning
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines for developers
- **[DATA.md](DATA.md)** - Data format specifications and requirements
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[API Documentation](docs/)** - Auto-generated API documentation (Sphinx)

### Building API Documentation

To build the HTML API documentation:

```bash
cd docs
make html
open _build/html/index.html  # View in browser
```

See [docs/README.md](docs/README.md) for details.

## Project Structure

```
expense-predictor/
├── model_runner.py          # Main script for model training and prediction
├── helpers.py               # Helper functions for data preprocessing
├── security.py              # Security utilities (path validation, sanitization)
├── config.py                # Configuration loader module
├── constants.py             # Centralized constants for the application
├── config.yaml              # Configuration file for hyperparameters
├── python_logging_framework.py  # Custom logging framework module
├── setup.py                 # Package setup and dependencies configuration
├── requirements.txt         # Production dependencies (pinned versions)
├── requirements-dev.txt     # Development dependencies (pinned versions)
├── .python-version          # Python version specification (3.9)
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── pytest.ini               # Pytest configuration
├── .coveragerc             # Coverage configuration
├── .env.example            # Example environment configuration
├── sample_data.csv         # Sample transaction data for testing
├── README.md               # This file
├── ARCHITECTURE.md         # Architecture and design documentation
├── MODELS.md               # Model evaluation and tuning guide
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # MIT License
├── CHANGELOG.md            # Version history
├── DATA.md                 # Data format documentation
├── docs/                   # Sphinx API documentation
│   ├── conf.py             # Sphinx configuration
│   ├── index.rst           # Documentation home page
│   ├── api/                # API reference documentation
│   └── Makefile            # Documentation build script
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest fixtures and configuration
│   ├── test_helpers.py     # Unit tests for helpers.py
│   ├── test_model_runner.py # Integration tests for ML pipeline
│   ├── test_data/          # Sample data files for testing
│   └── fixtures/           # Expected outputs for validation
└── .github/
    ├── workflows/
    │   ├── test.yml        # Automated testing workflow
    │   ├── pre-commit.yml  # Code quality checks workflow
    │   └── security.yml    # Security scanning workflow
    └── dependabot.yml      # Dependency management configuration
```

## Data Preprocessing

The system performs the following preprocessing steps:

1. **Data Cleaning**: Removes duplicates and handles missing values
2. **Date Normalization**: Converts dates to consistent format
3. **Feature Engineering**: Creates features like day of week, month, and day of month
4. **Data Completion**: Fills missing dates with zero transaction amounts
5. **One-Hot Encoding**: Encodes categorical features (day of week)

## Model Performance

The script uses a **chronological 80/20 train/test split** to evaluate each model's generalization performance. The split is time-aware: the first 80% of data (by date) is used for training and the last 20% for testing. This prevents data leakage by ensuring models are never evaluated on data from time periods they were trained on.

Each model is evaluated using:

- **RMSE (Root Mean Squared Error)**: Measures prediction accuracy
- **MAE (Mean Absolute Error)**: Average absolute prediction error
- **R-squared**: Proportion of variance explained by the model

Performance metrics are reported separately for:

- **Training Set**: Shows how well the model fits the training data
- **Test Set**: Shows true generalization performance on unseen future data

Train/test date boundaries are logged explicitly for transparency (e.g., "train [2024-01-01 to 2024-10-15], test [2024-10-16 to 2024-12-31]").

Check the log files in the `logs/` directory for detailed performance metrics.

## Logging

The project uses a consistent logging approach throughout, powered by the `python_logging_framework` (plog) library. All logging is standardized to ensure comprehensive tracking and debugging capabilities.

### Logging Framework

This project includes a custom logging framework (`python_logging_framework.py`) that provides simplified logging setup with both file and console handlers.

**Usage**:
```python
import python_logging_framework as plog

logger = plog.initialise_logger('my_script', log_dir='logs')
plog.log_info(logger, "Info message")
plog.log_warning(logger, "Warning message")
plog.log_error(logger, "Error message")
plog.log_debug(logger, "Debug message")
```

**Location**: `python_logging_framework.py` in the repository root.

**Features**:
- **Unified Logging**: All components use `plog` for consistent logging behavior
- **Log Levels**: Support for debug, info, warning, and error levels
  - `plog.log_debug()` - Debug messages for troubleshooting
  - `plog.log_info()` - Informational messages (successful operations, progress tracking)
  - `plog.log_warning()` - Warning messages for non-critical issues
  - `plog.log_error()` - Error conditions and failures
- **Automatic Log Files**: Logs are saved to the `logs/` directory with timestamps
- **Dual Output**: Messages are logged to both file and console simultaneously
- **Flexible Configuration**: Customizable log directory and log level

### What Gets Logged

Log files include detailed information about:

- **Model Training**: Training progress, model performance metrics (RMSE, MAE, R²)
- **Data Processing**:
  - Data validation results (file checks, column validation, date range validation)
  - Data cleaning operations (rows cleaned, duplicates removed)
  - Feature engineering steps (features created, transformations applied)
  - Date range processing (start/end dates, missing date filling)
- **Configuration**: Config file loading status, parameter usage
- **File Operations**: File reads, prediction outputs, data validation
- **Error Messages**: Detailed error information with context for debugging
- **Warnings**: Configuration fallbacks, data quality issues

### Log File Location

By default, logs are saved to:

```
logs/model_runner.py_YYYY-MM-DD_HH-MM-SS.log
```

You can customize the log directory using the `--log_dir` command-line argument:

```bash
expense-predictor --data_file trandata.csv --log_dir ./my_logs
```

### Logger Parameter

Most helper functions accept an optional `logger` parameter. When called from `model_runner.py`, the logger is passed through the call chain. Functions can also operate without a logger (logger=None) for standalone usage.

### Configuring log level

You can control the effective log level with the following priority (highest -> lowest):

- **CLI argument**: `--log-level` (choices: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- **Environment variable**: `EXPENSE_PREDICTOR_LOG_LEVEL`
- **Config file**: `config.yaml` under `logging.level`
- **Default**: `INFO`

Examples:

```bash
# Run with debug logging via CLI:
python model_runner.py --data_file trandata.csv --log-level DEBUG

# Run with error-only logging via env var:
EXPENSE_PREDICTOR_LOG_LEVEL=ERROR python model_runner.py --data_file trandata.csv
```

## Security

The application includes comprehensive security features to protect against common attack vectors:

### Path Injection Protection

All user-provided file paths are validated and sanitized to prevent path traversal attacks:

- Paths are resolved to absolute paths using `pathlib.Path().resolve()`
- Path traversal patterns (`../`) are detected and rejected
- Paths are normalized to prevent directory escaping
- Invalid paths are rejected with clear error messages

This applies to all path arguments: `--data_file`, `--excel_dir`, `--excel_file`, `--log_dir`, and `--output_dir`.

### File Extension Validation

The application validates file extensions before processing:

- CSV files must have `.csv` extension
- Excel files must have `.xls` or `.xlsx` extension
- Files with invalid extensions are rejected before processing
- Reduces risk of processing unexpected or malicious file types

### CSV Injection Prevention

All prediction output files are sanitized to prevent CSV injection attacks:

- Dangerous formula characters (`=`, `+`, `-`, `@`, tabs, newlines) are escaped
- Values that could be interpreted as formulas are prefixed with a single quote
- Protects users who open prediction CSVs in Excel or other spreadsheet applications
- Prevents potential code execution when CSVs are opened

### File Overwriting Protection

The application protects against accidental data loss:

- **Automatic Backups**: Creates timestamped backups before overwriting existing files
- **User Confirmation**: Prompts for confirmation before overwriting prediction files
- **Fail-Safe**: If backup creation fails, the write operation is aborted
- **Automation Support**: Use `--skip_confirmation` to disable prompts for batch processing

Example with confirmation prompts:

```bash
expense-predictor --data_file trandata.csv
# Will prompt: "File 'future_predictions_linear_regression.csv' already exists. Overwrite? [y/N]:"
```

Example for automated workflows (no prompts):

```bash
expense-predictor --data_file trandata.csv --skip_confirmation
# Overwrites without confirmation, but still creates backups
```

### Excel File Security Warning

When processing Excel files, the application logs security warnings:

- Reminds users that Excel files may contain malicious formulas or macros
- Encourages processing only Excel files from trusted sources
- Warns about potential security risks in the log files

**Important**: Only process Excel files from trusted sources. The application cannot detect or prevent malicious Excel formulas or macros.

### Best Practices

1. **Use Trusted Data Sources**: Only process CSV and Excel files from trusted sources
2. **Review Logs**: Check log files for security warnings and validation messages
3. **Backup Important Data**: The application creates backups, but maintain your own backups too
4. **Validate Paths**: Be cautious when using absolute paths from user input
5. **Automated Workflows**: Use `--skip_confirmation` only in controlled environments

## Development

### Pre-commit Hooks

The project uses pre-commit hooks to automatically check code quality before commits. This catches issues early and ensures consistent code formatting.

**Setup:**

```bash
# Install pre-commit (included in requirements-dev.txt)
pip install -r requirements-dev.txt

# Install the git hooks
pre-commit install

# (Optional) Run on all files to test
pre-commit run --all-files
```

**What gets checked:**
- Code formatting (black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)
- YAML/TOML validation
- Trailing whitespace, EOF fixes, and more

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed information about pre-commit hooks, including how to skip hooks when necessary.

### Running Tests

The project includes a comprehensive test suite with unit and integration tests.

#### Install Test Dependencies

```bash
# Install development dependencies (includes pytest, pytest-cov, pytest-mock)
pip install -r requirements-dev.txt
```

#### Run All Tests

```bash
# Run all tests with coverage report
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with short traceback
pytest tests/ --tb=short
```

#### Run Specific Test Suites

```bash
# Run only unit tests for helpers.py
pytest tests/test_helpers.py -v

# Run only integration tests
pytest tests/test_model_runner.py -v

# Run specific test class
pytest tests/test_helpers.py::TestFindColumnName -v

# Run specific test function
pytest tests/test_helpers.py::TestFindColumnName::test_find_column_name_exact_match -v
```

#### Running Tests by Category (Markers)

Tests are organized using pytest markers for selective execution. This allows you to run specific categories of tests for faster feedback during development.

**Available Test Markers:**

- `unit`: Unit tests for individual functions (fast, isolated)
- `integration`: Integration tests for complete workflows (slower)
- `slow`: Tests that take longer to run (model training, full pipelines)
- `validation`: Tests for data validation functions

**Run tests by category:**

```bash
# Run only unit tests (fast feedback during development)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only validation tests
pytest -m validation

# Skip slow tests during development
pytest -m "not slow"

# Run everything except integration tests
pytest -m "not integration"

# Combine markers (unit AND validation tests)
pytest -m "unit and validation"

# Run unit OR integration tests
pytest -m "unit or integration"
```

**Use Cases:**

- **Fast development cycle**: Run `pytest -m unit` for quick feedback
- **Pre-commit checks**: Run `pytest -m "not slow"` to skip time-consuming tests
- **Full validation**: Run `pytest` (all tests) before pushing
- **CI/CD staging**: Run unit tests first, then integration tests (see `.github/workflows/test.yml`)

**Verbose output with markers:**

```bash
# See which tests are being run
pytest -m unit -v

# Show marker information
pytest --markers
```

#### Coverage Reports

**Note:** Coverage is not enabled by default to keep test runs fast during development. Add `--cov=.` to any test command to generate coverage reports.

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test category with coverage
pytest -m unit --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML coverage report (for CI/CD)
pytest --cov=. --cov-report=xml

# Run all tests with full coverage report
pytest --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml
```

#### Test Coverage

**Coverage Requirement: 80% minimum** (enforced on pull requests)

Current test coverage: **88%** ✅ (exceeds CI/CD requirements)

Coverage breakdown by file:
- `model_runner.py`: **87%** - Main execution logic
- `helpers.py`: **88%** - Data processing utilities
- `config.py`: **100%** - Configuration management
- `security.py`: **85%** - Security validation

- Unit tests: 44 tests covering helpers.py functions
- Integration tests: 66 tests covering the ML pipeline and CLI
- CLI tests: 21 tests for argument parsing and main execution
- Total: 131 tests

**Tested Components:**

- File validation (CSV and Excel)
- Date range validation
- Column name matching
- Quarter-end date calculations
- Data preprocessing pipeline
- Model training (Linear Regression, Decision Tree, Random Forest, Gradient Boosting)
- Train/test splitting
- Model evaluation metrics
- Future prediction generation
- CSV output and security

**Note:** Pull requests must achieve 80% test coverage to be merged. See [Branch Protection Guide](.github/BRANCH_PROTECTION.md) for details.

### Code Style

The project follows PEP 8 style guidelines. Use a linter to check code quality:

```bash
flake8 model_runner.py helpers.py security.py config.py
```

## CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline with multiple automated workflows:

### Automated Workflows

1. **Testing (`test.yml`)** - Runs on all pull requests and pushes

   - Multi-version Python testing (3.9, 3.10, 3.11, 3.12)
   - Automated test execution with pytest
   - Code coverage enforcement (minimum 80%)
   - Coverage reports uploaded to Codecov
   - PR comments with coverage information
   - Coverage artifacts saved for review

2. **Code Quality (`pre-commit.yml`)** - Runs on all pull requests and pushes

   - **Linting**: flake8 checks for syntax errors and code style
   - **Formatting**: Black code formatting validation
   - **Import Sorting**: isort checks for organized imports
   - **Type Checking**: mypy for static type analysis

3. **Security Scanning (`security.yml`)** - Runs on pull requests, pushes, and weekly schedule

   - **Bandit**: Python security vulnerability scanner
     - Detects SQL injection, hard-coded secrets, weak crypto
     - Identifies path traversal and command injection risks
   - **Safety**: Dependency vulnerability scanner
     - Checks for known CVEs in dependencies
     - Scans both production and development packages
   - **Reports**: JSON and text reports uploaded as artifacts
   - **Schedule**: Weekly scans every Monday at 10:00 AM UTC

4. **Dependency Management (`dependabot.yml`)** - Automated dependency updates
   - Weekly checks for outdated Python packages
   - Automated pull requests for dependency updates
   - Security vulnerability notifications

### Viewing CI/CD Results

- **GitHub Actions**: View workflow runs in the "Actions" tab
- **Pull Requests**: Status checks and coverage comments appear automatically
- **Artifacts**: Download security and coverage reports from workflow runs
- **Badges**: Status badges at the top of README show current state

### Branch Protection

For production deployments, consider enabling branch protection rules:

- Require status checks to pass before merging
- Require pull request reviews
- Require up-to-date branches before merging
- See `.github/BRANCH_PROTECTION.md` for detailed setup

## Model Tuning

To improve prediction accuracy, you can tune the model hyperparameters in `config.yaml`:

1. **Adjust test_size**: Change the train/test split ratio (default: 0.2)
2. **Tune Decision Tree**: Modify `max_depth`, `min_samples_split`, etc.
3. **Tune Random Forest**: Adjust `n_estimators`, `max_depth`, etc.
4. **Tune Gradient Boosting**: Change `learning_rate`, `n_estimators`, etc.

After modifying `config.yaml`, simply run the script again - no code changes needed!

**Tips for tuning:**

- Lower `max_depth` values prevent overfitting
- Higher `min_samples_split` and `min_samples_leaf` create simpler models
- Increase `n_estimators` for better performance (at the cost of training time)
- Lower `learning_rate` (with more estimators) often improves generalization

## Troubleshooting

### Common Issues

**Issue**: `FileNotFoundError: CSV file not found` or `FileNotFoundError: Excel file not found`

- **Solution**: Verify the file path is correct. Use absolute paths or ensure relative paths are correct from the script's directory. Check that the file exists and you have read permissions.

**Issue**: `ValueError: Missing required columns in CSV file`

- **Solution**: Ensure your CSV file contains both 'Date' and 'Tran Amt' columns. Check the column names match exactly (case-sensitive). The error message will show which columns were found.

**Issue**: `ValueError: Invalid Excel file format`

- **Solution**: Ensure the file has a .xls or .xlsx extension and is a valid Excel file. The script only supports Excel formats, not other spreadsheet formats like .ods or .csv.

**Issue**: `ValueError: No valid dates found in the data`

- **Solution**: Check that your Date column contains valid date values. Ensure dates are properly formatted and not all empty/null values.

**Issue**: `ValueError: Data contains only future dates`

- **Solution**: The training data must contain historical (past) dates. The script cannot train on future dates only.

**Issue**: `KeyError` when reading Excel files

- **Solution**: Ensure Excel file has correct column names. The script supports flexible column name matching, but column headers should include "Value Date", "Withdrawal Amount", and "Deposit Amount"

**Issue**: `ValueError: Incorrect date format`

- **Solution**: Ensure dates are in DD/MM/YYYY format when using `--future_date`

**Issue**: Import errors for `python_logging_framework` or `yaml`

- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Predictions seem inaccurate

- **Solution**: Check that your training data has sufficient historical data (at least several months recommended). Review log files for model performance metrics. Try tuning hyperparameters in `config.yaml`.

**Issue**: Different Excel file format (different skiprows)

- **Solution**: Edit `config.yaml` and change the `skiprows` value under `data_processing` to match your bank statement format.

**Issue**: `ValueError: Path traversal detected` or `ValueError: Invalid file extension`

- **Solution**: These are security protections. Ensure you're using valid file paths without `../` patterns and that files have correct extensions (.csv, .xls, or .xlsx).

**Issue**: File overwrite confirmation prompts blocking automation
- **Solution**: Use the `--skip_confirmation` flag to disable prompts: `expense-predictor --data_file trandata.csv --skip_confirmation`

**Issue**: Cannot find backup files

- **Solution**: Backup files are created with timestamps in the same directory as the output file. Look for files with `.backup_YYYYMMDD_HHMMSS` suffix.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with scikit-learn for machine learning capabilities
- Uses pandas for data manipulation and analysis
- Logging powered by python_logging_framework (included locally in project)

## Support

For issues, questions, or contributions, please open an issue on the [GitHub repository](https://github.com/manoj-bhaskaran/expense-predictor/issues).
