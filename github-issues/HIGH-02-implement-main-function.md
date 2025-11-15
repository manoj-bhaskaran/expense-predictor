# [HIGH] Implement main() function for console entry point

## Priority
🟠 **High Priority**

## Labels
`bug`, `enhancement`, `packaging`

## Description

The `setup.py` defines a console script entry point that references a non-existent `main()` function:

```python
# setup.py:74-77
entry_points={
    "console_scripts": [
        "expense-predictor=model_runner:main",  # ❌ main() doesn't exist
    ],
},
```

Currently, trying to run `expense-predictor` after installation will fail with:
```
AttributeError: module 'model_runner' has no attribute 'main'
```

## Current Behavior

Users must run the script directly:
```bash
python model_runner.py --data_file trandata.csv
```

## Desired Behavior

After `pip install .`, users should be able to run:
```bash
expense-predictor --data_file trandata.csv
```

## Proposed Solution

### 1. Refactor model_runner.py

```python
#!/usr/bin/env python
"""
Expense Predictor Script - model_runner.py
...
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
# ... other imports ...

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Expense Predictor')
    parser.add_argument('--future_date', type=str, help='Future date for prediction (e.g., 31/12/2025)')
    parser.add_argument('--excel_dir', type=str, default='.', help='Directory where the Excel file is located')
    # ... rest of arguments ...
    return parser.parse_args()

def main():
    """Main entry point for the expense predictor CLI."""
    args = parse_arguments()

    # Get the directory where this script is located
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    # ... rest of the current script logic ...

    return 0  # Exit code

if __name__ == '__main__':
    import sys
    sys.exit(main())
```

### 2. Benefits

1. **Proper packaging**: Can install and run as a command
2. **Testability**: Can test `main()` with different arguments
3. **Better structure**: Separates parsing from execution
4. **Exit codes**: Can return proper exit codes

### 3. Testing

Create tests in `tests/test_model_runner_integration.py`:

```python
def test_main_with_args(monkeypatch):
    """Test main function with command line arguments."""
    test_args = ['expense-predictor', '--data_file', 'sample_data.csv']
    monkeypatch.setattr('sys.argv', test_args)

    exit_code = main()
    assert exit_code == 0

def test_main_invalid_args():
    """Test main function with invalid arguments."""
    # Should handle errors gracefully
    pass
```

## Acceptance Criteria

- [ ] `main()` function implemented in `model_runner.py`
- [ ] Function contains all current script logic
- [ ] Can be called from command line via `expense-predictor`
- [ ] Original script execution still works (`python model_runner.py`)
- [ ] Tests added for `main()` function
- [ ] Documentation updated with both usage methods
- [ ] Exit codes properly returned (0 for success, non-zero for errors)

## Breaking Changes

None - this is backward compatible. Both methods will work:
```bash
# Old method (still works)
python model_runner.py --data_file trandata.csv

# New method (now also works)
expense-predictor --data_file trandata.csv
```

## Documentation Updates

Update README.md to show both usage methods:

```markdown
### Using as Installed Package

```bash
pip install .
expense-predictor --data_file trandata.csv
```

### Using as Script

```bash
python model_runner.py --data_file trandata.csv
```
```

## Related Files
- `model_runner.py`
- `setup.py`
- `README.md`
- `tests/test_model_runner.py`

## Related Issues
- Issue #2 (Coverage configuration - this will help with testability)
