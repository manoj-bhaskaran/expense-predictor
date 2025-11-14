# Expense Predictor

A machine learning-based expense prediction system that analyzes historical transaction data to forecast future expenses. The project uses multiple regression models to predict transaction amounts for specified future dates.

## Features

- **Multiple ML Models**: Supports Linear Regression, Decision Tree, Random Forest, and Gradient Boosting algorithms
- **Flexible Data Input**: Works with CSV transaction data and optionally integrates Excel bank statements
- **Robust Input Validation**: Validates file existence, format, required columns, and date ranges before processing
- **Automated Predictions**: Generates predictions for custom future dates or automatically for the current quarter end
- **Comprehensive Logging**: Built-in logging framework for tracking operations and debugging
- **Performance Metrics**: Evaluates models using RMSE, MAE, and R-squared metrics
- **Portable**: Supports both absolute and relative file paths for flexible deployment

## Requirements

- Python 3.7 or higher
- Git (required for installing dependencies from GitHub)
- See `requirements.txt` for package dependencies

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

## Project Structure

```
expense-predictor/
├── model_runner.py          # Main script for model training and prediction
├── helpers.py               # Helper functions for data preprocessing
├── config.py                # Configuration loader module
├── config.yaml              # Configuration file for hyperparameters
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example            # Example environment configuration
├── README.md               # This file
├── LICENSE                 # MIT License
├── CHANGELOG.md            # Version history
├── DATA.md                 # Data format documentation
└── .github/
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

Logs are automatically saved to the `logs/` directory with timestamps. Log files include:
- Model training progress
- Data preprocessing steps
- Error messages and warnings
- Prediction results

## Development

### Running Tests

```bash
# Install development dependencies first
pip install -r requirements-dev.txt

# Run tests (when test suite is available)
pytest tests/
```

### Code Style

The project follows PEP 8 style guidelines. Use a linter to check code quality:

```bash
flake8 model_runner.py helpers.py
```

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
