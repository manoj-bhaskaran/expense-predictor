# Version Mismatch: line-profiler Between setup.py and requirements-dev.txt

## Summary
line-profiler version is inconsistent between `setup.py` (4.1.0) and `requirements-dev.txt` (4.1.3).

## Impact
- **Severity:** High
- Inconsistent development environments
- `pip install -e .[dev]` vs `pip install -r requirements-dev.txt` give different versions
- Potential compatibility issues
- Confusion for contributors

## Current Behavior
- Installing via `pip install -e .[dev]` installs line-profiler==4.1.0
- Installing via `pip install -r requirements-dev.txt` installs line-profiler==4.1.3
- Different developers may have different versions

## Expected Behavior
Both installation methods should install the same version of line-profiler.

## Technical Details

**Files:**
- `setup.py:73`: `"line-profiler==4.1.0"`
- `requirements-dev.txt:46`: `line-profiler==4.1.3`

**Why This Matters:**
Version 4.1.3 was specifically added to fix Python 3.12 compatibility issues (see PR #104). Using the older 4.1.0 version defeats this fix.

## Reproduction
```bash
# Method 1
pip install -e .[dev]
pip show line-profiler  # Shows 4.1.0

# Method 2
pip install -r requirements-dev.txt
pip show line-profiler  # Shows 4.1.3
```

## Proposed Solution

Update `setup.py` line 73:
```python
extras_require={
    "dev": [
        # ... other packages ...
        "memory-profiler==0.61.0",
        "line-profiler==4.1.3",  # Changed from 4.1.0
        "matplotlib==3.8.0",
        # ... rest ...
    ],
},
```

## Root Cause
PR #104 updated line-profiler in requirements-dev.txt for Python 3.12 compatibility but forgot to update setup.py.

## Verification
After fix, both methods should show same version:
```bash
pip install -e .[dev]
pip show line-profiler | grep Version  # Should show 4.1.3
```

## Related
- PR #104 - Add Python 3.12 to test matrix and update documentation
- Commit b7b1b13 - fix: Update line-profiler to 4.1.3 for Python 3.12 compatibility

## Labels
- bug
- dependencies
- good first issue
- python-3.12
