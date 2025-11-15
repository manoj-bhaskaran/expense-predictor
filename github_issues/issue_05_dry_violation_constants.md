# DRY Violation: TRANSACTION_AMOUNT_LABEL Defined in Multiple Files

## Summary
The constant `TRANSACTION_AMOUNT_LABEL = "Tran Amt"` is defined in both `helpers.py` and `model_runner.py`, violating the DRY (Don't Repeat Yourself) principle.

## Impact
- **Severity:** High
- If the column name changes, it must be updated in multiple places
- Risk of inconsistency if changed in one place but not the other
- Maintenance burden
- Potential bugs if definitions diverge

## Current Behavior
Two separate definitions:
- `helpers.py:16`: `TRANSACTION_AMOUNT_LABEL = "Tran Amt"`
- `model_runner.py:281`: `TRANSACTION_AMOUNT_LABEL = "Tran Amt"`

## Expected Behavior
Single source of truth for this constant, imported where needed.

## Technical Details

**Affected Files:**
- `helpers.py:16` - Definition 1
- `model_runner.py:281` - Definition 2
- Both files use this constant in multiple places

**Usage in helpers.py:**
```python
# Line 16 - Definition
TRANSACTION_AMOUNT_LABEL = "Tran Amt"

# Line 49 - Usage in validation
required_columns = ["Date", TRANSACTION_AMOUNT_LABEL]

# Lines 285, 292, 304, 316, 317, 437 - Multiple usages
```

**Usage in model_runner.py:**
```python
# Line 281 - Local definition
TRANSACTION_AMOUNT_LABEL = "Tran Amt"

# Line 353 - Usage
predicted_df = pd.DataFrame({
    "Date": future_dates,
    f"Predicted {TRANSACTION_AMOUNT_LABEL}": y_predict
})
```

## Proposed Solution

### Option 1: Create constants.py (Recommended)
Create new file `constants.py`:
```python
"""
Constants used throughout the Expense Predictor application.
"""

# Column names
TRANSACTION_AMOUNT_LABEL = "Tran Amt"
VALUE_DATE_LABEL = "Value Date"
DAY_OF_WEEK = "Day of the Week"

# Other constants can be added here as needed
```

Update imports:
```python
# In helpers.py:
from constants import TRANSACTION_AMOUNT_LABEL, VALUE_DATE_LABEL, DAY_OF_WEEK

# Remove lines 16-18 (old definitions)

# In model_runner.py:
from constants import TRANSACTION_AMOUNT_LABEL

# Remove line 281 (old definition)
```

### Option 2: Move to config.py
Add to `config.py`:
```python
# Column name constants
TRANSACTION_AMOUNT_LABEL = "Tran Amt"
VALUE_DATE_LABEL = "Value Date"
DAY_OF_WEEK = "Day of the Week"
```

Import from config:
```python
from config import TRANSACTION_AMOUNT_LABEL, VALUE_DATE_LABEL, DAY_OF_WEEK
```

### Option 3: Import from helpers.py to model_runner.py
Quick fix - import from helpers in model_runner:
```python
# In model_runner.py, update line 51:
from helpers import (
    get_quarter_end_date,
    prepare_future_dates,
    preprocess_and_append_csv,
    write_predictions,
    TRANSACTION_AMOUNT_LABEL  # Add this
)

# Remove line 281 local definition
```

## Recommendation
**Option 1 (constants.py)** is recommended because:
- Clear separation of concerns
- Easy to find all constants
- Scalable for future constants
- Common pattern in Python projects
- Prevents circular imports

## Additional Improvements
While fixing this, consider moving other duplicated constants:
- `DAY_OF_WEEK = "Day of the Week"` (helpers.py:17)
- `VALUE_DATE_LABEL = "Value Date"` (helpers.py:18)

## Testing
After changes, verify:
```bash
# Run all tests to ensure imports work
pytest -v

# Check for any import errors
python -c "from constants import TRANSACTION_AMOUNT_LABEL; print(TRANSACTION_AMOUNT_LABEL)"

# Run the actual script
python model_runner.py --data_file trandata.csv
```

## Benefits
1. Single source of truth
2. Easier to maintain and update
3. Reduces risk of inconsistency
4. Improves code organization
5. Follows Python best practices

## Labels
- refactoring
- code-quality
- maintenance
- good first issue
