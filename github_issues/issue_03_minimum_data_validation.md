# Add Minimum Data Validation Before Model Training

## Summary
There's no validation to ensure sufficient training data exists before attempting to train models. With very small datasets, model training could fail or produce meaningless results.

## Impact
- **Severity:** Critical
- Runtime errors with insufficient data
- Poor model performance not detected
- Confusing error messages for users
- Waste of computation on data that can't produce valid models

## Current Behavior
The code proceeds to train models even with 1-2 data points, which will either:
1. Crash during train_test_split (if only 1 sample exists)
2. Produce meaningless results (if 2-5 samples exist)
3. Overfit severely (if 5-20 samples exist)

## Expected Behavior
The system should validate minimum data requirements and provide clear error messages:
- Minimum absolute samples (e.g., 20-30 for meaningful ML)
- Minimum after train/test split (e.g., 10 for test set)
- Clear error message guiding users on data requirements

## Technical Details

**Affected Files:**
- `model_runner.py:407` (train_test_split without validation)
- `helpers.py` (data processing functions)

**Current Code:**
```python
# model_runner.py:407
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, shuffle=False, random_state=random_state
)
```

No validation before this line.

## Reproduction Steps
1. Create a CSV with only 2-3 transactions
2. Run: `python model_runner.py --data_file small.csv`
3. Observe either crash or meaningless results

## Proposed Solution

### 1. Add Validation Function
```python
def validate_minimum_data(X: pd.DataFrame, y: pd.Series,
                         min_total: int = 30,
                         min_test: int = 10,
                         logger: Optional[logging.Logger] = None) -> None:
    """
    Validate that sufficient data exists for training.

    Args:
        X: Feature dataframe
        y: Target series
        min_total: Minimum total samples required
        min_test: Minimum test samples required after split
        logger: Logger instance

    Raises:
        DataValidationError: If insufficient data
    """
    total_samples = len(X)

    if total_samples < min_total:
        msg = (
            f"Insufficient data for training: {total_samples} samples found, "
            f"but at least {min_total} samples are recommended for meaningful predictions. "
            f"Please provide more historical transaction data."
        )
        plog.log_error(logger, msg)
        raise DataValidationError(msg)

    # Check if test set will have enough samples
    test_size = config["model_evaluation"]["test_size"]
    expected_test_samples = int(total_samples * test_size)

    if expected_test_samples < min_test:
        msg = (
            f"Insufficient test data: with {total_samples} total samples and "
            f"test_size={test_size}, only {expected_test_samples} test samples "
            f"will be available. At least {min_test} are recommended. "
            f"Consider reducing test_size in config.yaml or adding more data."
        )
        plog.log_error(logger, msg)
        raise DataValidationError(msg)

    plog.log_info(logger,
                  f"Data validation passed: {total_samples} total samples, "
                  f"~{expected_test_samples} test samples")
```

### 2. Add Call in main()
```python
# In main(), after line 402:
X, y, _ = preprocess_and_append_csv(file_path, excel_path=excel_path, logger=logger)

# Add validation here:
validate_minimum_data(X, y, logger=logger)

# Then continue with train_test_split
test_size = config["model_evaluation"]["test_size"]
...
```

### 3. Make Thresholds Configurable
Add to `config.yaml`:
```yaml
model_evaluation:
  test_size: 0.2
  random_state: 42
  min_total_samples: 30  # Minimum total samples required
  min_test_samples: 10   # Minimum test samples required
```

### 4. Update Documentation
Add to README.md:
```markdown
## Data Requirements
- **Minimum samples:** 30 transactions recommended for meaningful predictions
- **Minimum test samples:** 10 transactions in test set (20% of data)
- For best results, provide at least 100+ historical transactions
- More data = better predictions
```

## Alternative Approach
Add a warning instead of hard error for 20-30 samples:
```python
if total_samples < 30:
    plog.log_warning(logger,
                     f"Warning: Only {total_samples} samples available. "
                     f"At least 30 samples recommended for reliable predictions. "
                     f"Results may not be accurate.")
elif total_samples < 50:
    plog.log_info(logger,
                  f"Note: {total_samples} samples available. "
                  f"50+ samples recommended for best results.")
```

## Benefits
1. Better user experience with clear error messages
2. Prevents wasted computation on insufficient data
3. Sets proper expectations about data requirements
4. Helps users understand why predictions might be poor

## Labels
- enhancement
- validation
- critical
- user-experience
