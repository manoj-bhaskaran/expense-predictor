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

- Python 3.9 or higher (tested on Python 3.9, 3.10, and 3.11)
- Git (required for installing dependencies from GitHub)
- See `requirements.txt` for pinned package dependencies

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

**Note:** Git must be installed on your system as some dependencies are installed directly from GitHub repositories.

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
  skiprows: 12  # Number of header rows to skip in Excel files

model_evaluation:
  test_size: 0.2      # 20% of data for testing
  random_state: 42    # Seed for reproducibility

decision_tree:
  max_depth: 5
  min_samples_split: 10
  # ... more parameters
```

See `config.yaml` for the complete list of configurable parameters with detailed explanations.

**Note:** If `config.yaml` is missing or invalid, the system will use sensible defaults and continue running.

### 2. Runtime Configuration (Command-Line Arguments)

Command-line arguments control file paths and runtime behavior. No environment variables are strictly required, but you can create a `.env` file based on `.env.example` for custom default paths.

## Usage

### Basic Usage

Run the model with default settings (uses current quarter end as prediction date):

```bash
python model_runner.py --data_file trandata.csv
```

### Advanced Usage

Specify a custom future date and additional data sources:

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
| `--output_dir` | Directory for prediction output files | `.` (current directory) |
| `--skip_confirmation` | Skip confirmation prompts when overwriting files (for automation) | False |

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
├── config.yaml              # Configuration file for hyperparameters
├── setup.py                 # Package setup and dependencies configuration
├── requirements.txt         # Production dependencies (pinned versions)
├── requirements-dev.txt     # Development dependencies (pinned versions)
├── .python-version          # Python version specification (3.9)
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

The script uses an 80/20 train/test split to evaluate each model's generalization performance. Each model is evaluated using:
- **RMSE (Root Mean Squared Error)**: Measures prediction accuracy
- **MAE (Mean Absolute Error)**: Average absolute prediction error
- **R-squared**: Proportion of variance explained by the model

Performance metrics are reported separately for:
- **Training Set**: Shows how well the model fits the training data
- **Test Set**: Shows true generalization performance on unseen data

Check the log files in the `logs/` directory for detailed performance metrics.

## Logging

The project uses a consistent logging approach throughout, powered by the `python_logging_framework` (plog) library. All logging is standardized to ensure comprehensive tracking and debugging capabilities.

### Logging Framework

- **Unified Logging**: All components use `plog` for consistent logging behavior
- **Log Levels**:
  - `plog.log_info()` - Informational messages (successful operations, progress tracking)
  - `plog.log_error()` - Error conditions and failures
- **Automatic Log Files**: Logs are saved to the `logs/` directory with timestamps
- **Configuration Loading**: Even configuration warnings are logged using plog

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
python model_runner.py --data_file trandata.csv --log_dir ./my_logs
```

### Logger Parameter

Most helper functions accept an optional `logger` parameter. When called from `model_runner.py`, the logger is passed through the call chain. Functions can also operate without a logger (logger=None) for standalone usage.

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
python model_runner.py --data_file trandata.csv
# Will prompt: "File 'future_predictions_linear_regression.csv' already exists. Overwrite? [y/N]:"
```

Example for automated workflows (no prompts):
```bash
python model_runner.py --data_file trandata.csv --skip_confirmation
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

#### Coverage Reports

```bash
# Generate coverage report in terminal
pytest tests/ --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML coverage report (for CI/CD)
pytest tests/ --cov=. --cov-report=xml
```

#### Test Coverage

**Coverage Requirement: 80% minimum** (enforced on pull requests)

Current test coverage: **43%** (needs improvement to meet CI/CD requirements)

- Unit tests: 44 tests covering helpers.py functions
- Integration tests: 13 tests covering the ML pipeline
- Total: 57 tests

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
   - Multi-version Python testing (3.9, 3.10, 3.11)
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
- **Solution**: Use the `--skip_confirmation` flag to disable prompts: `python model_runner.py --data_file trandata.csv --skip_confirmation`

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
- Logging powered by python_logging_framework

## Support

For issues, questions, or contributions, please open an issue on the [GitHub repository](https://github.com/manoj-bhaskaran/expense-predictor/issues).
