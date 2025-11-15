# [MEDIUM] Add pytest markers to test files

## Priority
🟡 **Medium Priority**

## Labels
`enhancement`, `testing`, `good-first-issue`

## Description

Test markers are defined in `pytest.ini` but not actually used in any test files. This prevents selective test execution and makes test organization less effective.

## Current Configuration

```ini
# pytest.ini:32-36
markers =
    unit: Unit tests for individual functions
    integration: Integration tests for complete workflows
    slow: Tests that take longer to run
    validation: Tests for data validation functions
```

## Problem

None of the test files use these markers:
- ❌ No `@pytest.mark.unit` decorators
- ❌ No `@pytest.mark.integration` decorators
- ❌ No `@pytest.mark.slow` decorators
- ❌ No `@pytest.mark.validation` decorators

## Benefits of Using Markers

### 1. Selective Test Execution
```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests during development
pytest -m "not slow"

# Run only validation tests
pytest -m validation
```

### 2. Better CI/CD Organization
```yaml
# Fast feedback - run unit tests first
- name: Quick unit tests
  run: pytest -m unit

# Full test suite - run if unit tests pass
- name: Integration tests
  run: pytest -m integration
```

### 3. Clearer Test Organization
Markers serve as documentation about test purpose and scope

## Proposed Implementation

### 1. Add Markers to Test Classes and Functions

```python
# tests/test_helpers.py

import pytest

@pytest.mark.unit
@pytest.mark.validation
class TestValidateCsvFile:
    """Tests for validate_csv_file function."""

    @pytest.mark.unit
    def test_validate_csv_file_valid(self, sample_csv_path, mock_logger):
        """Test validation of a valid CSV file."""
        validate_csv_file(sample_csv_path, logger=mock_logger)

    @pytest.mark.unit
    def test_validate_csv_file_not_found(self, mock_logger):
        """Test validation with non-existent file."""
        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            validate_csv_file("/nonexistent/file.csv", logger=mock_logger)


@pytest.mark.integration
class TestPreprocessData:
    """Integration tests for data preprocessing."""

    @pytest.mark.integration
    @pytest.mark.slow  # If preprocessing is time-consuming
    def test_preprocess_full_workflow(self, sample_csv_path):
        """Test complete preprocessing workflow."""
        X, y, df = preprocess_data(sample_csv_path)
        assert len(X) > 0
```

### 2. Categorize Existing Tests

#### Unit Tests (fast, isolated)
- `test_helpers.py`: All validation functions
- `test_security.py`: All security functions
- `test_config.py`: Configuration loading

#### Integration Tests (slower, end-to-end)
- `test_model_runner.py`: Full ML pipeline tests
- Tests that involve multiple components

#### Validation Tests (data validation specific)
- CSV validation tests
- Excel validation tests
- Date range validation tests

#### Slow Tests (long-running)
- Model training tests
- Large dataset tests
- Excel file processing tests

## Implementation Plan

### Phase 1: Test File Categorization
Create a mapping of which markers apply to which test files:

```python
# tests/test_helpers.py
# Markers: unit, validation (most tests)
# Markers: integration (preprocessing tests)

# tests/test_security.py
# Markers: unit (all tests)

# tests/test_config.py
# Markers: unit (all tests)

# tests/test_model_runner.py
# Markers: integration, slow (model training tests)

# tests/test_edge_cases.py
# Markers: unit, integration (depends on specific test)
```

### Phase 2: Apply Markers
- [ ] `tests/test_helpers.py` - Add appropriate markers
- [ ] `tests/test_security.py` - Add unit markers
- [ ] `tests/test_config.py` - Add unit markers
- [ ] `tests/test_model_runner.py` - Add integration and slow markers
- [ ] `tests/test_edge_cases.py` - Add appropriate markers

### Phase 3: Update CI/CD
```yaml
# .github/workflows/test.yml

# Add quick unit test job (runs first)
- name: Unit Tests (Fast)
  run: pytest -m unit -v

# Add integration tests (runs after unit)
- name: Integration Tests
  run: pytest -m integration -v
  if: success()
```

### Phase 4: Document Usage
Add to README:

```markdown
### Running Specific Test Categories

```bash
# Run only unit tests (fast feedback)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run validation tests only
pytest -m validation

# Skip slow tests during development
pytest -m "not slow"

# Run everything except integration tests
pytest -m "not integration"

# Combine markers
pytest -m "unit and validation"
```
```

## Example Marker Usage

```python
# Single marker
@pytest.mark.unit
def test_simple_function():
    pass

# Multiple markers
@pytest.mark.integration
@pytest.mark.slow
def test_full_ml_pipeline():
    pass

# Marker on class applies to all methods
@pytest.mark.unit
class TestSecurityFunctions:
    def test_path_validation(self):
        pass

    def test_csv_sanitization(self):
        pass
```

## Acceptance Criteria

- [ ] All test files have appropriate markers
- [ ] Can run `pytest -m unit` successfully
- [ ] Can run `pytest -m integration` successfully
- [ ] Can run `pytest -m "not slow"` successfully
- [ ] Markers documented in README
- [ ] CI/CD optionally uses markers for staged testing
- [ ] No pytest warnings about unknown markers

## Benefits Summary

1. **Faster Development**: Run only unit tests during development
2. **Better CI/CD**: Stage tests from fast to slow
3. **Clearer Organization**: Markers document test purpose
4. **Flexible Execution**: Run tests based on category
5. **Time Savings**: Skip slow tests when not needed

## Related Files
- `pytest.ini` (markers already defined)
- `tests/test_helpers.py`
- `tests/test_security.py`
- `tests/test_config.py`
- `tests/test_model_runner.py`
- `tests/test_edge_cases.py`
- `.github/workflows/test.yml`
- `README.md`
