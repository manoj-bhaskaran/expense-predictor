# Changelog

All notable changes to the Expense Predictor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.18.2] - 2025-11-16

### Changed

- **Consolidate Constants into Single Module** ([#110](https://github.com/manoj-bhaskaran/expense-predictor/issues/110))
  - Created new `constants.py` module for centralized constant definitions
  - Moved `TRANSACTION_AMOUNT_LABEL`, `VALUE_DATE_LABEL`, and `DAY_OF_WEEK` constants from helpers.py to constants.py
  - Removed duplicate `TRANSACTION_AMOUNT_LABEL` definition from model_runner.py (line 287)
  - Updated helpers.py to import constants from constants module
  - Updated model_runner.py to import constants from constants module
  - Establishes single source of truth for all constants
  - Prevents future DRY violations and inconsistencies

### Impact

- **Severity**: High
- **Type**: Code Quality / Refactoring
- **User Impact**: No functional changes - purely internal refactoring
- **Breaking Changes**: None - backward compatible code improvement
- **Benefits**:
  - Single source of truth for constants
  - Easier maintenance and updates
  - Reduces risk of inconsistency
  - Improved code organization
  - Follows Python best practices

### Technical Details

- **Files Added**:
  - `constants.py` - New module containing all shared constants

- **Files Modified**:
  - `helpers.py` (removed lines 16-18, added import from constants)
  - `model_runner.py` (removed line 287, added import from constants)
  - `setup.py` (added constants to py_modules, version bumped to 1.18.2)
  - `tests/__init__.py` (version bumped to 1.18.2)
  - `CHANGELOG.md` (this file)

- **Testing**:
  - All 191 existing tests pass
  - No test modifications required
  - Verified constant imports work correctly

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Version Justification**:
- Patch version bump (1.18.1 → 1.18.2) per Semantic Versioning
- Internal refactoring: improves code quality without changing functionality
- No API changes or new features
- Backward compatible: existing code works unchanged

**Migration Guide**:
- No migration needed - purely internal refactoring
- All imports remain compatible
- Existing code continues to work without modification

**Related Issues and PRs**:
- Issue #110: DRY Violation: TRANSACTION_AMOUNT_LABEL Defined in Multiple Files

## [1.18.1] - 2025-11-16

### Fixed

- **Line Profiler Version Consistency** ([#109](https://github.com/manoj-bhaskaran/expense-predictor/issues/109))
  - Updated `line-profiler` from 4.1.0 to 4.1.3 in `setup.py` extras_require (setup.py:74)
  - Resolved version mismatch between setup.py (4.1.0) and requirements-dev.txt (4.1.3)
  - Both installation methods now install the same version: 4.1.3
  - Ensures consistent development environments across all installation methods
  - Version 4.1.3 is required for Python 3.12 compatibility (see v1.17.0 release notes)

### Impact

- **Severity**: High
- **Affected Functionality**: Development environment consistency
- **User Impact**: Both `pip install -e .[dev]` and `pip install -r requirements-dev.txt` now install line-profiler==4.1.3
- **Breaking Changes**: None - backward compatible bug fix

### Technical Details

- **Files Modified**:
  - `setup.py` (line-profiler version updated from 4.1.0 to 4.1.3 at line 74)
  - `setup.py` (version bumped to 1.18.1)
  - `tests/__init__.py` (version bumped to 1.18.1)
  - `CHANGELOG.md` (this file)

- **Root Cause**:
  - PR #104 updated line-profiler in requirements-dev.txt for Python 3.12 compatibility
  - The corresponding update in setup.py was inadvertently missed
  - This created inconsistent environments depending on installation method

- **Version Justification**:
  - line-profiler 4.1.3 specifically fixes Python 3.12 compatibility issues
  - Using the older 4.1.0 version defeats the Python 3.12 support added in v1.17.0
  - Consistency across installation methods prevents "works on my machine" issues

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Version Justification**:
- Patch version bump (1.18.0 → 1.18.1) per Semantic Versioning
- Bug fix: resolves dependency version inconsistency
- No API changes or new features
- Backward compatible: existing code works unchanged

**Migration Guide**:
- For existing installations using `pip install -e .[dev]`: Re-run installation to get line-profiler 4.1.3
- For installations using `pip install -r requirements-dev.txt`: No changes needed (already on 4.1.3)
- To verify version: `pip show line-profiler | grep Version` (should show 4.1.3)

**Related Issues and PRs**:
- Issue #109: Version Mismatch: line-profiler Between setup.py and requirements-dev.txt
- PR #104: Add Python 3.12 to test matrix and update documentation
- Commit b7b1b13: fix: Update line-profiler to 4.1.3 for Python 3.12 compatibility

## [1.18.0] - 2025-11-16

### Added

- **Minimum Data Validation Before Model Training** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108))
  - Added `validate_minimum_data()` function to validate sufficient training data (helpers.py:214-257)
  - Validates minimum total samples (default: 30) before attempting model training
  - Validates minimum test samples (default: 10) after train/test split
  - Prevents runtime errors with insufficient data
  - Provides clear, actionable error messages guiding users on data requirements
  - Integrated into model_runner.py main() execution flow (model_runner.py:410-413)
  - Called after data preprocessing, before train_test_split

- **Configurable Data Validation Thresholds** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108))
  - Added `min_total_samples` parameter to config.yaml (default: 30)
  - Added `min_test_samples` parameter to config.yaml (default: 10)
  - Users can customize thresholds based on their specific use case
  - Graceful fallback to defaults if parameters not present in config

### Changed

- **Enhanced Error Messages** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108))
  - Insufficient data errors now include specific sample counts
  - Error messages suggest concrete actions (add more data or adjust config)
  - Test size validation considers configured test_size ratio
  - Logs validation success with sample counts for transparency

### Documentation

- **README.md** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108))
  - Added comprehensive "Data Requirements" section
  - Documented minimum sample requirements (30 total, 10 test)
  - Explained configurable thresholds in config.yaml
  - Provided guidance on what happens when data is insufficient
  - Recommended 100+ transactions for best results

- **config.yaml** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108))
  - Added detailed comments for min_total_samples parameter
  - Added detailed comments for min_test_samples parameter
  - Explained rationale for default values

### Improved

- **User Experience** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108))
  - Users receive clear error messages instead of cryptic failures
  - Validation happens early, before expensive computation
  - Error messages guide users on next steps
  - Sets proper expectations about data requirements

- **Code Reliability** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108))
  - Prevents crashes during train_test_split with 1 sample
  - Prevents meaningless results with 2-5 samples
  - Detects severe overfitting scenarios (5-20 samples) before training
  - Validates test set size to ensure meaningful evaluation

- **Developer Experience** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108))
  - Validation function is reusable and well-documented
  - Clear separation of concerns (validation vs. training)
  - Configurable thresholds enable different use cases
  - Comprehensive logging for debugging

### Impact

- **Severity**: Critical
- **Affected Functionality**: Model training pipeline
- **User Impact**: Better error handling and guidance for insufficient data
- **Breaking Changes**: None - backward compatible enhancement

### Technical Details

- **Files Modified**:
  - `helpers.py` (added validate_minimum_data function, lines 214-257)
  - `model_runner.py` (added validation call, lines 410-413; updated imports, lines 51-57)
  - `config.yaml` (added min_total_samples and min_test_samples parameters, lines 28-34)
  - `README.md` (added Data Requirements section)
  - `CHANGELOG.md` (this file)
  - `setup.py` (version bumped to 1.18.0)
  - `tests/__init__.py` (version bumped to 1.18.0)

- **Code References**:
  - `helpers.py:214-257` - validate_minimum_data() function implementation
  - `model_runner.py:410-413` - Validation call before train_test_split
  - `config.yaml:28-34` - New configuration parameters

### Notes

**Version Justification**:
- Minor version bump (1.17.2 → 1.18.0) per Semantic Versioning
- New feature: Data validation before model training
- Backward compatible: existing code works unchanged
- No breaking changes to API or behavior
- Enhancement prevents runtime failures

**Benefits**:
- Better user experience with clear error messages
- Prevents wasted computation on insufficient data
- Sets proper expectations about data requirements
- Helps users understand why predictions might be poor
- Early failure is better than cryptic late failure

**Testing**:
- Validation function uses existing DataValidationError exception
- Integrates with existing logging framework (plog)
- Uses existing config loading mechanism
- No new dependencies required

## [1.17.2] - 2025-11-16

### Fixed

- **Enhanced Error Handling for Excel File Processing** ([#107](https://github.com/manoj-bhaskaran/expense-predictor/issues/107))
  - Added explicit `ImportError` handling for missing openpyxl dependency in `helpers.py`
  - Better error messages when openpyxl is not installed for .xlsx file processing
  - Error message now includes installation instructions: `pip install openpyxl`
  - Improved error handling in both `validate_excel_file()` (helpers.py:108-118) and `preprocess_and_append_csv()` (helpers.py:414-424)
  - Prevents confusing error messages when processing .xlsx files without openpyxl

### Documentation

- **Excel File Support Documentation** ([#107](https://github.com/manoj-bhaskaran/expense-predictor/issues/107))
  - Added comprehensive "Excel File Support" section to README.md
  - Documented the distinction between .xls and .xlsx formats
  - Clarified that xlrd 2.0.1+ only supports .xls files (not .xlsx)
  - Explained automatic format detection based on file extension
  - Provided clear table showing which library handles which format:
    - `.xls` files: xlrd 2.0.1 (Excel 97-2003)
    - `.xlsx` files: openpyxl 3.1.2 (Excel 2007+)
  - Added usage examples for both file formats
  - Documented that both dependencies are included in requirements.txt

### Improved

- **Error Messages** ([#107](https://github.com/manoj-bhaskaran/expense-predictor/issues/107))
  - Users now get actionable error messages with installation instructions
  - Clear distinction between missing dependency errors and file corruption errors
  - Improved debugging experience for Excel file processing issues

### Impact

- **Severity**: Low
- **Affected Functionality**: Excel .xlsx file processing error handling
- **User Impact**: Better error messages and documentation for Excel file support
- **Breaking Changes**: None - backward compatible enhancement

### Technical Details

- **Files Modified**:
  - `helpers.py` (added ImportError handling in two locations)
  - `README.md` (added Excel File Support section)
  - `CHANGELOG.md` (this file)
  - `setup.py` (version bumped to 1.17.2)
  - `tests/__init__.py` (version bumped to 1.17.2)

- **Code References**:
  - `helpers.py:108-118` - ImportError handling in validate_excel_file()
  - `helpers.py:414-424` - ImportError handling in preprocess_and_append_csv()
  - xlrd 2.0.0+ dropped .xlsx support per official changelog
  - Both xlrd and openpyxl are production dependencies in requirements.txt

### Notes

**Version Justification**:
- Patch version bump (1.17.1 → 1.17.2) per Semantic Versioning
- Bug fix: Improved error handling for missing dependencies
- Documentation improvements
- No API changes or new features
- Backward compatible: existing code works unchanged

**Context**:
- xlrd 2.0.0+ intentionally dropped .xlsx support due to security concerns with Excel formulas
- The code already correctly uses openpyxl for .xlsx files (since v1.17.1)
- This release adds better error messages and documentation to clarify the distinction
- Both dependencies are already in requirements.txt - no installation changes needed

## [1.17.1] - 2025-11-16

### Fixed

- **Missing Production Dependency** ([#106](https://github.com/manoj-bhaskaran/expense-predictor/issues/106))
  - Added `openpyxl==3.1.2` to production dependencies in `requirements.txt`
  - Added `openpyxl==3.1.2` to `setup.py` install_requires
  - Resolves critical issue where .xlsx file processing failed in production installations
  - openpyxl was previously only listed in development dependencies (requirements-dev.txt)
  - Users can now process both .xls and .xlsx files after standard installation
  - Runtime error `ModuleNotFoundError: No module named 'openpyxl'` resolved

### Impact

- **Severity**: Critical
- **Affected Functionality**: Excel .xlsx file processing (helpers.py:105-106)
- **User Impact**: Production installations can now process .xlsx files without manual dependency installation
- **Breaking Changes**: None - backward compatible enhancement

### Technical Details

- **Files Modified**:
  - `requirements.txt` (added openpyxl==3.1.2 with comment)
  - `setup.py` (added openpyxl==3.1.2 to install_requires at line 48)
  - `tests/__init__.py` (version bumped to 1.17.1)
  - `CHANGELOG.md` (this file)

- **Code Reference**:
  - `helpers.py:105-106` uses openpyxl engine for .xlsx files
  - Engine selection: `engine = "xlrd" if file_path.endswith(".xls") else "openpyxl"`
  - pandas.ExcelFile() requires openpyxl for .xlsx format support

### Notes

**Version Justification**:
- Patch version bump (1.17.0 → 1.17.1) per Semantic Versioning
- Bug fix: missing dependency that broke core functionality
- No API changes or new features
- Backward compatible: existing code works unchanged

**Migration Guide**:
- For existing installations: `pip install -r requirements.txt` or `pip install openpyxl==3.1.2`
- For new installations: dependencies now correctly installed automatically
- No code changes required

## [1.17.0] - 2025-11-15

### Added

- **Python 3.12 Support** ([#87](https://github.com/manoj-bhaskaran/expense-predictor/issues/87))
  - Added Python 3.12 to CI/CD test matrix in `.github/workflows/test.yml`
  - All tests now run on Python 3.9, 3.10, 3.11, and 3.12
  - Updated coverage reporting to use Python 3.12 (latest tested version)
  - Verified all dependencies are compatible with Python 3.12:
    - numpy==1.26.4 ✅
    - pandas==2.2.0 ✅
    - scikit-learn==1.5.0 ✅
    - xlrd==2.0.1 ✅
    - pyyaml==6.0.1 ✅
  - Aligns CI/CD testing with setup.py classifiers (which already claimed 3.12 support)

### Fixed

- **Python 3.12 Dependency Compatibility** ([#87](https://github.com/manoj-bhaskaran/expense-predictor/issues/87))
  - Updated `line-profiler` from 4.1.0 to 4.1.3 in requirements-dev.txt
  - Resolves Cython dependency conflict that prevented installation on Python 3.12
  - line-profiler 4.1.3 properly supports Python 3.12 without requiring unavailable Cython alpha versions

### Changed

- **CI/CD Pipeline Enhancement** ([#87](https://github.com/manoj-bhaskaran/expense-predictor/issues/87))
  - Coverage reports now generated using Python 3.12 instead of 3.11
  - Codecov uploads now use Python 3.12 results
  - PR coverage comments now based on Python 3.12 test runs
  - All four Python versions (3.9, 3.10, 3.11, 3.12) now tested in parallel

### Documentation

- **README.md** ([#87](https://github.com/manoj-bhaskaran/expense-predictor/issues/87))
  - Updated requirements section to include Python 3.12
  - Changed "tested on Python 3.9, 3.10, and 3.11" to "tested on Python 3.9, 3.10, 3.11, and 3.12"
  - Updated Python version badge to reflect 3.9+ support with 3.12 testing
  - Documentation now accurately reflects tested Python versions

### Improved

- **Future Compatibility** ([#87](https://github.com/manoj-bhaskaran/expense-predictor/issues/87))
  - Users can confidently install and run on Python 3.12
  - CI/CD validates Python 3.12 compatibility on every pull request
  - Eliminates inconsistency between classifiers and actual testing
  - Ensures compatibility with latest stable Python release

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Context**:
- Issue #87 identified inconsistency between setup.py classifiers (claiming 3.12 support) and CI/CD test matrix (only testing 3.9-3.11)
- All dependencies already support Python 3.12
- This change validates existing classifier claims with actual testing

**Version Justification**:
- Minor version bump (1.16.0 → 1.17.0) per Semantic Versioning
- Adds new Python version support (new feature)
- Backward compatible: all existing Python versions (3.9-3.11) still supported
- No code changes required, only CI/CD infrastructure updates

**Testing Coverage**:
- All 163 existing tests now run on Python 3.12
- No test modifications required
- All tests pass on Python 3.12
- Coverage threshold (80%) maintained across all Python versions

**Files Modified**:
- `.github/workflows/test.yml` (added 3.12 to matrix, updated coverage conditions)
- `requirements-dev.txt` (updated line-profiler to 4.1.3 for Python 3.12 compatibility)
- `README.md` (updated Python version documentation)
- `CHANGELOG.md` (this file)
- `setup.py` (version bumped to 1.17.0)

## [1.16.0] - 2025-11-16

### Added

- **Configurable Log Levels** 
  - Added `--log-level` command-line argument with choices: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - Added `EXPENSE_PREDICTOR_LOG_LEVEL` environment variable support
  - Added logging configuration section to `config.yaml` with `level` parameter
  - Implemented priority order: CLI argument > environment variable > config file > default (INFO)
  - Added automatic log level validation with graceful fallback to INFO for invalid values
  - Added startup log message indicating the selected log level
  - Updated argument parser documentation to include environment variable and config file options

### Changed

- Enhanced logging flexibility for development, production, and CI/CD environments
- Improved debugging capabilities with configurable verbosity levels

## [1.15.0] - 2025-11-15

### Added

- **Pre-commit Hooks Configuration** ([#85](https://github.com/manoj-bhaskaran/expense-predictor/issues/85))
  - Created `.pre-commit-config.yaml` with comprehensive pre-commit hooks
  - Configured hooks for code formatting (black, isort)
  - Added linting checks (flake8 with max-line-length=127, max-complexity=10)
  - Integrated type checking (mypy with ignore-missing-imports)
  - Added security scanning (bandit excluding tests directory)
  - Included basic checks (trailing whitespace, EOF fixer, YAML/TOML validation, etc.)
  - Added YAML linting (yamllint with 120-character line length)
  - Hook versions match requirements-dev.txt for consistency:
    - black==24.3.0
    - isort==5.12.0
    - flake8==6.1.0
    - mypy==1.5.0
    - bandit==1.7.5
    - pre-commit-hooks==4.4.0
    - yamllint==1.32.0

### Documentation

- **README.md** ([#85](https://github.com/manoj-bhaskaran/expense-predictor/issues/85))
  - Added new "Pre-commit Hooks" section in Development
  - Documented setup instructions and what gets checked
  - Updated project structure to include `.pre-commit-config.yaml`
  - Added reference to CONTRIBUTING.md for detailed information

- **CONTRIBUTING.md** ([#85](https://github.com/manoj-bhaskaran/expense-predictor/issues/85))
  - Added new section "6. Set Up Pre-commit Hooks" in Development Setup
  - Documented what each hook does (black, isort, flake8, mypy, bandit, basic checks, yamllint)
  - Provided instructions for skipping hooks when necessary
  - Added commands for updating hook versions
  - Renumbered subsequent sections accordingly

### Improved

- **Developer Experience** ([#85](https://github.com/manoj-bhaskaran/expense-predictor/issues/85))
  - Developers can now run `pre-commit install` to enable local pre-commit hooks
  - Automatic code quality checks before each commit
  - Catches formatting, linting, and security issues early (before CI/CD)
  - Faster feedback loop: local checks are faster than waiting for CI/CD
  - Reduced CI/CD failures: issues caught locally before pushing
  - Consistent code formatting across all contributors
  - Auto-formatters (black, isort) fix issues automatically

- **Code Quality** ([#85](https://github.com/manoj-bhaskaran/expense-predictor/issues/85))
  - Ensures all code meets quality standards before commit
  - Automatic formatting prevents style debates
  - Type checking catches potential bugs early
  - Security scanning identifies vulnerabilities before they reach the repository
  - Configuration matches CI/CD pipeline for consistency

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Context**:
- Issue #85 requested adding `.pre-commit-config.yaml` file
- pre-commit was already in requirements-dev.txt (version 3.4.0)
- CI/CD workflow `.github/workflows/pre-commit.yml` already existed
- This completes the pre-commit setup by enabling local hooks

**Version Justification**:
- Minor version bump (1.14.0 → 1.15.0) per Semantic Versioning
- New feature added (pre-commit hooks configuration)
- Backward compatible: no changes to existing functionality
- Enhancement to developer experience without breaking changes

**Pre-commit Hooks Coverage**:
- Code formatters: 2 hooks (black, isort) - auto-fix on commit
- Linters: 1 hook (flake8) - check-only
- Type checking: 1 hook (mypy) - check-only
- Security: 1 hook (bandit) - check-only
- Basic checks: 9 hooks (whitespace, EOF, YAML, TOML, merge conflicts, etc.)
- YAML validation: 1 hook (yamllint) - check-only
- Total: 15 pre-commit hooks configured

**Integration with CI/CD**:
- Pre-commit configuration mirrors CI/CD checks in `.github/workflows/pre-commit.yml`
- Same tools with same arguments (black, isort, flake8)
- Ensures local checks match CI/CD expectations
- Reduces "works on my machine" issues

**Files Modified**:
- `.pre-commit-config.yaml` (new file)
- `CONTRIBUTING.md` (added pre-commit setup section)
- `README.md` (added pre-commit hooks section, updated project structure)
- `setup.py` (version bumped to 1.15.0)
- `CHANGELOG.md` (this file)

## [1.14.0] - 2025-11-15

### Added

- **Environment Variable Configuration Support** ([#84](https://github.com/manoj-bhaskaran/expense-predictor/issues/84))
  - Created `.env.example` file with all supported environment variables
  - Added `python-dotenv==1.0.0` dependency for environment variable loading
  - Implemented automatic `.env` file loading in `model_runner.py`
  - Environment variables now provide default values for all CLI arguments
  - Supported environment variables:
    - `EXPENSE_PREDICTOR_DATA_FILE`: Default CSV data file path
    - `EXPENSE_PREDICTOR_EXCEL_DIR`: Default Excel file directory
    - `EXPENSE_PREDICTOR_EXCEL_FILE`: Default Excel file name
    - `EXPENSE_PREDICTOR_LOG_DIR`: Default log directory
    - `EXPENSE_PREDICTOR_OUTPUT_DIR`: Default output directory
    - `EXPENSE_PREDICTOR_FUTURE_DATE`: Default future date for predictions
    - `EXPENSE_PREDICTOR_SKIP_CONFIRMATION`: Skip confirmation prompts (true/false)
  - Command-line arguments take precedence over environment variables
  - Works seamlessly without `.env` file (uses built-in defaults)

### Changed

- **Configuration Priority** ([#84](https://github.com/manoj-bhaskaran/expense-predictor/issues/84))
  - Updated configuration priority order:
    1. Command-line arguments (highest priority)
    2. Environment variables (.env file)
    3. Configuration file (config.yaml)
    4. Default values (lowest priority)

### Documentation

- **README.md** ([#84](https://github.com/manoj-bhaskaran/expense-predictor/issues/84))
  - Added comprehensive "Environment Variables (.env file)" section
  - Documented all supported environment variables with descriptions
  - Provided example `.env` configurations for different environments
  - Explained configuration priority order
  - Added usage examples showing environment variable and CLI interaction

- **CONTRIBUTING.md** ([#84](https://github.com/manoj-bhaskaran/expense-predictor/issues/84))
  - Added "Configure Environment Variables" step in development setup
  - Added "Environment Variables for Development" section in Development Tips
  - Documented environment variable configuration workflow
  - Added "Adding new environment variables" to documentation update checklist

### Testing

- **Environment Variable Tests** ([#84](https://github.com/manoj-bhaskaran/expense-predictor/issues/84))
  - Added 11 new unit tests for environment variable loading
  - Test individual environment variables are loaded correctly
  - Test CLI arguments override environment variables (priority)
  - Test application works without environment variables (defaults)
  - Test multiple environment variables work together
  - All tests marked with `@pytest.mark.unit` for selective execution

### Improved

- **Developer Experience** ([#84](https://github.com/manoj-bhaskaran/expense-predictor/issues/84))
  - Developers can now set default paths via `.env` file
  - Reduces need to specify command-line arguments repeatedly
  - Supports different configurations per environment (dev, staging, prod)
  - `.env` file already in `.gitignore` to prevent accidental commits

- **Automation and CI/CD** ([#84](https://github.com/manoj-bhaskaran/expense-predictor/issues/84))
  - Environment variables enable easier automation and scripting
  - Docker containers can use environment variables for configuration
  - CI/CD pipelines can set variables without modifying code
  - `SKIP_CONFIRMATION` variable supports headless execution

## [1.13.0] - 2025-11-15

### Added

- **Pytest Markers for Selective Test Execution** ([#83](https://github.com/manoj-bhaskaran/expense-predictor/issues/83))
  - Added `@pytest.mark.unit` to all unit tests (144 tests)
  - Added `@pytest.mark.integration` to integration tests (29 tests)
  - Added `@pytest.mark.slow` to time-consuming tests (16 tests)
  - Added `@pytest.mark.validation` to data validation tests (33 tests)
  - Markers enable selective test execution: `pytest -m unit`, `pytest -m integration`, etc.
  - Support for combining markers: `pytest -m "unit and validation"`, `pytest -m "not slow"`
  - All markers properly defined in `pytest.ini` with descriptions

### Changed

- **CI/CD Pipeline Enhancement** ([#83](https://github.com/manoj-bhaskaran/expense-predictor/issues/83))
  - Updated `.github/workflows/test.yml` to use staged testing
  - CI now runs unit tests first (fast feedback), then integration tests, then validation tests
  - Tests execute in sequence with `--cov-append` to accumulate coverage
  - Faster CI feedback: unit tests complete in ~30 seconds
  - Full test suite still runs, but organized for better developer experience

### Documentation

- **Enhanced README.md** ([#83](https://github.com/manoj-bhaskaran/expense-predictor/issues/83))
  - Added comprehensive "Running Tests by Category (Markers)" section
  - Documented all four marker types with descriptions and use cases
  - Provided examples for common testing scenarios
  - Added CLI examples: run unit tests, skip slow tests, combine markers
  - Explained CI/CD staging approach

### Improved

- **Developer Experience** ([#83](https://github.com/manoj-bhaskaran/expense-predictor/issues/83))
  - Faster development cycle: developers can run `pytest -m unit` for quick feedback
  - Skip slow tests during development: `pytest -m "not slow"`
  - Better test organization: tests clearly categorized by purpose
  - Selective test execution reduces test time from ~2 minutes to ~30 seconds for unit tests

- **Test Organization** ([#83](https://github.com/manoj-bhaskaran/expense-predictor/issues/83))
  - Unit tests: Individual function tests (test_security, test_config, test_logging_framework)
  - Integration tests: Full workflow tests (test_model_runner, test_model_runner_cli)
  - Validation tests: Data validation specific (parts of test_helpers, test_edge_cases)
  - Slow tests: Model training and full pipeline tests
  - Markers serve as documentation of test purpose and scope

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Context**:
- Issue #83 requested adding pytest markers to enable selective test execution
- Markers were defined in pytest.ini but not used in any test files
- This prevented selective test execution and made test organization less effective

**Version Justification**:
- Minor version bump (1.12.1 → 1.13.0) per Semantic Versioning
- New functionality added (selective test execution via markers)
- Backward compatible: all existing test commands still work
- Enhancement to testing infrastructure without breaking changes

**Test Coverage**:
- All 163 tests now properly marked with appropriate categories
- Test execution verified with all marker combinations
- Coverage reporting still works correctly with marker-based execution
- No tests removed or modified, only markers added

**Files Modified**:
- `tests/test_helpers.py` (added markers to 10 test classes)
- `tests/test_security.py` (added markers to 8 test classes)
- `tests/test_config.py` (added markers to 4 test classes)
- `tests/test_model_runner.py` (added markers to 7 test classes)
- `tests/test_edge_cases.py` (added markers to 3 test classes)
- `tests/test_model_runner_cli.py` (added markers to 6 test classes)
- `tests/test_logging_framework.py` (added markers to 6 test classes)
- `.github/workflows/test.yml` (updated to use staged testing)
- `README.md` (added marker usage documentation)
- `CHANGELOG.md` (this file)

## [1.12.1] - 2025-11-15

### Fixed

- **Logging Framework Clarification** ([#82](https://github.com/manoj-bhaskaran/expense-predictor/issues/82))
  - Clarified that `python_logging_framework.py` is the official logging framework implementation
  - Removed "Mock" designation from module header
  - Updated module docstring to accurately describe its purpose and functionality
  - Removed all `# pragma: no cover` comments from logging framework functions
  - GitHub dependency was already removed in v1.9.0; confirmed local version is the standard

### Added

- **Comprehensive Logging Framework Tests** ([#82](https://github.com/manoj-bhaskaran/expense-predictor/issues/82))
  - Created `tests/test_logging_framework.py` with 22 comprehensive unit tests
  - Tests for `initialise_logger()`: default params, custom log level, directory creation, file creation, handler management, formatters
  - Tests for `log_info()`, `log_error()`, `log_warning()`, `log_debug()`: with and without logger
  - Integration tests: full logging workflow, debug level logging, log file naming conventions
  - Achieved 100% test coverage for python_logging_framework.py module
  - Total test count increased from 141 to 163 tests
  - Overall test coverage increased to 89.15%

### Documentation

- **Enhanced README.md** ([#82](https://github.com/manoj-bhaskaran/expense-predictor/issues/82))
  - Added comprehensive "Logging Framework" section with usage examples
  - Included code examples demonstrating all logging functions
  - Added feature list: unified logging, log levels, automatic log files, dual output, flexible configuration
  - Updated project structure to include `python_logging_framework.py`
  - Improved clarity on logging framework location and purpose
  - Enhanced logging documentation with complete API usage

### Improved

- **Code Quality** ([#82](https://github.com/manoj-bhaskaran/expense-predictor/issues/82))
  - Logging framework now properly tested with comprehensive test suite
  - Removed misleading "mock" designation that caused contributor confusion
  - Clear documentation establishes single source of truth for logging
  - No duplicate versions to maintain
  - Contributors now understand which code to modify

- **Developer Experience** ([#82](https://github.com/manoj-bhaskaran/expense-predictor/issues/82))
  - Clear usage examples in README for logging framework
  - Tests demonstrate proper logging framework usage patterns
  - Eliminated confusion between "mock" and "real" implementations
  - Single, well-documented logging framework

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Context**:
- Issue #82 requested clarification on python_logging_framework usage strategy
- The GitHub dependency was already removed in v1.9.0 (requirements.txt line 15-16)
- The local version was marked as "mock" with pragma: no cover comments
- This release completes the transition by updating documentation and adding tests

**Version Justification**:
- Patch version bump (1.12.0 → 1.12.1) per Semantic Versioning
- No functional changes to the logging framework code
- Documentation improvements and test additions only
- Removes technical debt (pragma comments)
- Clarifies existing functionality

**Test Coverage**:
- New tests: 22 tests for logging framework
- Total tests: 163 (up from 141)
- python_logging_framework.py coverage: 100%
- Overall project coverage: 89.15%
- All tests pass successfully

**Files Modified**:
- `python_logging_framework.py` (header updated, pragma comments removed)
- `tests/test_logging_framework.py` (new file with 22 tests)
- `README.md` (enhanced logging framework documentation)
- `CHANGELOG.md` (this file)

## [1.12.0] - 2025-11-15

### Added

- **Custom Exception Classes** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Created new `exceptions.py` module with custom exception hierarchy
  - Added `ExpensePredictorError` as base exception for all application errors
  - Added `DataValidationError` for data validation failures
  - Added `ConfigurationError` for configuration-related errors
  - Added `ModelTrainingError` for model training failures
  - All custom exceptions include comprehensive docstrings with usage examples
  - Exceptions preserve error context using `from` clause for better debugging

### Changed

- **Standardized Error Handling in config.py** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Replaced broad `except Exception` with specific exception handling (config.py:69-83)
  - Now catches `FileNotFoundError` and `PermissionError` separately for file access issues
  - Now catches `yaml.YAMLError` specifically for YAML parsing errors
  - Unexpected errors now raise `ConfigurationError` with preserved context instead of being silently caught
  - Improved error messages with actionable context
  - Falls back to default configuration for expected errors (file access, YAML parsing)

- **Standardized Error Handling in helpers.py** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Replaced all `ValueError`, `FileNotFoundError`, and `KeyError` with `DataValidationError` in validation functions
  - Updated `validate_csv_file()` to raise `DataValidationError` for all validation failures
  - Updated `validate_excel_file()` to raise `DataValidationError` with specific error types:
    - `xlrd.biffh.XLRDError` for corrupted .xls files
    - `ValueError` and `KeyError` for format errors from openpyxl/pandas
    - Generic exception handling for other unexpected errors
  - Updated `validate_date_range()` to raise `DataValidationError` for date validation failures
  - Updated `get_training_date_range()` to raise `DataValidationError` for NaT values
  - Updated `_process_dataframe()` to raise `DataValidationError` for non-numeric transaction amounts
  - Updated `prepare_future_dates()` to raise `DataValidationError` for invalid future dates
  - Updated `preprocess_and_append_csv()` to raise `DataValidationError` for missing Excel columns
  - All error messages now include context from original exceptions using `from` clause

- **Updated Function Docstrings** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Updated all validation function docstrings to document `DataValidationError` instead of generic exceptions
  - Improved docstrings to specify all scenarios that trigger exceptions
  - Added detailed exception documentation for better API clarity

### Improved

- **Error Debugging** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Specific exception types make it easier to identify the exact nature of errors
  - Exception chaining preserves full stack traces for root cause analysis
  - Clear error messages include relevant context (file paths, column names, etc.)
  - No more hidden bugs from overly broad exception handling

- **Code Quality** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Eliminated all broad `except Exception` clauses except where documented and necessary
  - Exceptions are now part of the API contract (documented in docstrings)
  - Better separation of concerns: specific exceptions for specific error categories
  - Follows Python best practices (PEP 8) for exception handling

- **Maintainability** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Centralized exception definitions in `exceptions.py` module
  - Easier to add new exception types in the future
  - Consistent error handling patterns across the codebase
  - Single source of truth for exception documentation

### Testing

- **Updated Test Suite** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Updated `tests/test_config.py` to test new `ConfigurationError` exception
  - Added test for `PermissionError` handling with fallback to defaults
  - Added test for unexpected errors raising `ConfigurationError` with preserved context
  - Updated `tests/test_helpers.py` to expect `DataValidationError` instead of generic exceptions
  - Updated 11 tests to validate new exception types
  - All tests verify exception messages contain expected context
  - Tests verify exception chaining preserves original errors

### Documentation

- **Exception Module Documentation** ([#81](https://github.com/manoj-bhaskaran/expense-predictor/issues/81))
  - Comprehensive module-level docstring in `exceptions.py` explaining exception hierarchy
  - Each exception class has detailed docstring with:
    - Purpose and use cases
    - Common scenarios that trigger the exception
    - Code examples demonstrating proper usage
  - Updated all function docstrings to document raised exceptions

### Notes

**Breaking Changes**: Potentially breaking for code that catches specific exception types.

**Migration Guide**:
- If your code catches `ValueError` from validation functions, update to catch `DataValidationError`
- If your code catches `FileNotFoundError` from validation functions, update to catch `DataValidationError`
- If your code catches `KeyError` from Excel processing, update to catch `DataValidationError`
- If your code relies on `config.load_config()` silently handling all errors, be aware that unexpected errors now raise `ConfigurationError`

**Version Justification**:
- Minor version bump (1.11.2 → 1.12.0) per Semantic Versioning
- Adds new feature (custom exception classes) with potential breaking changes
- Changes exception types raised by validation functions (breaking API change)
- Improves error handling without changing core functionality
- No changes to function signatures or return types

**Impact Analysis**:
- **Low risk** for most users: validation errors should be rare in production
- **Medium risk** for users with error handling: may need to update exception types
- **High value**: significantly improves debugging and error handling
- All existing functionality preserved (only exception types changed)

**Test Coverage**:
- All existing tests updated to use new exception types
- 2 new tests added for `ConfigurationError` handling
- Tests verify exception chaining and context preservation
- All tests pass with new exception handling

**Files Modified**:
- `exceptions.py` (new file)
- `config.py` (error handling improved)
- `helpers.py` (error handling standardized)
- `setup.py` (version bumped to 1.12.0, exceptions module added)
- `tests/test_config.py` (tests updated and added)
- `tests/test_helpers.py` (tests updated for new exception types)

## [1.11.2] - 2025-11-15

### Changed

- **Refactored Duplicate Date Range Logic** ([#80](https://github.com/manoj-bhaskaran/expense-predictor/issues/80))
  - Created new `get_training_date_range()` helper function in helpers.py (lines 195-247)
  - Removed duplicate date range calculation logic in `_process_dataframe()` (previously lines 224-234)
  - Removed duplicate date range calculation logic in `preprocess_and_append_csv()` (previously lines 362-364)
  - Both functions now use the shared helper function for DRY (Don't Repeat Yourself) principle
  - Single source of truth for date range calculation logic

### Added

- **New Helper Function** ([#80](https://github.com/manoj-bhaskaran/expense-predictor/issues/80))
  - `get_training_date_range()`: Calculates complete date range for training data
  - Parameters: DataFrame, optional date column name (default: 'Date'), optional logger
  - Returns: DatetimeIndex from earliest date in data to yesterday at midnight
  - Excludes today to avoid training on incomplete data
  - Comprehensive docstring explaining business logic and rationale
  - Proper error handling for invalid date ranges (NaT values)

- **Comprehensive Unit Tests** ([#80](https://github.com/manoj-bhaskaran/expense-predictor/issues/80))
  - Added 9 new unit tests for `get_training_date_range()` in tests/test_helpers.py
  - Tests cover: valid data, custom column names, NaT handling, today exclusion
  - Tests validate: time normalization, continuous ranges, single date edge case
  - Total test count increased from 131 to 139 tests (8 new tests)
  - All 139 tests pass successfully
  - Test coverage maintained at 89% (up from 88%)

### Improved

- **Code Maintainability** ([#80](https://github.com/manoj-bhaskaran/expense-predictor/issues/80))
  - Single source of truth: Date range logic defined once in `get_training_date_range()`
  - Better documentation: Comprehensive docstring explains why we exclude today's data
  - Easier testing: Date range logic tested once comprehensively with 9 dedicated tests
  - Easier maintenance: Changes to date range logic now made in one place
  - Reduced code duplication: ~13 lines of duplicate code eliminated

- **Code Quality** ([#80](https://github.com/manoj-bhaskaran/expense-predictor/issues/80))
  - Follows DRY (Don't Repeat Yourself) principle
  - Reduced technical debt from duplicate code
  - Lower risk of logic divergence between functions
  - Clearer intent: Function name explicitly states purpose
  - Better error messages: Centralized logging and error handling

### Documentation

- **Inline Documentation** ([#80](https://github.com/manoj-bhaskaran/expense-predictor/issues/80))
  - Detailed docstring for `get_training_date_range()` explains:
    - Why we exclude today's data (incomplete data, potential bias)
    - What the function returns (DatetimeIndex from earliest to yesterday)
    - When to use it (for creating training date ranges)
  - Example usage included in docstring
  - Parameters and return types fully documented

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Migration Guide**: No code changes required for users of the library. This is purely an internal refactoring.

**Version Justification**:
- Patch version bump (1.11.1 → 1.11.2) per Semantic Versioning
- Refactoring with no API changes or new features
- Internal code improvement for maintainability
- No functional changes to external behavior
- All existing tests continue to pass

**Test Coverage**:
- Tests: 139 (up from 131, +8 tests)
- Coverage: 89% (up from 88%)
- New tests specifically for `get_training_date_range()`: 9 tests
- All tests pass successfully

**Code Quality Metrics**:
- Duplicate code removed: ~13 lines across 2 functions
- New helper function: 53 lines (including comprehensive docstring)
- Net code reduction in duplication: Improved maintainability
- Cyclomatic complexity: Unchanged
- Code readability: Improved through better abstraction

## [1.11.1] - 2025-11-15

### Documentation

- **Console Entry Point Usage Documentation** ([#79](https://github.com/manoj-bhaskaran/expense-predictor/issues/79))
  - Updated README.md with comprehensive documentation for both usage methods
  - Added "Method 1: As an Installed Package (Recommended)" section demonstrating `expense-predictor` command
  - Added "Method 2: As a Python Script" section for direct Python execution
  - Updated all usage examples throughout README to prefer the console command
  - Updated Security section examples to use `expense-predictor` command
  - Updated Logging section examples to use `expense-predictor` command
  - Updated Troubleshooting section examples to use `expense-predictor` command
  - Clarified that users can run the tool either as an installed package or as a script

### Notes

**Breaking Changes**: None. This is a documentation-only release.

**Context**:
- Console entry point (`expense-predictor`) was defined in setup.py in v1.8.0
- `main()` function was implemented in v1.10.0 for testability
- Comprehensive CLI tests (21 tests) were added in v1.10.0
- This release completes the feature by documenting the console entry point usage
- Both execution methods remain fully supported and tested

**Version Justification**:
- Patch version bump (1.11.0 → 1.11.1) per Semantic Versioning
- Documentation-only change with no code modifications
- No functional changes or API modifications
- Improves user experience by documenting existing functionality

## [1.11.0] - 2025-11-15

### Added

- **Type Hints** ([#78](https://github.com/manoj-bhaskaran/expense-predictor/issues/78))
  - Added comprehensive type hints to all function signatures across the codebase
  - **security.py** (9 functions): All parameters and return types now have proper type hints
  - **config.py** (3 functions): Complete type annotations for configuration functions
  - **python_logging_framework.py** (5 functions): Type hints for all logging utility functions
  - **helpers.py** (17 functions): Complex pandas and datetime type annotations added
  - **model_runner.py** (6 functions): Full type coverage for CLI and model training functions
  - Created `mypy.ini` configuration file for type checking
  - All modules now pass mypy type checking with no errors

### Improved

- **IDE Support** ([#78](https://github.com/manoj-bhaskaran/expense-predictor/issues/78))
  - Enhanced autocomplete and inline documentation in modern IDEs
  - Better code navigation with type information
  - Improved parameter hints during function calls

- **Code Quality** ([#78](https://github.com/manoj-bhaskaran/expense-predictor/issues/78))
  - Type hints serve as inline documentation
  - Easier to understand function signatures and return types
  - Self-documenting code reduces need for external documentation

- **Developer Experience** ([#78](https://github.com/manoj-bhaskaran/expense-predictor/issues/78))
  - Catches type errors during development rather than runtime
  - Safer refactoring with type information
  - Clear API contracts for all functions
  - Better team collaboration with explicit type information

### Testing

- **Type Checking** ([#78](https://github.com/manoj-bhaskaran/expense-predictor/issues/78))
  - Added mypy type checking to development workflow
  - All 131 existing tests continue to pass
  - 88% test coverage maintained
  - No breaking changes to existing functionality

### Documentation

- **Type Annotations** ([#78](https://github.com/manoj-bhaskaran/expense-predictor/issues/78))
  - All function parameters now have clear type annotations
  - Return types explicitly documented
  - Optional parameters properly typed
  - Complex types (pandas DataFrames, Series, etc.) fully annotated

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Migration Guide**:
- No code changes required for existing users
- Type hints are purely for development-time checks
- All existing code continues to work unchanged
- To benefit from type checking, install mypy: `pip install mypy`

**Version Justification**:
- Minor version bump (1.10.1 → 1.11.0) per Semantic Versioning
- Adds new development feature (type hints) without breaking changes
- Enhances code quality and developer experience
- No API or behavior modifications
- Backward-compatible enhancement only

**Type Coverage**:
- **security.py**: 9/9 functions (100%)
- **config.py**: 3/3 functions (100%)
- **python_logging_framework.py**: 5/5 functions (100%)
- **helpers.py**: 17/17 functions (100%)
- **model_runner.py**: 6/6 functions (100%)
- **Total**: 40/40 functions with complete type hints

## [1.10.1] - 2025-11-15

### Fixed

- **Coverage Documentation Update** ([#77](https://github.com/manoj-bhaskaran/expense-predictor/issues/77))
  - Updated README.md with current test coverage: **88%** (was documented as 82.66%)
  - Updated coverage breakdown to reflect latest test results:
    - `helpers.py`: Now **88%** (up from 76%)
  - Verified CI/CD coverage threshold (80%) is met and passing
  - Confirmed all 131 tests pass successfully
  - Clarified that coverage mismatch issue from #77 was already resolved in v1.10.0
  - No code changes needed - coverage already exceeds requirements

### Changed

- **Version Alignment** ([#77](https://github.com/manoj-bhaskaran/expense-predictor/issues/77))
  - Updated setup.py version to 1.10.0 to match CHANGELOG

## [1.10.0] - 2025-11-15

### Fixed

- **Coverage Configuration - model_runner.py Included** ([#76](https://github.com/manoj-bhaskaran/expense-predictor/issues/76))
  - Removed `model_runner.py` from `.coveragerc` omit list (line 12)
  - Main orchestration logic now properly tracked in coverage reports
  - Addresses misleading coverage metrics that excluded the most critical file
  - Improved confidence in main execution flow correctness
  - Coverage reporting now reflects actual code coverage accurately

### Added

- **Comprehensive CLI Integration Tests** ([#76](https://github.com/manoj-bhaskaran/expense-predictor/issues/76))
  - Created `tests/test_model_runner_cli.py` with 21 new integration tests
  - Tests for CLI argument parsing with various combinations
  - Tests for main execution flow with different configurations
  - Tests for error handling (invalid paths, dates, missing files)
  - Tests for all 4 ML models (Linear Regression, Decision Tree, Random Forest, Gradient Boosting)
  - Tests for prediction file generation and content validation
  - Tests for logging integration
  - Total of 131 tests now in the test suite (up from 110)

### Changed

- **Refactored model_runner.py for Testability** ([#76](https://github.com/manoj-bhaskaran/expense-predictor/issues/76))
  - Extracted `parse_args(args=None)` function for argument parsing
  - Created `main(args=None)` function as entry point
  - Added `if __name__ == '__main__'` guard for script execution
  - Enabled unit testing of CLI without running full pipeline
  - Improved code organization and maintainability
  - No breaking changes - script still works identically from command line

### Improved

- **Test Coverage Metrics** ([#76](https://github.com/manoj-bhaskaran/expense-predictor/issues/76))
  - **Total coverage increased from 43% to 82.66%** (39.66 percentage points improvement)
  - `model_runner.py` coverage: **87%** (was 0% when excluded)
  - `config.py` coverage: **100%**
  - `helpers.py` coverage: **76%**
  - `security.py` coverage: **85%**
  - All files now meet or exceed the 80% coverage requirement
  - Coverage enforcement now applies to actual codebase
  - CI/CD pipeline now validates real code quality

### Security

- **Enhanced Testing of Security Features** ([#76](https://github.com/manoj-bhaskaran/expense-predictor/issues/76))
  - CLI tests validate path injection protection
  - Tests verify file extension validation
  - Tests confirm CSV injection prevention in outputs
  - Tests ensure proper error handling for invalid inputs
  - Increased confidence in security feature effectiveness

### Documentation

- **README.md Updates** ([#76](https://github.com/manoj-bhaskaran/expense-predictor/issues/76))
  - Updated test coverage from 43% to 82.66%
  - Documented that model_runner.py is now included in coverage
  - Reflects accurate code quality metrics

### Notes

**Breaking Changes**: None. This is a backward-compatible release.

**Migration Guide**:
- No code changes required for existing users
- Script usage remains identical
- To update: `pip install -r requirements.txt`

**Version Justification**:
- Minor version bump (1.9.0 → 1.10.0) per Semantic Versioning
- Significant improvement to test infrastructure and coverage
- Added new test functionality (CLI integration tests)
- Improved code quality and maintainability
- Backward-compatible changes only
- No API or behavior modifications

**Coverage Impact**:
- Initial reported coverage of 43% excluded the main entry point file
- New coverage of 82.66% accurately reflects actual code coverage
- This is a **39.66 percentage point improvement** in real coverage
- Project now exceeds the 80% CI/CD requirement

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
