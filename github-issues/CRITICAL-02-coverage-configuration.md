# [CRITICAL] Fix coverage configuration - model_runner.py excluded from coverage

## Priority
🔴 **Critical**

## Labels
`critical`, `testing`, `ci-cd`, `configuration`

## Description

The main entry point file `model_runner.py` is completely excluded from test coverage, which significantly misrepresents the actual code coverage and defeats the purpose of coverage testing.

### Current Configuration

```ini
# .coveragerc:11
[run]
omit =
    tests/*
    setup.py
    */site-packages/*
    */__pycache__/*
    .venv/*
    venv/*
    model_runner.py  # ❌ Main file excluded!
```

### Problems

1. **Main orchestration logic** is not covered by tests
2. **Misleading coverage metrics**: README claims 43% coverage, but this excludes the most important file
3. **CI/CD enforcement gap**: Coverage requirement is 80%, but the main file doesn't count
4. **Reduced confidence**: Cannot verify that the main execution flow works correctly

## Root Cause Analysis

The file was likely excluded because:
- It's difficult to test (contains argparse and script execution)
- No tests were written for it initially
- It was easier to exclude than to fix

However, this creates a false sense of security about code quality.

## Proposed Solution

### Step 1: Remove from omit list
Remove `model_runner.py` from `.coveragerc` and `pytest.ini` omit lists

### Step 2: Add integration tests
Create `tests/test_model_runner_integration.py` with:
- Tests for CLI argument parsing
- Tests for full execution flow
- Tests for error handling in main execution
- Tests for different argument combinations

### Step 3: Refactor for testability
If needed, refactor `model_runner.py` to separate concerns:
```python
def parse_args(args=None):
    """Parse command line arguments."""
    # Current argparse logic
    return parsed_args

def main(args=None):
    """Main entry point for CLI."""
    parsed_args = parse_args(args)
    # Rest of execution logic

if __name__ == '__main__':
    main()
```

This allows testing with different argument combinations.

## Acceptance Criteria

- [ ] `model_runner.py` removed from coverage omit lists
- [ ] Integration tests added for `model_runner.py`
- [ ] Coverage reported includes `model_runner.py`
- [ ] All tests pass
- [ ] Actual coverage percentage documented

## Impact

This will likely **reduce the reported coverage percentage** initially, but will provide an accurate picture of test coverage.

## Related Files
- `.coveragerc`
- `pytest.ini`
- `model_runner.py`
- `tests/test_model_runner.py` (needs expansion)

## See Also
- Issue #3 (Fix CI/CD coverage threshold)
