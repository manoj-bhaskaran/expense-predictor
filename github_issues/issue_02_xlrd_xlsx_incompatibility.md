# xlrd 2.0.1 Cannot Read .xlsx Files

## Summary
The project uses xlrd 2.0.1, but xlrd versions 2.0.0+ dropped support for .xlsx files. The code incorrectly attempts to use xlrd for .xlsx files in some cases.

## Impact
- **Severity:** Critical
- .xlsx file processing fails with xlrd
- Confusing error messages for users
- Documentation claims .xlsx support but it may not work correctly

## Background
xlrd 2.0.0 and later dropped support for .xlsx files due to security concerns. Only .xls (Excel 97-2003) format is supported. For .xlsx files, openpyxl or another library is required.

## Current Behavior
The code correctly selects openpyxl for .xlsx files (helpers.py:105), but:
1. xlrd is still listed as a dependency
2. No clear documentation about the .xls vs .xlsx distinction
3. Potential confusion in validate_excel_file

## Technical Details

**Affected Files:**
- `requirements.txt:10` (xlrd==2.0.1)
- `helpers.py:95-101` (validation accepts both extensions)
- `helpers.py:105` (correctly routes to openpyxl)
- `security.py:23` (ALLOWED_EXCEL_EXTENSIONS includes both)

**Code References:**
```python
# helpers.py:95-101
valid_extensions = [".xls", ".xlsx"]
file_extension = os.path.splitext(file_path)[1].lower()

if file_extension not in valid_extensions:
    plog.log_error(logger, f"Invalid Excel file format: {file_extension}...")
    raise DataValidationError(...)
```

## Proposed Solution

### 1. Keep Current Approach (Recommended)
- Keep xlrd for .xls files
- Ensure openpyxl is in production dependencies (see Issue #1)
- Update documentation to clarify:
  - .xls files use xlrd
  - .xlsx files use openpyxl
  - Both formats are supported

### 2. Add Error Handling
Add better error message if openpyxl is missing:

```python
try:
    engine = "xlrd" if file_path.endswith(".xls") else "openpyxl"
    pd.ExcelFile(file_path, engine=engine)
except ImportError as e:
    if "openpyxl" in str(e):
        raise DataValidationError(
            f"Processing .xlsx files requires openpyxl. "
            f"Install it with: pip install openpyxl"
        ) from e
    raise
```

### 3. Update Documentation
In README.md, clarify:
```markdown
## Excel File Support
- **.xls files** (Excel 97-2003): Supported via xlrd
- **.xlsx files** (Excel 2007+): Supported via openpyxl
- Both formats are automatically detected and processed
```

## Related Issues
- #1 - Missing openpyxl in Production Dependencies

## Labels
- bug
- dependencies
- documentation
- critical
