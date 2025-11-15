# [HIGH] Remove duplicate date range logic in helpers.py

## Priority
🟠 **High Priority**

## Labels
`refactoring`, `code-quality`, `technical-debt`

## Description

Date range calculation logic is duplicated in multiple functions within `helpers.py`, violating the DRY (Don't Repeat Yourself) principle and creating maintenance burden.

## Duplicate Code Examples

### Location 1: `_process_dataframe()` (lines 222-234)
```python
end_date = datetime.now() - timedelta(days=1)
end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

start_date = df['Date'].min()
if pd.isna(start_date) or pd.isna(end_date):
    plog.log_error(logger, "Invalid start or end date found in data")
    raise ValueError("Invalid start or end date found. Please check the data.")

plog.log_info(logger, f"Creating complete date range from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
complete_date_range = pd.date_range(start=start_date, end=end_date)
```

### Location 2: `preprocess_and_append_csv()` (lines 360-364)
```python
start_date = df['Date'].min()
end_date = datetime.now() - timedelta(days=1)
complete_date_range = pd.date_range(start=start_date, end=end_date)
```

## Problems

1. **Maintenance Burden**: Changes must be made in multiple places
2. **Inconsistency Risk**: Logic can diverge over time
3. **Bug Potential**: Easy to fix a bug in one place but not another
4. **Testing**: Must test the same logic multiple times
5. **Readability**: Obscures the intent behind the calculation

## Questions to Answer

1. **Why `datetime.now() - timedelta(days=1)`?**
   - Is this to exclude today's incomplete data?
   - Should this be configurable?
   - Should be documented

2. **Why normalize time to midnight?**
   - Important for date range calculations
   - Should be part of the helper function

## Proposed Solution

### 1. Create Helper Function

```python
def get_training_date_range(
    df: pd.DataFrame,
    date_column: str = 'Date',
    logger: Optional[logging.Logger] = None
) -> pd.DatetimeIndex:
    """
    Get the complete date range for training data.

    Creates a complete date range from the earliest date in the data
    to yesterday (excluding today to avoid incomplete data).

    Parameters:
        df: DataFrame containing the date column
        date_column: Name of the date column (default: 'Date')
        logger: Optional logger for logging messages

    Returns:
        Complete date range for training

    Raises:
        ValueError: If date range is invalid
    """
    # Calculate end date (yesterday at midnight)
    # Exclude today to avoid training on incomplete data
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Get start date from data
    start_date = df[date_column].min()

    # Validate dates
    if pd.isna(start_date) or pd.isna(end_date):
        plog.log_error(logger, "Invalid start or end date found in data")
        raise ValueError("Invalid start or end date found. Please check the data.")

    # Log the range
    plog.log_info(
        logger,
        f"Creating complete date range from {start_date.strftime('%Y-%m-%d')} "
        f"to {end_date.strftime('%Y-%m-%d')}"
    )

    return pd.date_range(start=start_date, end=end_date)
```

### 2. Update Callers

```python
# In _process_dataframe()
complete_date_range = get_training_date_range(df, logger=logger)
df = df.set_index('Date').reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()

# In preprocess_and_append_csv()
complete_date_range = get_training_date_range(df, logger=logger)
df = df.set_index('Date').reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()
```

### 3. Consider Configuration

Add to `config.yaml`:
```yaml
data_processing:
  skiprows: 12
  exclude_today: true  # Exclude today's data from training
  training_end_offset_days: 1  # How many days before today to end training
```

## Acceptance Criteria

- [ ] New helper function `get_training_date_range()` created
- [ ] Function has proper docstring explaining the logic
- [ ] All duplicate code replaced with calls to helper
- [ ] Unit tests added for the new function
- [ ] All existing tests still pass
- [ ] Magic number (days=1) explained in comments or made configurable
- [ ] Code is more maintainable and DRY

## Benefits

1. **Single Source of Truth**: Logic defined once
2. **Better Documentation**: Docstring explains the business logic
3. **Easier Testing**: Test the function once comprehensively
4. **Easier Maintenance**: Changes made in one place
5. **Configurability**: Easier to make configurable later

## Related Files
- `helpers.py` (lines 222-234, 360-364)
- `config.yaml` (if making configurable)
- `tests/test_helpers.py` (add tests)

## Related Issues
- Issue #5 (Move hardcoded values to config)
