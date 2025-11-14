# Data Documentation

This document describes the data formats and requirements for the Expense Predictor system.

## Table of Contents

- [CSV Transaction Data Format](#csv-transaction-data-format)
- [Excel Bank Statement Format](#excel-bank-statement-format)
- [Sample Data Examples](#sample-data-examples)
- [Data Preprocessing](#data-preprocessing)
- [Data Requirements](#data-requirements)

## CSV Transaction Data Format

The primary input format is a CSV file containing transaction history.

### Required Columns

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `Date` | Date | Transaction date | `01/01/2024` |
| `Tran Amt` | Numeric | Transaction amount | `150.00` |

### CSV Format Specifications

- **File Encoding**: UTF-8
- **Date Format**: Flexible - supports DD/MM/YYYY, MM/DD/YYYY, and other common formats
- **Decimal Separator**: Period (`.`)
- **Missing Values**: Will be handled by the preprocessing pipeline

### Sample CSV Structure

```csv
Date,Tran Amt
01/01/2024,150.00
02/01/2024,75.50
03/01/2024,200.00
04/01/2024,0.00
05/01/2024,325.75
06/01/2024,89.99
```

### Creating Sample Data

To create a sample `trandata.csv` file:

```csv
Date,Tran Amt
01/01/2024,120.50
02/01/2024,95.00
03/01/2024,150.75
04/01/2024,200.00
05/01/2024,85.25
06/01/2024,175.00
07/01/2024,140.50
08/01/2024,95.75
09/01/2024,210.00
10/01/2024,130.25
11/01/2024,165.50
12/01/2024,190.00
13/01/2024,110.75
14/01/2024,145.00
15/01/2024,175.50
```

## Excel Bank Statement Format

Optionally, you can provide bank statement data in Excel format (.xls or .xlsx).

### Required Columns

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `Value Date` | Date | Transaction date | `01/01/2024` |
| `Withdrawal Amount (INR )` | Numeric | Withdrawal amount | `500.00` |
| `Deposit Amount (INR )` | Numeric | Deposit amount | `1000.00` |

### Excel Format Specifications

- **File Format**: Excel 97-2003 (.xls) or Excel 2007+ (.xlsx)
- **Sheet**: First sheet is processed (you can have multiple sheets, but only the first is used)
- **Header Row**: Row 13 (rows 1-12 are skipped as they typically contain bank header information)
- **Column Names**: Flexible matching - the system can handle slight variations in spacing around parentheses

### Column Name Variations

The system supports flexible column name matching. These variations are all acceptable:

- `Value Date` or `ValueDate`
- `Withdrawal Amount (INR )` or `Withdrawal Amount (INR)` or `Withdrawal Amount(INR)`
- `Deposit Amount (INR )` or `Deposit Amount (INR)` or `Deposit Amount(INR)`

### Excel Processing

The system will:
1. Read the first sheet
2. Skip the first 12 rows (typical bank header)
3. Calculate expenses: `expense = (withdrawal × -1) + deposit`
4. Aggregate transactions by date
5. Merge with CSV data

## Sample Data Examples

### Example 1: Simple Daily Expenses

```csv
Date,Tran Amt
01/01/2024,50.00
02/01/2024,75.00
03/01/2024,100.00
04/01/2024,50.00
05/01/2024,125.00
```

### Example 2: Mixed Positive and Negative Values

```csv
Date,Tran Amt
01/01/2024,-50.00
02/01/2024,200.00
03/01/2024,-100.00
04/01/2024,150.00
05/01/2024,-75.00
```

Note: Negative values represent withdrawals/expenses, positive values represent deposits/income.

### Example 3: Irregular Intervals

```csv
Date,Tran Amt
01/01/2024,100.00
05/01/2024,150.00
10/01/2024,200.00
15/01/2024,125.00
25/01/2024,175.00
```

The system will automatically fill missing dates with 0 transaction amounts.

## Data Preprocessing

The system performs several preprocessing steps automatically:

### 1. Data Cleaning

- **Duplicate Removal**: Keeps the last occurrence if multiple transactions exist for the same date
- **Missing Date Handling**: Rows with invalid or missing dates are removed
- **Data Type Validation**: Ensures `Tran Amt` contains only numeric values

### 2. Date Completion

The system creates a complete date range from the earliest transaction to yesterday:

- **Start Date**: Minimum date in the dataset
- **End Date**: Yesterday (excludes today and future dates)
- **Missing Dates**: Filled with 0 transaction amount

### 3. Feature Engineering

The following features are automatically created:

| Feature | Description | Example |
|---------|-------------|---------|
| `Day of the Week` | Day name | Monday, Tuesday, etc. |
| `Month` | Month number | 1-12 |
| `Day of the Month` | Day of month | 1-31 |

These features are then one-hot encoded for model training.

### 4. Data Normalization

- Dates are converted to `datetime` objects
- All date formats are standardized
- Time components are removed (only date is used)

## Data Requirements

### Minimum Requirements

- **Rows**: At least 30 days of historical data recommended
- **Time Period**: Longer historical periods improve prediction accuracy
- **Data Quality**: Clean, consistent transaction records

### Best Practices

1. **Historical Depth**: 3-6 months of data provides better predictions
2. **Consistency**: Regular daily transactions improve model performance
3. **Completeness**: More complete data reduces preprocessing gaps
4. **Accuracy**: Verify transaction amounts are correct before processing

### Known Limitations

- **Future Dates**: Dates in the future are excluded during preprocessing
- **Today's Date**: Today's date is excluded (only historical data is used)
- **Missing Days**: Automatically filled with zero - ensure this is appropriate for your use case
- **Single Currency**: The system assumes all amounts are in the same currency

## Data Privacy and Security

### Recommendations

1. **Never commit real financial data** to version control
2. Add data files to `.gitignore`:
   ```
   trandata.csv
   *.xls
   *.xlsx
   /data/*
   ```
3. Use sample/anonymized data for testing
4. Store sensitive data outside the repository
5. Use environment variables for data file paths in production

## Generating Test Data

For testing purposes, you can generate synthetic transaction data:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate 180 days of sample data
start_date = datetime.now() - timedelta(days=180)
dates = pd.date_range(start=start_date, periods=180, freq='D')

# Generate random transaction amounts (0-500)
amounts = np.random.uniform(0, 500, size=180)

# Create DataFrame
df = pd.DataFrame({
    'Date': dates.strftime('%d/%m/%Y'),
    'Tran Amt': np.round(amounts, 2)
})

# Save to CSV
df.to_csv('trandata.csv', index=False)
print("Sample data created: trandata.csv")
```

## Troubleshooting Data Issues

### Common Data Problems

**Problem**: "The 'Tran Amt' column contains non-numeric values"
- **Cause**: Special characters or text in amount column
- **Solution**: Clean the data to ensure only numeric values

**Problem**: "Value Date column not found"
- **Cause**: Excel file has different column names
- **Solution**: Ensure column headers match expected names or supported variations

**Problem**: "Invalid start or end date found"
- **Cause**: All dates are invalid or in the wrong format
- **Solution**: Verify date format and ensure dates are valid

**Problem**: Predictions seem inaccurate
- **Cause**: Insufficient historical data or irregular patterns
- **Solution**: Provide at least 90 days of historical data for better predictions

## Support

For data-related questions or issues, please open an issue on the [GitHub repository](https://github.com/manoj-bhaskaran/expense-predictor/issues) with:
- Sample of your data structure (anonymized)
- Error messages encountered
- Steps to reproduce the issue
