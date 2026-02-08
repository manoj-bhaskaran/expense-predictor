# Changelog

All notable changes to the Expense Predictor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.21.0] - 2026-02-08

### Fixed
- **Time-Series Train/Test Leakage**: Replaced sklearn `train_test_split` with explicit chronological splitting to prevent data leakage in time-dependent expense data. New `chronological_train_test_split` function enforces strict temporal ordering: first 80% of data for training, last 20% for testing, with validation that dates are strictly increasing (no duplicates). Train/test date boundaries are now logged explicitly for transparency.

### Added
- `chronological_train_test_split()` function in helpers.py for time-aware data splitting with date boundary logging, chronological order validation, and duplicate date detection.
- Unit tests for chronological splitting (`TestChronologicalTrainTestSplit`: 8 tests) covering split ratio, temporal ordering, unsorted data rejection, duplicate date rejection, and various test sizes.
- Leakage detection tests (`TestFutureDataLeakage`: 5 tests) verifying no future targets in training, features are date-intrinsic, strict date boundaries, no shuffling, and full pipeline integration.

### Impact
- **Severity**: Critical | **Type**: Bug Fix | **Breaking Changes**: None (evaluation behavior improved)
- Default evaluation split is now strictly chronological. Models never access future target values or features during evaluation. Negative test R² values from inappropriate splitting are resolved.

### Technical Details
- Removed `sklearn.model_selection.train_test_split` dependency from model_runner.py. Split index calculated as `n_samples - int(n_samples * test_size)`. Upfront validation rejects non-monotonic or duplicate date sequences with `DataValidationError`, replacing the previous unreliable post-split overlap check. The upstream pipeline guarantees one row per date via `drop_duplicates` and date-range reindexing; the split function validates this invariant defensively. Version bump 1.20.1 → 1.21.0 (minor) for new function and behavior change.

## [1.20.1] - 2025-11-16

### Changed
- **Condensed and Normalized CHANGELOG** ([#116](https://github.com/manoj-bhaskaran/expense-predictor/issues/116)): Manually condensed CHANGELOG from 109,545 to 13,054 characters (88% reduction) to meet project requirements. All individual entries now ≤400 words. Retained last 5 minor versions (1.16-1.20) as separate entries. Condensed older minors (1.0-1.15) into single summary entry. Improved readability while preserving chronological order and key information.

### Impact
- **Type**: Documentation | **Breaking Changes**: None
- CHANGELOG now manageable and maintainable. Easier to navigate recent changes while preserving historical context in condensed form.

## [1.20.0] - 2025-11-16

### Added
- **Comprehensive Test Coverage Audit** ([#122](https://github.com/manoj-bhaskaran/expense-predictor/issues/122)): Conducted full coverage audit achieving 87.85% coverage (571/650 statements). Generated comprehensive HTML and XML reports. Created `.coveragerc-audit` configuration for periodic audits. Added detailed audit documentation (`coverage-audit/COVERAGE_AUDIT_SUMMARY.md`) breaking down coverage by file and categorizing 79 missing statements by type (error handling, edge cases, validation, security). Verified minimal and appropriate exclusion rules.

### Documentation
- Added "Coverage Auditing" section to CONTRIBUTING.md with comprehensive guidelines for running audits, interpreting reports, managing exclusions, and testing error paths. Documented quarterly review process and best practices for security code testing.

### Impact
- **Severity**: Medium | **Type**: Documentation/Tooling/QA | **Breaking Changes**: None
- **Benefits**: Transparency into actual coverage, prioritized testing roadmap, prevents coverage exclusions from hiding untested code, highlighted security code needing better tests

### Technical Details
- 204 tests passing, 11.97s execution time. Identified critical follow-up: security path validation tests (CRITICAL), error handling tests (HIGH), Excel edge cases (MEDIUM), user interaction tests (LOW). Version bump justified as minor (1.19.0 → 1.20.0) for new development tooling and substantial documentation improvements.

## [1.19.0] - 2025-11-16

### Added
- **Pydantic Type Validation for config.yaml** ([#112](https://github.com/manoj-bhaskaran/expense-predictor/issues/112)): Implemented strict type checking for all configuration parameters to prevent runtime errors. Created validation models for LoggingConfig (log levels), DataProcessingConfig (skiprows ≥0), ModelEvaluationConfig (test_size 0.0-1.0, random_state ≥0), and all ML model hyperparameters (DecisionTree, RandomForest, GradientBoosting). Added 13 comprehensive validation tests covering invalid types, out-of-range values, invalid enums, and multiple errors.

### Impact
- **Severity**: High | **Type**: Feature/Enhancement | **Breaking Changes**: None
- **Benefits**: Fail-fast at startup with clear error messages instead of cryptic runtime errors (e.g., "expected integer, got 'five'" vs "TypeError: '<=' not supported"). Self-documenting schemas, type safety with strict mode, range validation, better debugging for non-technical users.

### Technical Details
- Files modified: `config.py` (Pydantic models), `requirements.txt` (pydantic==2.10.3), `tests/test_config.py` (13 validation tests). All 27 config tests pass. Version bump (1.18.3 → 1.19.0) justified as minor for new type validation capability.

## [1.18.0 → 1.18.3] - 2025-11-16

### Summary
Four patch releases focused on data validation, code quality improvements, and dependency management.

### Added
- **Minimum Data Validation** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108)): validate_minimum_data() function validating sufficient training data (min 30 total, 10 test samples). Configurable thresholds via config.yaml. Prevents crashes with clear error messages. Added "Data Requirements" section to README.

### Changed
- **Deprecated pandas API** ([#111](https://github.com/manoj-bhaskaran/expense-predictor/issues/111)): Removed all inplace=True uses, replaced with method chaining. Future-proof for pandas 3.0+.
- **Constants Module** ([#110](https://github.com/manoj-bhaskaran/expense-predictor/issues/110)): Created constants.py for centralized definitions. Moved TRANSACTION_AMOUNT_LABEL, VALUE_DATE_LABEL, DAY_OF_WEEK. Single source of truth.

### Fixed
- **line-profiler Version** ([#109](https://github.com/manoj-bhaskaran/expense-predictor/issues/109)): Updated to 4.1.3 in setup.py, matching requirements-dev.txt. Ensures consistent dev environments.

### Impact
Critical data validation enhancement. High-impact code quality improvements. All changes backward compatible.

## [1.17.0 → 1.17.2] - (2025-11-15 → 2025-11-16)

### Summary
Three patch releases adding Python 3.12 support and fixing critical Excel processing issues.

### Added
- **Python 3.12 Support** ([#87](https://github.com/manoj-bhaskaran/expense-predictor/issues/87)): Added to CI/CD test matrix. All 163 tests pass on Python 3.9-3.12. Updated line-profiler to 4.1.3 for Python 3.12 compatibility. Updated README.

### Fixed
- **Missing Production Dependency** ([#106](https://github.com/manoj-bhaskaran/expense-predictor/issues/106)): Added openpyxl==3.1.2 to requirements.txt and setup.py. Fixes ModuleNotFoundError for .xlsx processing in production.
- **Excel Error Handling** ([#107](https://github.com/manoj-bhaskaran/expense-predictor/issues/107)): Added explicit ImportError handling with installation instructions for missing openpyxl.

### Documentation
- Added "Excel File Support" section to README clarifying .xls (xlrd) vs .xlsx (openpyxl) distinction with format detection and usage examples.

### Impact
Python 3.12 support (new feature). Critical dependency fix for .xlsx files. Improved error messages for Excel processing.

## [1.16.0] - 2025-11-16

### Added
- **Configurable Log Levels**: Added `--log-level` CLI argument with choices (DEBUG, INFO, WARNING, ERROR, CRITICAL), `EXPENSE_PREDICTOR_LOG_LEVEL` environment variable support, and logging configuration in config.yaml. Priority order: CLI > environment > config > default (INFO). Automatic validation with graceful fallback to INFO for invalid values.

### Impact
- **Type**: Feature | **Breaking Changes**: None
- Enhanced logging flexibility for development, production, and CI/CD. Improved debugging capabilities with configurable verbosity.

## [1.0.0 → 1.15.0] - (2025-11-14 → 2025-11-15)

### Summary
Foundational development from initial release through comprehensive testing, security, CI/CD infrastructure, and developer experience improvements.

### Major Additions
- **1.15.0**: Pre-commit hooks (.pre-commit-config.yaml) with black, isort, flake8, mypy, bandit, yamllint for automatic code quality checks before commits.
- **1.14.0**: Environment variable configuration via .env files (python-dotenv). Variables: DATA_FILE, EXCEL_DIR, EXCEL_FILE, LOG_DIR, OUTPUT_DIR, FUTURE_DATE, SKIP_CONFIRMATION. Priority: CLI > env > config > defaults.
- **1.13.0**: Pytest markers (@pytest.mark.unit, .integration, .slow, .validation) for selective test execution. Staged CI/CD testing for faster feedback.
- **1.12.0-1.12.1**: Logging framework tests (22 tests, 100% coverage for python_logging_framework.py). Enhanced documentation.
- **1.11.0-1.11.2**: Enhanced data processing with normalization, flexible column detection, feature engineering. Extensive unit tests.
- **1.10.0-1.10.1**: Improved Excel integration with robust column matching and error handling for varying bank statement formats.
- **1.9.0**: Removed external GitHub dependency, made local python_logging_framework official.
- **1.8.0-1.8.1**: Enhanced model evaluation metrics with separate train/test reporting and improved logging format.
- **1.7.0**: CI/CD pipeline (test.yml) with multi-Python version testing and 80% coverage enforcement.
- **1.6.0**: Security scanning workflow (Bandit, Safety) with scheduled weekly scans and automated vulnerability detection.
- **1.5.0**: Testing framework (pytest/pytest-cov/pytest-mock). 57 initial tests, 43% coverage. Test structure with conftest.py, test data, fixtures.
- **1.4.0**: Security module (security.py) with path validation, CSV injection prevention, backups, user confirmations, --skip_confirmation flag.
- **1.3.0-1.3.1**: Standardized logging (replaced print() with plog), comprehensive pipeline logging, optimized categorical handling.
- **1.2.0**: Input validation (validate_csv_file, validate_excel_file, validate_date_range) for early error detection with clear messages.
- **1.1.0**: Configuration system (config.yaml, config.py) centralizing parameters (data processing, model hyperparameters). Graceful defaults.
- **1.0.0-1.0.5**: Initial release with four ML models (Linear Regression, Decision Tree, Random Forest, Gradient Boosting), CSV/Excel processing, feature engineering, CLI, logging, metrics (RMSE, MAE, R²). Fixes for dependencies, train/test split, column renaming, data mutation.

### Infrastructure & Quality
Complete CI/CD pipeline (testing, pre-commit, security, Dependabot). Test coverage: 43% (v1.5.0) to 89%+ (v1.12.1+). Security: multi-layer scanning, path/CSV injection protection. Developer experience: pre-commit hooks, selective tests, env vars, comprehensive docs.

### Breaking Changes
None - all releases backward compatible

### Technical Stack
Dependencies: pytest, pytest-cov, pytest-mock, pydantic, python-dotenv, pre-commit, line-profiler, bandit. Python 3.9-3.12. Core: scikit-learn, pandas, numpy.

---

## How to Report Issues

If you encounter bugs or have feature requests, please open an issue on the [GitHub repository](https://github.com/manoj-bhaskaran/expense-predictor/issues).

Include: version number, OS and Python version, complete error messages, reproduction steps, anonymized sample data if relevant.

---

[Unreleased]: https://github.com/manoj-bhaskaran/expense-predictor/compare/v1.21.0...HEAD
[1.21.0]: https://github.com/manoj-bhaskaran/expense-predictor/compare/v1.20.1...v1.21.0
[1.20.1]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.20.1
[1.20.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.20.0
[1.19.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.19.0
[1.18.0 → 1.18.3]: https://github.com/manoj-bhaskaran/expense-predictor/compare/v1.18.0...v1.18.3
[1.17.0 → 1.17.2]: https://github.com/manoj-bhaskaran/expense-predictor/compare/v1.17.0...v1.17.2
[1.16.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.16.0
[1.0.0 → 1.15.0]: https://github.com/manoj-bhaskaran/expense-predictor/compare/v1.0.0...v1.15.0
