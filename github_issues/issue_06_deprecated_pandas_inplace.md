# Replace Deprecated pandas inplace=True Parameter

## Summary
Code uses pandas `inplace=True` parameter in multiple locations. This parameter is discouraged in recent pandas versions and may be removed in future versions.

## Impact
- **Severity:** High
- Future pandas versions may deprecate or remove `inplace=True`
- FutureWarning messages in current pandas versions
- Code may break in pandas 3.0+
- Performance: `inplace=True` doesn't always improve performance as commonly believed

## Current Behavior
Three usages of `inplace=True` in helpers.py:

**Location 1 - Line 305:**
```python
df.rename(columns={"index": "Date"}, inplace=True)
```

**Location 2 - Line 437:**
```python
daily_expenses.rename(columns={"expense": TRANSACTION_AMOUNT_LABEL}, inplace=True)
```

**Location 3 - Line 448:**
```python
df.rename(columns={"index": "Date"}, inplace=True)
```

## Expected Behavior
Use assignment instead of `inplace=True`:
```python
df = df.rename(columns={"index": "Date"})
```

## Background
From pandas documentation:
> "The inplace parameter in many pandas methods may be deprecated in a future version. It is recommended to use assignment instead."

Reasons:
1. `inplace=True` doesn't guarantee better performance
2. Can lead to confusing behavior with chaining
3. Makes code harder to reason about
4. Against functional programming principles
5. May still create copies internally

## Proposed Solution

### Change 1 - helpers.py:305
```python
# Before
df = df.set_index("Date").reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()
df.rename(columns={"index": "Date"}, inplace=True)

# After
df = df.set_index("Date").reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()
df = df.rename(columns={"index": "Date"})

# Or chain it:
df = (df.set_index("Date")
        .reindex(complete_date_range)
        .fillna({TRANSACTION_AMOUNT_LABEL: 0})
        .reset_index()
        .rename(columns={"index": "Date"}))
```

### Change 2 - helpers.py:437
```python
# Before
daily_expenses.columns = ["Date", "expense"]
daily_expenses.rename(columns={"expense": TRANSACTION_AMOUNT_LABEL}, inplace=True)

# After
daily_expenses.columns = ["Date", "expense"]
daily_expenses = daily_expenses.rename(columns={"expense": TRANSACTION_AMOUNT_LABEL})

# Or combine:
daily_expenses.columns = ["Date", TRANSACTION_AMOUNT_LABEL]
```

### Change 3 - helpers.py:448
```python
# Before
df = df.set_index("Date").reindex(complete_date_range).fillna({TRANSACTION_AMOUNT_LABEL: 0}).reset_index()
df.rename(columns={"index": "Date"}, inplace=True)

# After
df = (df.set_index("Date")
        .reindex(complete_date_range)
        .fillna({TRANSACTION_AMOUNT_LABEL: 0})
        .reset_index()
        .rename(columns={"index": "Date"}))
```

## Verification Steps
After making changes:

1. **Run tests:**
```bash
pytest -v
```

2. **Check for FutureWarnings:**
```bash
python -W error::FutureWarning model_runner.py --data_file trandata.csv
```

3. **Manual testing:**
```bash
python model_runner.py --data_file trandata.csv --future_date 31/12/2025
```

4. **Performance check (optional):**
```python
# Before and after timings should be similar
import timeit
# Test both approaches
```

## Benefits
1. Future-proof code for pandas 3.0+
2. More explicit and easier to understand
3. Follows pandas best practices
4. Removes deprecation warnings
5. Better for code review and maintenance

## Migration Notes
- This is a non-breaking change for current functionality
- All tests should continue to pass
- No changes to API or user-facing behavior
- Can be done incrementally or all at once

## Related
- pandas documentation: https://pandas.pydata.org/docs/user_guide/indexing.html#returning-a-view-versus-a-copy
- pandas GitHub issue on deprecating inplace: https://github.com/pandas-dev/pandas/issues/16529

## Labels
- refactoring
- dependencies
- pandas
- deprecation
- maintenance
