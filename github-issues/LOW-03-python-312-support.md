# [LOW] Add Python 3.12 to test matrix or remove from classifiers

## Priority
🔵 **Low Priority**

## Labels
`enhancement`, `ci-cd`, `testing`

## Description

There's an inconsistency between `setup.py` classifiers (which claim Python 3.12 support) and the CI/CD test matrix (which only tests up to Python 3.11).

## Current State

### setup.py claims 3.12 support
```python
# setup.py:35
classifiers=[
    ...
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",  # ✅ Listed
    ...
],
```

### CI/CD only tests 3.9-3.11
```yaml
# .github/workflows/test.yml:14
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']  # ❌ No 3.12
```

## Problem

This creates false expectations:
- Users think Python 3.12 is supported
- But it's never tested in CI/CD
- Potential compatibility issues unknown
- PyPI/pip will allow installation on 3.12 despite no testing

## Proposed Solutions

### Option 1: Add Python 3.12 to Test Matrix (Recommended)

```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

**Pros**:
- Validates actual 3.12 compatibility
- Future-proofs the project
- Gives confidence to 3.12 users

**Cons**:
- May reveal compatibility issues
- Slightly longer CI/CD time

### Option 2: Remove 3.12 from Classifiers

```python
# setup.py
classifiers=[
    ...
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    # Remove 3.12 until tested
],
```

**Pros**:
- Honest about support
- No false expectations
- Quick fix

**Cons**:
- Doesn't move project forward
- 3.12 might work fine anyway

## Recommendation

**Add Python 3.12 to test matrix** - it's likely to work fine and keeps the project up-to-date.

## Implementation Steps

### Step 1: Test Locally

```bash
# Install Python 3.12 (if not already installed)
pyenv install 3.12

# Create virtual environment
python3.12 -m venv venv312
source venv312/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Check for deprecation warnings
pytest tests/ -W default
```

### Step 2: Check Dependencies

Verify all dependencies support Python 3.12:
```bash
pip install --dry-run -r requirements.txt
```

Common issues:
- **numpy**: Ensure version supports 3.12
- **pandas**: Check compatibility
- **scikit-learn**: Verify 3.12 support

### Step 3: Update CI/CD

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
      fail-fast: false  # Continue even if one version fails

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    # ... rest of workflow
```

### Step 4: Update Documentation

README.md:
```markdown
## Requirements

- Python 3.9, 3.10, 3.11, or 3.12
- Git (required for installing dependencies from GitHub)
- See `requirements.txt` for pinned package dependencies
```

### Step 5: Handle Potential Issues

If tests fail on 3.12:

#### Approach A: Fix compatibility issues
- Update dependencies to 3.12-compatible versions
- Fix any code incompatibilities
- Add 3.12 to matrix once fixed

#### Approach B: Mark as experimental
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
    experimental: [false, false, false, true]
  allow-failure:
    - experimental: true
```

#### Approach C: Defer 3.12 support
- Remove from classifiers for now
- Add TODO comment to add later
- Document in CHANGELOG

## Dependency Compatibility Check

Current dependencies and Python 3.12 support:

| Dependency | Version | Python 3.12 Support |
|------------|---------|---------------------|
| numpy | 1.26.4 | ✅ Yes |
| pandas | 2.2.0 | ✅ Yes |
| scikit-learn | 1.5.0 | ✅ Yes |
| xlrd | 2.0.1 | ✅ Yes |
| pyyaml | 6.0.1 | ✅ Yes |

All current dependencies support Python 3.12, so adding it should be safe.

## Testing Checklist

- [ ] Install Python 3.12 locally
- [ ] Install all dependencies on 3.12
- [ ] Run full test suite on 3.12
- [ ] Check for deprecation warnings
- [ ] Verify all imports work
- [ ] Test model training on 3.12
- [ ] Test all CLI arguments
- [ ] Check for any 3.12-specific issues

## Acceptance Criteria

### For Option 1 (Add to matrix):
- [ ] Python 3.12 added to test matrix
- [ ] All tests pass on Python 3.12
- [ ] No critical warnings on Python 3.12
- [ ] Dependencies compatible with 3.12
- [ ] Documentation updated
- [ ] Badge shows all Python versions

### For Option 2 (Remove from classifiers):
- [ ] Python 3.12 removed from `setup.py`
- [ ] Documentation updated (if mentioning versions)
- [ ] TODO added to revisit in future

## Known Python 3.12 Changes

Python 3.12 introduced some changes to be aware of:

1. **Performance improvements**: Generally faster
2. **Better error messages**: More helpful tracebacks
3. **Deprecated features removed**: Some old warnings become errors
4. **Type hinting improvements**: Better typing support

None of these should affect this project negatively.

## Related Files
- `setup.py`
- `.github/workflows/test.yml`
- `README.md`
- `.python-version` (optional: could add 3.12)

## Timeline

**Immediate** (this sprint):
- Test locally with Python 3.12
- Fix any issues found

**Short-term** (next sprint):
- Add to CI/CD if tests pass
- Update documentation

**Alternative** (if issues found):
- Remove from classifiers until resolved
- Document known issues
- Plan fix for future release

## References
- [Python 3.12 Release Notes](https://docs.python.org/3/whatsnew/3.12.html)
- [Python 3.12 Migration Guide](https://docs.python.org/3/howto/pyporting.html)
