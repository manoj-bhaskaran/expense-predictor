# Missing openpyxl in Production Dependencies

## Summary
openpyxl is required for .xlsx file processing but is only listed in `requirements-dev.txt`, not in `requirements.txt` or `setup.py` install_requires.

## Impact
- **Severity:** Critical
- Production installations cannot process .xlsx files
- Runtime error when users try to process Excel files in .xlsx format
- Breaks core functionality for most modern Excel files

## Current Behavior
When a user installs via `pip install -r requirements.txt` or `pip install expense-predictor`, openpyxl is not installed. When they try to process a .xlsx file, the code will fail at runtime.

## Expected Behavior
Users should be able to process both .xls and .xlsx files after installation without needing dev dependencies.

## Technical Details

**Affected Files:**
- `requirements.txt` (missing openpyxl)
- `setup.py:43-50` (install_requires missing openpyxl)
- `helpers.py:105-106` (code attempts to use openpyxl)

**Code Reference:**
```python
# helpers.py:105-106
engine = "xlrd" if file_path.endswith(".xls") else "openpyxl"
pd.ExcelFile(file_path, engine=engine)
```

## Reproduction Steps
1. Create fresh virtual environment
2. `pip install -r requirements.txt`
3. Try to run with a .xlsx file: `python model_runner.py --excel_file data.xlsx`
4. Get error: `ModuleNotFoundError: No module named 'openpyxl'`

## Proposed Solution
Add `openpyxl==3.1.2` to both `requirements.txt` and `setup.py` install_requires.

**requirements.txt:**
```txt
# Excel file support
xlrd==2.0.1  # For .xls files
openpyxl==3.1.2  # For .xlsx files
```

**setup.py:**
```python
install_requires=[
    "numpy==1.26.4",
    "pandas==2.2.0",
    "scikit-learn==1.5.0",
    "xlrd==2.0.1",
    "openpyxl==3.1.2",  # Add this
    "pyyaml==6.0.1",
    "python-dotenv==1.0.0",
],
```

## Labels
- bug
- dependencies
- critical
- good first issue
