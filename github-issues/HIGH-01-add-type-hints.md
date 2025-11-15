# [HIGH] Add type hints to all function signatures

## Priority
🟠 **High Priority**

## Labels
`enhancement`, `code-quality`, `typing`, `good-first-issue`

## Description

The codebase currently lacks type hints despite having `mypy` configured in the CI/CD pipeline. Adding type hints will improve code quality, IDE support, and catch potential bugs at development time.

### Current State

Functions lack type annotations:
```python
# helpers.py:142
def find_column_name(df_columns, expected_name):
    """Find a column name..."""
    # No type hints
```

### Desired State

```python
from typing import Optional
import pandas as pd

def find_column_name(df_columns: pd.Index, expected_name: str) -> Optional[str]:
    """Find a column name that matches the expected name with flexible formatting."""
```

## Benefits

1. **Better IDE Support**: Autocomplete and inline documentation
2. **Early Bug Detection**: Catch type errors before runtime
3. **Self-Documenting**: Type hints serve as inline documentation
4. **Refactoring Safety**: Easier to refactor with confidence
5. **Team Collaboration**: Clearer API contracts

## Scope

Add type hints to all functions in:
- [ ] `helpers.py` (17 functions)
- [ ] `security.py` (9 functions)
- [ ] `config.py` (3 functions)
- [ ] `model_runner.py` (main script)
- [ ] `python_logging_framework.py` (if keeping local version)

## Implementation Guidelines

### 1. Import Required Types
```python
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
import pandas as pd
import logging
```

### 2. Annotate Function Signatures
```python
def validate_csv_file(file_path: str, logger: Optional[logging.Logger] = None) -> None:
    """Validate that CSV file exists and has required columns."""
    pass

def preprocess_data(file_path: str, logger: Optional[logging.Logger] = None) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Preprocess input data from a CSV file."""
    pass
```

### 3. Run mypy to Verify
```bash
mypy helpers.py security.py config.py model_runner.py
```

### 4. Fix Any Type Errors
Address issues found by mypy

## Acceptance Criteria

- [ ] All public functions have type hints
- [ ] All parameters annotated with types
- [ ] All return types specified
- [ ] `mypy` passes with no errors (or only allowed ignores)
- [ ] Documentation updated if type signatures clarify behavior
- [ ] All tests still pass

## Suggested Approach

Start with one file at a time:
1. Start with `security.py` (smallest, clearest types)
2. Then `config.py` (simple types)
3. Then `helpers.py` (more complex with pandas types)
4. Finally `model_runner.py` (most complex)

## Example PR Structure

```python
# Before
def write_predictions(predicted_df, output_path, logger=None, skip_confirmation=False):
    """Write predictions to a CSV file."""
    pass

# After
def write_predictions(
    predicted_df: pd.DataFrame,
    output_path: str,
    logger: Optional[logging.Logger] = None,
    skip_confirmation: bool = False
) -> None:
    """Write predictions to a CSV file with security measures."""
    pass
```

## Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

## Related Files
- `helpers.py`
- `security.py`
- `config.py`
- `model_runner.py`
- `.github/workflows/pre-commit.yml` (mypy already configured)
