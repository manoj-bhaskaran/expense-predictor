# Expense Predictor

A machine learning-based expense prediction system that analyzes historical transaction data to forecast future expenses. The project uses multiple regression models to predict transaction amounts for specified future dates.

## Features

- **Multiple ML Models**: Supports Linear Regression, Decision Tree, Random Forest, and Gradient Boosting algorithms
- **Flexible Data Input**: Works with CSV transaction data and optionally integrates Excel bank statements
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

The project can be configured using command-line arguments. No environment variables are strictly required, but you can create a `.env` file based on `.env.example` for custom default paths.

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

The script evaluates each model using:
- **RMSE (Root Mean Squared Error)**: Measures prediction accuracy
- **MAE (Mean Absolute Error)**: Average absolute prediction error
- **R-squared**: Proportion of variance explained by the model

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

## Troubleshooting

### Common Issues

**Issue**: `KeyError` when reading Excel files
- **Solution**: Ensure Excel file has correct column names. The script supports flexible column name matching, but column headers should include "Value Date", "Withdrawal Amount", and "Deposit Amount"

**Issue**: `ValueError: Incorrect date format`
- **Solution**: Ensure dates are in DD/MM/YYYY format when using `--future_date`

**Issue**: Import errors for `python_logging_framework`
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Predictions seem inaccurate
- **Solution**: Check that your training data has sufficient historical data (at least several months recommended). Review log files for model performance metrics.

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
