# [HIGH] Standardize error handling across codebase

## Priority
🟠 **High Priority**

## Labels
`bug`, `code-quality`, `error-handling`

## Description

Error handling is inconsistent across the codebase, with some functions using specific exception types and others using broad `except Exception` clauses. This makes debugging harder and can hide bugs.

## Examples of Inconsistent Patterns

### ✅ Good Example: model_runner.py (lines 70-76)
```python
try:
    log_dir_path_str = os.path.join(SCRIPT_DIR, args.log_dir) if not os.path.isabs(args.log_dir) else args.log_dir
    log_dir_path_obj = validate_directory_path(log_dir_path_str, create_if_missing=True)
    log_dir_path = str(log_dir_path_obj)
except (ValueError, FileNotFoundError) as e:
    print(f"Error: Invalid log directory path: {e}")
    exit(1)
```
**Why Good**: Catches specific exceptions, clear error message, proper exit

### ❌ Bad Example: config.py (line 68)
```python
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
        return _merge_configs(DEFAULT_CONFIG, config)
except Exception as e:  # Too broad!
    plog.log_error(None, f"Could not load config.yaml: {e}")
    plog.log_info(None, "Using default configuration.")
    return DEFAULT_CONFIG
```
**Why Bad**:
- Catches ALL exceptions (including KeyboardInterrupt, SystemExit)
- Hides programming errors (NameError, AttributeError)
- Makes debugging harder

## Problems with Broad Exception Handling

1. **Hides bugs**: Programming errors caught and ignored
2. **Poor debugging**: Stack traces lost
3. **Unexpected behavior**: Catches system exceptions (KeyboardInterrupt)
4. **Security**: Can hide security-related errors
5. **Maintenance**: Harder to understand what can go wrong

## Proposed Standards

### 1. Use Specific Exceptions

```python
# ❌ Don't do this
except Exception as e:
    pass

# ✅ Do this
except (FileNotFoundError, PermissionError, yaml.YAMLError) as e:
    pass
```

### 2. Create Custom Exceptions

```python
# helpers.py or exceptions.py
class ExpensePredictorError(Exception):
    """Base exception for expense predictor."""
    pass

class DataValidationError(ExpensePredictorError):
    """Raised when data validation fails."""
    pass

class ConfigurationError(ExpensePredictorError):
    """Raised when configuration is invalid."""
    pass

class ModelTrainingError(ExpensePredictorError):
    """Raised when model training fails."""
    pass
```

### 3. Use Custom Exceptions

```python
# Before
def validate_csv_file(file_path, logger=None):
    if not os.path.exists(file_path):
        plog.log_error(logger, f"CSV file not found: {file_path}")
        raise FileNotFoundError(f"CSV file not found: {file_path}")

# After
def validate_csv_file(file_path, logger=None):
    if not os.path.exists(file_path):
        plog.log_error(logger, f"CSV file not found: {file_path}")
        raise DataValidationError(f"CSV file not found: {file_path}")
```

### 4. Proper Error Context

```python
# ❌ Loses context
except yaml.YAMLError as e:
    raise ConfigurationError("Failed to load config")

# ✅ Preserves context
except yaml.YAMLError as e:
    raise ConfigurationError(f"Failed to load config: {e}") from e
```

## Files to Update

### Priority 1: Critical Error Handling
- [ ] `config.py` line 68 - Replace `except Exception`
- [ ] `helpers.py` lines 101-103 - Replace `except Exception`

### Priority 2: Add Custom Exceptions
- [ ] Create `exceptions.py` with custom exception classes
- [ ] Update all modules to use custom exceptions

### Priority 3: Improve Error Messages
- [ ] Add context to error messages
- [ ] Include relevant variable values
- [ ] Add suggestions for fixing common errors

## Specific Changes Required

### config.py (line 68)
```python
# Before
except Exception as e:
    plog.log_error(None, f"Could not load config.yaml: {e}")

# After
except (FileNotFoundError, PermissionError) as e:
    plog.log_error(None, f"Could not access config.yaml: {e}")
except yaml.YAMLError as e:
    plog.log_error(None, f"Invalid YAML in config.yaml: {e}")
except Exception as e:
    # Only as last resort with re-raise
    plog.log_error(None, f"Unexpected error loading config.yaml: {e}")
    raise
```

### helpers.py (line 101-103)
```python
# Before
except Exception as e:
    plog.log_error(logger, f"Excel file is corrupted or invalid: {e}")
    raise ValueError(f"Excel file is corrupted or cannot be read: {e}")

# After
except (xlrd.XLRDError, openpyxl.utils.exceptions.InvalidFileException) as e:
    plog.log_error(logger, f"Excel file is corrupted or invalid: {e}")
    raise DataValidationError(f"Excel file is corrupted or cannot be read: {e}") from e
```

## Acceptance Criteria

- [ ] No bare `except:` statements
- [ ] `except Exception` only used as last resort with documentation
- [ ] Custom exception classes created and documented
- [ ] All specific exceptions caught with appropriate handlers
- [ ] Error messages include context and actionable information
- [ ] Tests added for error conditions
- [ ] Documentation updated with exception specifications

## Testing

Add tests for exception handling:
```python
def test_config_load_invalid_yaml(tmp_path):
    """Test config loading with invalid YAML."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("invalid: yaml: content:")

    with pytest.raises(ConfigurationError) as exc_info:
        load_config()

    assert "Invalid YAML" in str(exc_info.value)
```

## References

- [PEP 8 - Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)
- [Python Exception Hierarchy](https://docs.python.org/3/library/exceptions.html#exception-hierarchy)
- [Best Practices for Exception Handling](https://realpython.com/python-exceptions/)

## Related Files
- `config.py`
- `helpers.py`
- `security.py`
- `model_runner.py`
- New: `exceptions.py` (to create)
