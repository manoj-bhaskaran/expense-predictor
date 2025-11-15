# [MEDIUM] Clarify python_logging_framework usage strategy

## Priority
🟡 **Medium Priority**

## Labels
`documentation`, `dependencies`, `technical-debt`

## Description

There is confusion about the `python_logging_framework` - it exists both as a local file and as a GitHub dependency, making it unclear which version is actually used and what the intended approach is.

## Current Situation

### Local Version
```python
# python_logging_framework.py exists in repo root
# Contains a "mock" implementation with pragma: no cover comments
# Header says "Mock python_logging_framework for testing purposes"
```

### Remote Version
```python
# requirements.txt:16
git+https://github.com/manoj-bhaskaran/My-Scripts.git@main
# Installs from GitHub repository
```

## Questions to Answer

1. **Which version is used in production?**
   - When installed via pip, the GitHub version overwrites the local one
   - But local version exists for development?

2. **Is the local version truly a "mock"?**
   - It has full implementation, not really a mock
   - Used for testing when GitHub package unavailable?

3. **What's the long-term strategy?**
   - Keep using GitHub dependency?
   - Switch to local version?
   - Publish to PyPI?

## Problems This Causes

1. **Confusion for Contributors**: Which version to modify?
2. **Testing Inconsistency**: Tests might use different version than production
3. **Maintenance Burden**: Two versions to keep in sync
4. **Documentation Gap**: Not explained in README

## Proposed Solutions

### Option 1: Use Local Version Only (Recommended)
**Best for**: Quick fix, simple maintenance

```diff
- git+https://github.com/manoj-bhaskaran/My-Scripts.git@main
```

**Steps**:
1. Remove from `requirements.txt`
2. Rename `python_logging_framework.py` header to clarify it's the real implementation
3. Remove `pragma: no cover` comments
4. Add tests for the logging framework
5. Document in README

**Pros**: Simple, no external dependency, works offline
**Cons**: Code duplication if used in other projects

### Option 2: Use GitHub Version Only
**Best for**: Sharing across multiple projects

**Steps**:
1. Delete local `python_logging_framework.py`
2. Pin GitHub dependency to specific commit (see Issue #1)
3. Document the dependency clearly
4. Ensure it's installed before tests run

**Pros**: Single source of truth, shared across projects
**Cons**: External dependency, fragility (see Issue #1)

### Option 3: Publish to PyPI (Best Long-term)
**Best for**: Professional distribution

**Steps**:
1. Create separate repository for `python_logging_framework`
2. Add `setup.py`, proper packaging
3. Publish to PyPI
4. Install from PyPI: `python-logging-framework==1.0.0`
5. Delete local version

**Pros**: Professional, versioned, reliable
**Cons**: Most effort, requires PyPI account

### Option 4: Vendor the Dependency
**Best for**: Complete control

**Steps**:
1. Create `expense_predictor/vendor/python_logging_framework.py`
2. Import as: `from expense_predictor.vendor import python_logging_framework as plog`
3. Remove from requirements
4. Add notice about vendoring in file header

**Pros**: Complete control, no external deps
**Cons**: Harder to update if source changes

## Recommendation

**Short-term** (this sprint):
- Choose Option 1 (use local version)
- Fixes Issue #1 simultaneously
- Simplest solution

**Long-term** (future consideration):
- If used in multiple projects: Option 3 (publish to PyPI)
- If only used here: Keep Option 1

## Implementation Checklist

### For Option 1 (Recommended):
- [ ] Remove Git dependency from `requirements.txt`
- [ ] Update `python_logging_framework.py` header:
  ```python
  """
  Logging framework for Expense Predictor.

  Provides simplified logging initialization with file and console handlers.
  """
  ```
- [ ] Remove all `# pragma: no cover` comments
- [ ] Add unit tests in `tests/test_logging_framework.py`
- [ ] Update README to document the logging framework
- [ ] Verify all tests pass
- [ ] Update CHANGELOG

## Documentation Updates

Add to README:

```markdown
### Logging Framework

This project includes a custom logging framework (`python_logging_framework.py`)
that provides simplified logging setup with both file and console handlers.

**Usage**:
```python
import python_logging_framework as plog
logger = plog.initialise_logger('my_script', log_dir='logs')
plog.log_info(logger, "Info message")
plog.log_error(logger, "Error message")
```

**Location**: `python_logging_framework.py` in the repository root.
```

## Acceptance Criteria

- [ ] Clear decision made on which approach to use
- [ ] Implementation matches the chosen approach
- [ ] No duplicate versions
- [ ] Documentation updated to explain the choice
- [ ] All tests pass
- [ ] Contributors understand which code to modify

## Related Issues
- Issue #1 (GitHub dependency - this issue helps solve that)

## Related Files
- `python_logging_framework.py`
- `requirements.txt`
- `README.md`
- All files importing `python_logging_framework`
