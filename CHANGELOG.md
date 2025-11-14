# Changelog

All notable changes to the Expense Predictor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Version number (1.0.0)
- Operating system and Python version
- Complete error messages
- Steps to reproduce the issue
- Sample data (anonymized) if relevant

---

## Contributors

- Manoj Bhaskaran - Initial development and release

---

[1.0.0]: https://github.com/manoj-bhaskaran/expense-predictor/releases/tag/v1.0.0
