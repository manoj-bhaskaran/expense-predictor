# Changelog

All notable changes to the Expense Predictor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

## [1.18.3] - 2025-11-16

### Changed
- **Replace Deprecated pandas inplace=True** ([#111](https://github.com/manoj-bhaskaran/expense-predictor/issues/111)): Removed all `inplace=True` parameter uses in helpers.py, replacing with assignment and method chaining (lines 354-358, 502, 512-516). Future-proofs for pandas 3.0+ and follows modern best practices.

### Impact
- **Severity**: High | **Type**: Refactoring/Future Compatibility | **Breaking Changes**: None
- Purely internal refactoring with identical functionality, improved code clarity, removes potential deprecation warnings.

## [1.18.2] - 2025-11-16

### Changed
- **Consolidate Constants into Single Module** ([#110](https://github.com/manoj-bhaskaran/expense-predictor/issues/110)): Created `constants.py` module for centralized constant definitions. Moved `TRANSACTION_AMOUNT_LABEL`, `VALUE_DATE_LABEL`, and `DAY_OF_WEEK` from helpers.py. Removed duplicate `TRANSACTION_AMOUNT_LABEL` from model_runner.py. Establishes single source of truth, prevents DRY violations.

### Impact
- **Severity**: High | **Type**: Code Quality/Refactoring | **Breaking Changes**: None
- All 191 tests pass. Version bump (1.18.1 → 1.18.2) for internal refactoring improving maintainability.

## [1.18.1] - 2025-11-16

### Fixed
- **Line Profiler Version Consistency** ([#109](https://github.com/manoj-bhaskaran/expense-predictor/issues/109)): Updated line-profiler from 4.1.0 to 4.1.3 in setup.py extras_require, resolving version mismatch with requirements-dev.txt. Ensures consistent development environments across installation methods. Version 4.1.3 required for Python 3.12 compatibility.

### Impact
- **Severity**: High | **Type**: Bug Fix | **Breaking Changes**: None
- Both `pip install -e .[dev]` and `pip install -r requirements-dev.txt` now install line-profiler==4.1.3.

## [1.18.0] - 2025-11-16

### Added
- **Minimum Data Validation Before Model Training** ([#108](https://github.com/manoj-bhaskaran/expense-predictor/issues/108)): Added `validate_minimum_data()` function (helpers.py:214-257) validating sufficient training data before model training. Validates minimum total samples (default: 30) and minimum test samples (default: 10) after split. Prevents runtime errors with clear, actionable error messages. Added configurable thresholds via `min_total_samples` and `min_test_samples` in config.yaml.

### Documentation
- Added "Data Requirements" section to README.md documenting minimum sample requirements (30 total, 10 test), configurable thresholds, and recommendations (100+ transactions for best results).

### Impact
- **Severity**: Critical | **Type**: Feature/Enhancement | **Breaking Changes**: None
- Prevents crashes during train_test_split with insufficient data. Validation happens early before expensive computation. Version bump (1.17.2 → 1.18.0) justified as minor for new data validation capability.

## [1.17.2] - 2025-11-16

### Fixed
- **Enhanced Error Handling for Excel Processing** ([#107](https://github.com/manoj-bhaskaran/expense-predictor/issues/107)): Added explicit ImportError handling for missing openpyxl dependency with installation instructions (helpers.py:108-118, 414-424). Better error messages prevent confusion when processing .xlsx files without openpyxl.

### Documentation
- Added "Excel File Support" section to README.md clarifying distinction between .xls (xlrd 2.0.1) and .xlsx (openpyxl 3.1.2) formats. Documented automatic format detection and usage examples.

### Impact
- **Severity**: Low | **Type**: Bug Fix/Documentation | **Breaking Changes**: None

## [1.17.1] - 2025-11-16

### Fixed
- **Missing Production Dependency** ([#106](https://github.com/manoj-bhaskaran/expense-predictor/issues/106)): Added `openpyxl==3.1.2` to production dependencies (requirements.txt, setup.py). Resolves critical issue where .xlsx processing failed in production (openpyxl was only in dev dependencies). Fixes `ModuleNotFoundError: No module named 'openpyxl'`.

### Impact
- **Severity**: Critical | **Type**: Bug Fix | **Breaking Changes**: None
- Production installations can now process .xlsx files without manual dependency installation.

## [1.17.0] - 2025-11-15

### Added
- **Python 3.12 Support** ([#87](https://github.com/manoj-bhaskaran/expense-predictor/issues/87)): Added Python 3.12 to CI/CD test matrix. All tests now run on Python 3.9, 3.10, 3.11, and 3.12. Updated coverage reporting to use Python 3.12. Verified all dependencies compatible with 3.12.

### Fixed
- Updated line-profiler from 4.1.0 to 4.1.3 in requirements-dev.txt to resolve Cython dependency conflict preventing Python 3.12 installation.

### Documentation
- Updated README.md to include Python 3.12 in requirements section and version badge.

### Impact
- **Severity**: Medium | **Type**: Feature | **Breaking Changes**: None
- All 163 tests pass on Python 3.12. Version bump (1.16.0 → 1.17.0) for new Python version support.

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

[Unreleased]: https://github.com/manoj-bhaskaran/expense-predictor/compare/v1.20.1...HEAD
[1.20.1]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.20.1
[1.20.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.20.0
[1.19.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.19.0
[1.18.3]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.18.3
[1.18.2]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.18.2
[1.18.1]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.18.1
[1.18.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.18.0
[1.17.2]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.17.2
[1.17.1]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.17.1
[1.17.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.17.0
[1.16.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.16.0
[1.0.0 → 1.15.0]: https://github.com/manoj-bhaskaran/expense-predictor/compare/v1.0.0...v1.15.0
