# Changelog

All notable changes to the Expense Predictor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.9.0] - 2025-11-15

### Fixed

- **GitHub Dependency Removed** ([#74](https://github.com/manoj-bhaskaran/expense-predictor/issues/74))
  - Removed unpinned GitHub dependency from requirements.txt (line 16)
  - Eliminated `git+https://github.com/manoj-bhaskaran/My-Scripts.git@main` dependency
  - Now uses local `python_logging_framework.py` included in the project root
  - No external Git installation required for package installation
  - Installation now works in offline environments
  - Resolves security risks associated with unpinned branch references
  - Prevents installation failures due to GitHub rate limiting or outages

### Security

- **Improved Installation Security** ([#74](https://github.com/manoj-bhaskaran/expense-predictor/issues/74))
  - Eliminated risk of repository compromise or deletion breaking installations
  - Removed dependency on GitHub availability during installation
  - Local logging framework ensures consistent behavior across all installations
  - No longer vulnerable to unexpected changes in the upstream repository

### Improved

- **Installation Reliability** ([#74](https://github.com/manoj-bhaskaran/expense-predictor/issues/74))
  - Installation no longer requires Git to be installed on the system
  - Works in offline and air-gapped environments
  - Faster installation without network access to GitHub
  - More reliable CI/CD builds without external dependencies
  - Consistent installation experience across all platforms

- **Deployment Readiness** ([#74](https://github.com/manoj-bhaskaran/expense-predictor/issues/74))
  - Production-ready deployment without Git dependencies
  - Suitable for containerized environments (Docker, Kubernetes)
  - Compatible with restricted network environments
  - Reduces attack surface by eliminating external code dependencies

### Documentation

- **README.md Updates** ([#74](https://github.com/manoj-bhaskaran/expense-predictor/issues/74))
  - Removed requirement for Git installation
  - Updated installation instructions to reflect simplified process
  - Documented that python_logging_framework is included locally

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Migration Guide**:
- Existing installations will continue to work without changes
- For fresh installations, Git is no longer required
- To update: `pip install -r requirements.txt`

**Version Justification**:
- Minor version bump (1.8.1 → 1.9.0) per Semantic Versioning
- Significant improvement to installation reliability and security
- Backward-compatible change (no API modifications)
- Addresses critical dependency management issues

## [1.8.1] - 2025-11-15

### Improved

- **Enhanced .gitignore** ([#53](https://github.com/manoj-bhaskaran/expense-predictor/issues/53))
  - Added missing Python bytecode patterns: `*.pyo`, `*.pyd`
  - Added OS-specific patterns: `.DS_Store`, `Thumbs.db`
  - Added temporary editor files: `*~`
  - Added `.venv` to environment ignores (complements existing venv/, env/, ENV/)
  - Added model artifacts section: `models/`, `*.pkl`, `*.joblib`
  - Added configuration file pattern: `config.ini`
  - Ensures consistent Git hygiene across all development environments

### Fixed

- **Git Version Control** ([#53](https://github.com/manoj-bhaskaran/expense-predictor/issues/53))
  - Previously minimal .gitignore could allow unwanted files to be committed
  - Model artifacts (*.pkl, *.joblib) and trained models directory now properly ignored
  - OS-specific files (.DS_Store on macOS, Thumbs.db on Windows) now ignored
  - Python bytecode variations (*.pyo, *.pyd) now properly excluded
  - Temporary editor backup files (*~) now ignored

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Version Justification**:
- Patch version bump (1.8.0 → 1.8.1) per Semantic Versioning
- Improves repository hygiene and prevents accidental commits of unwanted files
- No code changes or functionality modifications
- No API changes

## [1.8.0] - 2025-11-15

### Added

- **Dependency Management Improvements** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - Created `setup.py` with proper package configuration
    - Includes `python_requires=">=3.9"` to enforce minimum Python version
    - Specifies all dependencies with pinned versions
    - Includes package metadata and classifiers
    - Defines console script entry point for `expense-predictor` command
    - Supports optional development dependencies via `extras_require`

  - Created `.python-version` file
    - Specifies Python 3.9 as the default version
    - Used by tools like pyenv for automatic version selection
    - Ensures consistent Python version across development environments

  - Added `bandit` security scanner to development dependencies
    - Version 1.7.5 for Python code security analysis
    - Complements existing security scanning workflow

### Changed

- **Pinned All Dependencies** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - **Production dependencies** (`requirements.txt`):
    - `numpy==1.26.4` (was unpinned)
    - `pandas==2.2.0` (was unpinned)
    - `scikit-learn==1.4.0` (was unpinned)
    - `xlrd==2.0.1` (was unpinned)
    - `pyyaml==6.0.1` (was unpinned)
    - Added clear section headers and comments for better organization
    - Kept GitHub dependency for `python_logging_framework` (author's own package)

  - **Development dependencies** (`requirements-dev.txt`):
    - Changed all `>=` version specifiers to `==` for exact versions
    - `pytest==7.4.0`, `pytest-cov==4.1.0`, `pytest-mock==3.11.1`
    - `flake8==6.1.0`, `black==23.7.0`, `isort==5.12.0`, `mypy==1.5.0`
    - `sphinx==7.1.0`, `pre-commit==3.4.0`, and all other dev tools
    - Added `bandit==1.7.5` for security scanning
    - Updated `matplotlib==3.8.0`, `seaborn==0.13.0` to stable versions

- **Documentation Updates** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - **README.md**:
    - Fixed Python version inconsistency (was "3.7+" in Requirements, "3.9+" in badge)
    - Now consistently specifies "Python 3.9 or higher" throughout
    - Added note about tested Python versions (3.9, 3.10, 3.11)
    - Updated project structure to include `setup.py` and `.python-version`
    - Clarified that `requirements.txt` contains pinned versions

### Fixed

- **Python Version Specification** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - Resolved inconsistency between README (Python 3.7+) and badge (Python 3.9+)
  - Now consistently requires Python 3.9+ across all documentation and configuration
  - Aligns with CI/CD test matrix (Python 3.9, 3.10, 3.11)

- **Dependency Version Compatibility** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - Pinned all dependency versions to prevent breaking changes from newer versions
  - Eliminates risk of unexpected behavior from automatic dependency upgrades
  - Ensures reproducible builds across different environments and time periods
  - Removed local path dependency issue (was already fixed in v1.0.1)

### Improved

- **Development Experience** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - Developers can now install the package in editable mode: `pip install -e .`
  - Development dependencies installable via: `pip install -e ".[dev]"`
  - Consistent Python version across team via `.python-version` file
  - No more "works on my machine" issues from version drift

- **Deployment and Distribution** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - Package installable via standard Python tools (pip, setuptools)
  - Can be built and distributed as a wheel: `python setup.py bdist_wheel`
  - Console script `expense-predictor` available after installation
  - Proper package metadata for PyPI compatibility (future publishing)

- **Dependency Security** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - Pinned versions allow targeted security updates
  - Dependabot can now suggest specific version updates
  - Security scanning (Bandit, Safety) works with known dependency versions
  - Reproducible security audits across time

- **Build Reproducibility** ([#52](https://github.com/manoj-bhaskaran/expense-predictor/issues/52))
  - Same dependencies installed regardless of when/where build occurs
  - CI/CD builds are now fully reproducible
  - Easier to debug dependency-related issues
  - Clear upgrade path when updating dependencies

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Migration Guide**:
1. If you have an existing installation, reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # for development
   ```

2. Or use the new setup.py:
   ```bash
   pip install -e .              # production dependencies
   pip install -e ".[dev]"       # with development dependencies
   ```

3. If using pyenv or similar tools, the `.python-version` file will automatically select Python 3.9

**Version Justification**:
- Minor version bump (1.7.0 → 1.8.0) per Semantic Versioning
- Adds new features (setup.py, .python-version) without breaking changes
- Improves dependency tracking and compatibility (non-breaking enhancement)
- No API changes or removal of functionality

## [1.7.0] - 2025-11-15

### Added

- **Comprehensive Documentation** ([#51](https://github.com/manoj-bhaskaran/expense-predictor/issues/51))
  - **ARCHITECTURE.md**: Complete architecture and design documentation
    - System overview with component diagram
    - Detailed model selection rationale for all four models
    - Feature engineering justification and implementation details
    - Data flow diagrams for each pipeline stage
    - Performance benchmarking guidelines and expected ranges
    - Design decisions with explanations (train/test split, YAML config, CLI, etc.)
    - Security architecture and defense-in-depth strategy
    - Scalability considerations and future enhancements

  - **MODELS.md**: Model evaluation and selection guide
    - Detailed explanation of each model's strengths and weaknesses
    - Comprehensive interpretation guide for RMSE, MAE, and R² metrics
    - Model comparison framework with decision flowchart
    - Scenario-based model recommendations
    - Hyperparameter tuning guide with practical examples
    - Common issues and solutions
    - Step-by-step example workflow

  - **CONTRIBUTING.md**: Complete contribution guidelines
    - Code of conduct and standards
    - Development setup instructions
    - Detailed development workflow (branching, testing, committing)
    - Code style guidelines with PEP 8 specifics
    - Docstring format with examples (Google-style)
    - Testing requirements and best practices
    - Pull request process and template
    - Commit message guidelines (Conventional Commits)
    - Documentation guidelines
    - Bug report and feature request templates

  - **API Documentation (Sphinx)**:
    - Complete Sphinx documentation setup in `docs/` directory
    - Auto-generated API reference from docstrings
    - Module documentation for model_runner, helpers, security, config
    - Installation guide (docs/installation.rst)
    - Configuration with sphinx-rtd-theme
    - Makefile for building HTML, PDF, and other formats
    - Documentation README with build instructions

  - **Sample Data**:
    - Added `sample_data.csv` with 3 months of realistic transaction data
    - 91 sample transactions with varying amounts
    - Properly formatted for immediate testing
    - Excluded from .gitignore for easy access

### Changed

- **README.md Updates** ([#51](https://github.com/manoj-bhaskaran/expense-predictor/issues/51))
  - Added new "Documentation" section with links to all documentation
  - Updated project structure to include new documentation files
  - Added instructions for building Sphinx documentation
  - Improved organization with clear navigation to specialized docs

- **.gitignore Updates** ([#51](https://github.com/manoj-bhaskaran/expense-predictor/issues/51))
  - Added exception for `sample_data.csv` to include in repository
  - Added Sphinx build directories (`docs/_build/`, `docs/_static/`, etc.)
  - Ensures documentation build artifacts are not committed

### Documentation

This release focuses entirely on filling critical documentation gaps:

**Before v1.7.0**:
- Basic README with usage instructions
- DATA.md with data format details
- CHANGELOG with version history
- Code had good docstrings but no compiled API docs

**After v1.7.0**:
- ✅ Architecture documentation explaining design decisions
- ✅ Model evaluation guide for choosing and tuning models
- ✅ Contribution guidelines for developers
- ✅ Auto-generated API documentation (Sphinx)
- ✅ Sample data included in repository
- ✅ Clear navigation between all documentation

**Documentation Coverage**:
- Project description and purpose ✓
- Features and capabilities ✓ (README.md)
- Installation instructions ✓ (README.md, docs/installation.rst)
- Usage examples ✓ (README.md)
- Data format requirements ✓ (DATA.md)
- Model performance benchmarks ✓ (ARCHITECTURE.md, MODELS.md)
- Troubleshooting guide ✓ (README.md)
- Contributing guidelines ✓ (CONTRIBUTING.md)
- License information ✓ (README.md, LICENSE)
- API documentation ✓ (docs/)
- Schema definition ✓ (DATA.md)
- Sample data ✓ (sample_data.csv)
- ML model selection rationale ✓ (ARCHITECTURE.md)
- Feature engineering justification ✓ (ARCHITECTURE.md)
- Configuration guide ✓ (README.md, docs/api/config.rst)

### Improved

- **Developer Experience**: Comprehensive contribution guidelines make it easier for new contributors
- **User Experience**: Clear model selection guide helps users choose the right model
- **Maintainability**: Architecture documentation preserves design decisions
- **Discoverability**: Centralized documentation section in README
- **Onboarding**: Sample data allows immediate experimentation
- **API Reference**: Sphinx documentation provides searchable API reference

### Notes

This is a documentation-only release with no code changes. All previous functionality remains unchanged. Users can upgrade without any breaking changes.

The project now has comprehensive documentation covering all aspects from high-level architecture to low-level API details.

## [1.6.0] - 2025-11-15

### Added

- **Security Scanning Pipeline** ([#50](https://github.com/manoj-bhaskaran/expense-predictor/issues/50))
  - Created comprehensive security scanning workflow (`security.yml`)
  - Bandit security scanner for Python code vulnerabilities
  - Safety dependency checker for known security vulnerabilities
  - Automated security scans on pull requests and pushes
  - Weekly scheduled security scans (Monday 10:00 AM UTC)
  - Security scan reports uploaded as artifacts
  - JSON and text format reports for both Bandit and Safety

- **Security Scanning Features**
  - **Bandit Integration**: Scans Python code for common security issues
    - SQL injection vulnerabilities
    - Hard-coded passwords and secrets
    - Insecure deserialization
    - Use of weak cryptographic functions
    - Path traversal vulnerabilities
    - Command injection risks
  - **Dependency Scanning**: Checks all dependencies for known CVEs
    - Scans both production and development dependencies
    - Reports known vulnerabilities from Safety DB
    - Provides remediation guidance

### Fixed

- **Dependabot Configuration** ([#50](https://github.com/manoj-bhaskaran/expense-predictor/issues/50))
  - Corrected package ecosystem from "maven" to "pip" (.github/dependabot.yml:8)
  - Dependabot will now properly monitor Python dependencies
  - Automated dependency updates will work correctly
  - Weekly update schedule maintained

### Improved

- **Security Posture**: Multiple layers of automated security scanning
- **DevOps Maturity**: Complete CI/CD pipeline with testing, quality, and security
- **Vulnerability Detection**: Automated detection of code and dependency vulnerabilities
- **Compliance**: Regular security audits through scheduled scans
- **Visibility**: Security reports available as workflow artifacts

### CI/CD Pipeline Summary

The project now has a complete CI/CD pipeline:

1. **Testing** (`test.yml`): Multi-version Python testing with 80% coverage enforcement
2. **Code Quality** (`pre-commit.yml`): Linting, formatting, and type checking
3. **Security** (`security.yml`): Vulnerability scanning for code and dependencies
4. **Dependency Management** (`dependabot.yml`): Automated dependency updates

## [1.5.0] - 2025-11-15

### Added

- **Comprehensive Testing Framework** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - Created complete test suite with pytest, pytest-cov, and pytest-mock
  - Added 57 unit and integration tests covering core functionality
  - Achieved 43% test coverage on initial implementation
  - Testing dependencies added to requirements-dev.txt

- **Test Structure** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - `tests/conftest.py`: Shared fixtures and test configuration
  - `tests/test_helpers.py`: 44 unit tests for helpers.py functions
  - `tests/test_model_runner.py`: 13 integration tests for ML pipeline
  - `tests/test_data/`: Sample CSV files for testing various scenarios
  - `tests/fixtures/`: Expected outputs for validation

- **Unit Tests for helpers.py** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - **File Validation Tests**:
    - `validate_csv_file()`: Tests for valid files, missing files, invalid columns, empty files
    - `validate_excel_file()`: Tests for file existence, format validation, extension checking
    - `validate_date_range()`: Tests for valid dates, NaT values, future dates
  - **Column Matching Tests**:
    - `find_column_name()`: Tests for exact match, normalized spacing, fuzzy matching
    - Validates flexible column name handling for Excel imports
  - **Date Manipulation Tests**:
    - `get_quarter_end_date()`: Tests for all quarters (Q1-Q4), edge cases, year boundaries
    - Comprehensive coverage of date calculations
  - **Data Processing Tests**:
    - `preprocess_data()`: Tests for valid files, invalid files, feature engineering
    - `prepare_future_dates()`: Tests for default dates, custom dates, past dates
    - `write_predictions()`: Tests for CSV creation, backup creation, injection prevention

- **Integration Tests for model_runner.py** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - **Data Preprocessing Pipeline**:
    - Full CSV preprocessing workflow
    - Missing date filling validation
    - Duplicate removal verification
  - **Model Training Tests**:
    - Linear Regression, Decision Tree, Random Forest, Gradient Boosting
    - Config parameter integration
    - Prediction generation validation
  - **Train/Test Split Tests**:
    - Split ratio validation from config
    - Temporal order preservation (shuffle=False)
  - **Model Evaluation Tests**:
    - RMSE, MAE, R² metric calculations
    - Separate metrics for train and test sets
  - **End-to-End Pipeline**:
    - Complete workflow from CSV to predictions
    - Feature alignment validation
    - Output format verification
  - **Configuration Integration**:
    - Config parameter loading tests
    - Value range validation

- **Test Configuration Files** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - `pytest.ini`: Pytest configuration with coverage settings
  - `.coveragerc`: Coverage configuration with 40% threshold
  - Test markers for categorization (unit, integration, slow, validation)
  - HTML and XML coverage reports enabled

- **Sample Test Data** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - `sample.csv`: Valid transaction data for testing
  - `sample_invalid_columns.csv`: Missing required columns
  - `sample_empty.csv`: Empty file edge case
  - `sample_invalid_dates.csv`: Invalid date formats
  - `sample_future_dates.csv`: Future-only dates for validation

- **Mock Logging Framework** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - Created `python_logging_framework.py` mock for testing
  - Allows tests to run without external dependency installation
  - Maintains compatibility with production logging interface

### Changed

- **Updated .gitignore** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - Added test artifacts (`.pytest_cache/`, `.coverage`, `htmlcov/`)
  - Added IDE-specific patterns (`.vscode/`, `.idea/`)
  - Added Python build artifacts (`*.pyc`, `__pycache__/`, `*.egg-info/`)
  - Excluded test data from ignore patterns (`!tests/test_data/*.csv`)

### Documentation

- **README.md Updates** ([#49](https://github.com/manoj-bhaskaran/expense-predictor/issues/49))
  - Added comprehensive "Running Tests" section
  - Included test coverage information
  - Added instructions for running specific test suites
  - Documented pytest markers and options
  - Added test coverage goals and metrics

### Improved

- **Quality Assurance**: Comprehensive test coverage for critical functionality
- **Code Reliability**: Automated testing catches regressions and bugs
- **Development Workflow**: Tests enable confident refactoring and feature additions
- **Documentation**: Clear testing guidelines for contributors
- **CI/CD Ready**: Tests prepared for continuous integration pipelines

## [1.4.0] - 2025-11-14

### Added

- **Security Module** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - Created new `security.py` module with comprehensive security utilities
  - Path validation and sanitization functions to prevent path injection attacks
  - File extension validation for CSV and Excel files
  - CSV injection prevention through value sanitization
  - Backup creation before file modifications
  - User confirmation prompts for file overwrites

- **Path Validation** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - `validate_and_resolve_path()`: Core path validation with security checks
  - `validate_file_path()`: File-specific validation with extension checking
  - `validate_directory_path()`: Directory validation with auto-creation option
  - Detects and prevents path traversal attacks (../ patterns)
  - Normalizes and resolves all file paths to absolute paths
  - Validates file extensions against allowed lists (security.py:28-86)

- **CSV Injection Prevention** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - `sanitize_csv_value()`: Sanitizes individual values before CSV output
  - `sanitize_dataframe_for_csv()`: Sanitizes entire DataFrames
  - Prevents formula injection by escaping dangerous characters (=, +, -, @)
  - Applied automatically to all prediction CSV outputs (security.py:138-181)

- **File Protection** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - `create_backup()`: Creates timestamped backups before overwriting files
  - `confirm_overwrite()`: Interactive confirmation prompts for file overwrites
  - Automatic backup creation in `write_predictions()` (helpers.py:389-396)
  - User confirmation required before overwriting existing files (helpers.py:382-387)

- **Command-Line Options** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - `--skip_confirmation`: New flag to skip confirmation prompts for automation
  - Useful for batch processing and CI/CD pipelines (model_runner.py:55)

### Changed

- **Enhanced Security in model_runner.py** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - All file and directory paths now validated before use
  - Excel directory and file paths validated with extension checks (model_runner.py:84-98)
  - Data file path validated with CSV extension check (model_runner.py:104-120)
  - Log directory path validated and safely created (model_runner.py:57-64)
  - Output directory path validated and safely created (model_runner.py:218-233)
  - Script exits gracefully with clear error messages on invalid paths

- **Enhanced Security in helpers.py** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - `write_predictions()` now includes backup and sanitization (helpers.py:361-408)
  - Added `skip_confirmation` parameter with default False (backward compatible)
  - CSV data sanitized before writing to prevent injection attacks
  - Backup created automatically before overwriting existing files
  - User prompted for confirmation before overwriting (unless skipped)

- **Excel File Validation** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - Added security warning for Excel files from untrusted sources (helpers.py:74-76)
  - Logs warning about potential malicious formulas or macros
  - Reminds users to only process Excel files from trusted sources

- **Updated Documentation** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - model_runner.py docstring updated with security features section
  - Added examples for automated mode with --skip_confirmation
  - Enhanced command-line argument documentation

### Security

- **Path Injection Protection** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - All user-provided paths (--excel_dir, --excel_file, --data_file, --log_dir, --output_dir) validated
  - Path traversal attacks prevented through resolution and pattern detection
  - Paths normalized to absolute paths using `pathlib.Path().resolve()`
  - Invalid paths rejected with clear error messages

- **File Extension Validation** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - CSV files must have .csv extension
  - Excel files must have .xls or .xlsx extension
  - Invalid extensions rejected before processing
  - Reduces risk of processing unexpected file types

- **CSV Injection Mitigation** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - All CSV output sanitized to prevent formula execution in spreadsheet applications
  - Dangerous formula characters (=, +, -, @, tabs, newlines) escaped with single quote
  - Protects users opening prediction CSVs in Excel or other spreadsheet tools

- **File Overwriting Protection** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - Automatic timestamped backups created before overwriting files
  - User confirmation required before overwriting (prevents accidental data loss)
  - Backup creation failures prevent the write operation (fail-safe)
  - Can be disabled with --skip_confirmation for automation

- **Excel File Warning** ([#48](https://github.com/manoj-bhaskaran/expense-predictor/issues/48))
  - Warning logged when processing Excel files
  - Reminds users about potential malicious formulas or macros
  - Encourages processing only trusted Excel files

### Improved

- **Error Handling**: More specific error messages for path validation failures
- **Security Posture**: Multiple layers of defense against common attack vectors
- **User Experience**: Clear warnings and confirmations for potentially destructive operations
- **Automation Support**: --skip_confirmation flag enables unattended operation
- **Code Organization**: Security utilities centralized in dedicated module
- **Logging**: Enhanced logging of security checks and validations

## [1.3.1] - 2025-11-14

### Improved

- **Categorical Handling Efficiency** ([#47](https://github.com/manoj-bhaskaran/expense-predictor/issues/47))
  - Optimized categorical conversion in `prepare_future_dates()` to happen during column creation (helpers.py:279)
  - Changed from two-step process (create then convert) to single-step conversion
  - Eliminates intermediate object-type Series creation, improving memory efficiency
  - No functional changes, purely performance optimization

## [1.3.0] - 2025-11-14

### Changed

- **Standardized Logging Approach** ([#46](https://github.com/manoj-bhaskaran/expense-predictor/issues/46))
  - Replaced all `print()` statements with `plog` logging calls for consistency
  - Removed 4 print() statements in config.py (config.py:67-72) - now use plog.log_error() and plog.log_info()
  - Removed duplicate print() statement in helpers.py (helpers.py:367) that was redundant with plog call
  - Enhanced `_process_dataframe()` with comprehensive logging (helpers.py:184-237)
  - Added logging for data conversion, cleaning, date range creation, and feature engineering steps
  - All logging now consistently uses `python_logging_framework` (plog) library

### Improved

- **Logging Consistency**: Unified logging approach across all modules (config.py, helpers.py, model_runner.py)
- **Observability**: Added detailed logging in data processing pipeline for better debugging and monitoring
- **Code Quality**: Eliminated mixed logging approaches (no more print() for operational messages)
- **Data Processing Visibility**: Users can now track data transformation steps through log files
  - Data type conversions and validations
  - Row counts after cleaning operations
  - Date range filling operations
  - Feature engineering progress

### Documentation

- **README.md**: Significantly expanded Logging section with comprehensive documentation
  - Added logging framework details and log levels
  - Documented what gets logged in each component
  - Added examples of log file location and customization
  - Explained logger parameter usage pattern
  - Included detailed breakdown of logged operations (model training, data processing, configuration, errors)

## [1.2.0] - 2025-11-14

### Added

- **Comprehensive Input Validation** ([#45](https://github.com/manoj-bhaskaran/expense-predictor/issues/45))
  - Added `validate_csv_file()` function to check CSV file existence and required columns (helpers.py:14-55)
  - Added `validate_excel_file()` function to validate Excel file existence and format (helpers.py:57-94)
  - Added `validate_date_range()` function to validate date ranges in data (helpers.py:96-131)
  - CSV validation checks for file existence, file type, and required columns ('Date', 'Tran Amt')
  - Excel validation checks for file existence, valid extensions (.xls, .xlsx), and file integrity
  - Date range validation checks for valid dates, prevents all-NaT data, and ensures data isn't all future dates
  - All validation functions integrated with logging framework for detailed error reporting

### Changed

- **Function Signatures**
  - Updated `preprocess_data()` to include logger parameter and call validation (helpers.py:232-247)
  - Updated `_process_dataframe()` to include logger parameter and date range validation (helpers.py:184-230)
  - Updated `preprocess_and_append_csv()` to call CSV and Excel validation before processing (helpers.py:276-352)
  - Added comprehensive error messages with file paths and available columns when validation fails

### Improved

- **Error Handling**: Early validation prevents cryptic errors later in processing
- **User Experience**: Clear, actionable error messages when input files are invalid
- **Data Quality**: Ensures required columns exist before attempting data processing
- **Robustness**: Validates file formats and detects corrupted Excel files before processing
- **Debugging**: All validations log detailed information for troubleshooting

## [1.1.0] - 2025-11-14

### Added

- **Configuration System** ([#44](https://github.com/manoj-bhaskaran/expense-predictor/issues/44))
  - Added `config.yaml` file for centralizing all configurable parameters
  - Created `config.py` module to load and manage configuration
  - All magic numbers and hyperparameters are now configurable without code changes
  - Configuration includes detailed comments explaining each parameter
  - Graceful fallback to sensible defaults if config.yaml is missing or invalid

- **Configurable Parameters**
  - **Data Processing**: `skiprows` (default: 12) - customizable for different bank statement formats
  - **Model Evaluation**: `test_size` (default: 0.2) and `random_state` (default: 42)
  - **Decision Tree**: All hyperparameters (max_depth, min_samples_split, min_samples_leaf, ccp_alpha, random_state)
  - **Random Forest**: All hyperparameters (n_estimators, max_depth, min_samples_split, min_samples_leaf, max_features, ccp_alpha, random_state)
  - **Gradient Boosting**: All hyperparameters (n_estimators, learning_rate, max_depth, min_samples_split, min_samples_leaf, max_features, random_state)

### Changed

- **Code Structure**
  - Refactored model_runner.py to load hyperparameters from configuration (model_runner.py:97-131)
  - Refactored helpers.py to load skiprows from configuration (helpers.py:174)
  - Added PyYAML dependency to requirements.txt

### Documentation

- Updated README.md with comprehensive configuration documentation
  - Added new "Configuration" section explaining config.yaml usage
  - Added "Model Tuning" section with tips for hyperparameter optimization
  - Updated project structure to include config.py and config.yaml
  - Enhanced troubleshooting section with configuration-related issues

### Improved

- **User Experience**: Users can now tune model parameters without editing code
- **Maintainability**: All magic numbers centralized in one location
- **Flexibility**: Easy to experiment with different hyperparameter combinations
- **Documentation**: Each parameter in config.yaml includes explanatory comments

## [1.0.5] - 2025-11-14

### Changed

- **Code Quality** ([#43](https://github.com/manoj-bhaskaran/expense-predictor/issues/43))
  - Removed redundant condition in model_runner.py:74
  - Simplified `elif not args.excel_file:` to `else:` for cleaner code
  - No functional changes, improves code readability

## [1.0.4] - 2025-11-14

### Fixed

- **Train/Test Split Implementation** ([#42](https://github.com/manoj-bhaskaran/expense-predictor/issues/42))
  - Introduced proper train/test split (80/20) for model evaluation (model_runner.py:95-96)
  - Models are now evaluated on held-out test data instead of training data only
  - Added separate performance metrics for training and test sets
  - Fixed overfitting risk detection by reporting true generalization performance
  - Test set metrics now accurately reflect model performance on unseen data
  - Training set metrics still logged for comparison and overfitting detection

### Changed

- **Model Evaluation**
  - Evaluation metrics now calculated on both training and test sets
  - Log output now includes separate sections for "Training Set Performance" and "Test Set Performance"
  - Added informative logging about data split sizes
  - Improved metric formatting with 2 decimal places for RMSE/MAE and 4 for R-squared

## [1.0.3] - 2025-11-14

### Fixed

- **Inconsistent Column Renaming** ([#41](https://github.com/manoj-bhaskaran/expense-predictor/issues/41))
  - Fixed duplicate column rename operation in `preprocess_and_append_csv` function (helpers.py:187-189)
  - Removed redundant second rename that attempted to rename an already-renamed column
  - The bug caused silent failures when processing Excel data with non-standard column names
  - Column is now correctly renamed once from the detected column name to VALUE_DATE_LABEL

## [1.0.2] - 2025-11-14

### Fixed

- **Data Mutation Side Effect** ([#40](https://github.com/manoj-bhaskaran/expense-predictor/issues/40))
  - Fixed `preprocess_and_append_csv` function in helpers.py that was destructively overwriting input CSV files
  - Refactored data processing logic into `_process_dataframe` helper function
  - The function now processes data in-memory without modifying original files
  - Eliminates unexpected behavior and data loss
  - Allows reprocessing with different parameters without data loss
  - Improves code maintainability and follows principle of least surprise

### Changed

- **Code Structure**
  - Extracted core dataframe processing logic into `_process_dataframe` internal helper function
  - Both `preprocess_data` and `preprocess_and_append_csv` now use the shared helper
  - Improved documentation to clarify non-destructive behavior

## [1.0.1] - 2025-11-14

### Fixed

- **Dependency Management**
  - Resolved external local dependency issue in requirements.txt
  - Replaced hard-coded local path `-e "D:\\My Scripts"` with GitHub reference
  - Added `python_logging_framework` as a proper Git dependency from `manoj-bhaskaran/My-Scripts` repository
  - Ensures the project can be installed by other users without local path dependencies

## [1.0.0] - 2025-11-14

### Added

- **Core Machine Learning Models**
  - Linear Regression model for baseline predictions
  - Decision Tree Regressor with optimized hyperparameters
  - Random Forest Regressor for ensemble predictions
  - Gradient Boosting Regressor with tuned parameters for better generalization

- **Data Processing Features**
  - CSV transaction data import and preprocessing
  - Excel bank statement integration (.xls and .xlsx support)
  - Flexible column name matching for Excel imports
  - Automatic date range completion with zero-filling for missing dates
  - Duplicate transaction handling (keeps last occurrence)
  - Support for both absolute and relative file paths

- **Feature Engineering**
  - Day of the week extraction and one-hot encoding
  - Month and day of month features
  - Automated feature alignment for predictions

- **Prediction Capabilities**
  - Custom future date predictions via command-line arguments
  - Automatic quarter-end prediction when no date specified
  - Separate prediction files for each model
  - Rounded predictions to 2 decimal places

- **Command-Line Interface**
  - `--future_date` parameter for custom prediction dates (DD/MM/YYYY format)
  - `--data_file` parameter for specifying transaction CSV file
  - `--excel_dir` parameter for Excel file directory
  - `--excel_file` parameter for Excel bank statement filename
  - `--log_dir` parameter for custom log directory
  - `--output_dir` parameter for prediction output location

- **Logging and Monitoring**
  - Comprehensive logging using python_logging_framework
  - Configurable log directory
  - Detailed model performance metrics (RMSE, MAE, R-squared)
  - Data processing step logging
  - Error tracking and debugging information

- **Model Evaluation**
  - Root Mean Squared Error (RMSE) calculation
  - Mean Absolute Error (MAE) calculation
  - R-squared score for model performance assessment
  - Performance metrics logged for each model

- **Documentation**
  - Comprehensive README.md with setup instructions
  - DATA.md with detailed data format documentation
  - Inline code documentation and docstrings
  - MIT License
  - .env.example configuration template
  - Development dependencies in requirements-dev.txt

- **Configuration Management**
  - Environment variable support via .env files
  - Command-line argument override capability
  - Flexible path configuration (relative and absolute)

### Fixed

- Hardcoded absolute paths removed to make project portable across systems
- Flexible column name matching for Excel bank statements with varying formatting
- KeyError handling for Excel column name variations
- Expense calculation from withdrawal and deposit columns in Excel files

### Changed

- Model hyperparameters tuned for better generalization
  - Decision Tree: max_depth=5, min_samples_split=10, min_samples_leaf=5, ccp_alpha=0.01
  - Random Forest: n_estimators=100, max_depth=10, max_features="sqrt"
  - Gradient Boosting: learning_rate=0.1, max_depth=5, optimized for balance

### Infrastructure

- GitHub Dependabot configuration for automated dependency updates
- CI/CD workflow setup for Python validation
- Git repository structure with proper .gitignore

### Security

- No hardcoded credentials or sensitive data
- Support for environment-based configuration
- Data privacy considerations documented

---

## Release Notes

### Version 1.0.0 - Initial Release

This is the initial stable release of the Expense Predictor. The system provides:

- **Multi-model approach**: Four different ML algorithms to compare prediction accuracy
- **Flexible data input**: Support for both CSV and Excel data sources
- **Production-ready**: Comprehensive logging, error handling, and configuration options
- **Well-documented**: Complete documentation for setup, usage, and data formats
- **Maintainable**: Clean code structure with helper functions and modular design

### Upgrade Instructions

As this is the first release, no upgrade steps are necessary. For new installations, follow the setup instructions in README.md.

### Known Limitations

- Single currency support (no multi-currency handling)
- Requires historical data for accurate predictions
- Excel import assumes specific column naming conventions
- No GUI interface (command-line only)

### Future Roadmap

Planned features for future releases:

- Additional ML models (e.g., LSTM for time series)
- Multi-currency support
- Interactive data visualization
- REST API for predictions
- Web-based user interface
- Automated model retraining
- Extended feature engineering options
- Database integration for data storage

---

## How to Report Issues

If you encounter any bugs or have feature requests, please open an issue on the [GitHub repository](https://github.com/manoj-bhaskaran/expense-predictor/issues).

When reporting issues, please include:
- Version number
- Operating system and Python version
- Complete error messages
- Steps to reproduce the issue
- Sample data (anonymized) if relevant

---

## Contributors

- Manoj Bhaskaran - Initial development and release

---

[1.9.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.9.0
[1.8.1]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.8.1
[1.8.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.8.0
[1.7.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.7.0
[1.6.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.6.0
[1.5.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.5.0
[1.4.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.4.0
[1.3.1]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.3.1
[1.3.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.3.0
[1.2.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.2.0
[1.1.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.1.0
[1.0.5]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.0.5
[1.0.4]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.0.4
[1.0.3]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.0.3
[1.0.2]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.0.2
[1.0.1]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.0.1
[1.0.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.0.0
