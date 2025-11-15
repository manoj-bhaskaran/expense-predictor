# Add Type Validation for config.yaml Values

## Summary
`config.yaml` is loaded with `yaml.safe_load()` but there's no validation of data types. If a user provides incorrect types (e.g., string instead of int), the code will crash with confusing error messages.

## Impact
- **Severity:** High
- Poor user experience with cryptic error messages
- Runtime crashes in production
- Security risk: unexpected types could cause issues
- Hard to debug for non-technical users

## Current Behavior
Config is loaded and merged with defaults, but no type checking:

```python
# config.py:61
config = yaml.safe_load(f)
return _merge_configs(DEFAULT_CONFIG, config)
```

If user has:
```yaml
decision_tree:
  max_depth: "five"  # String instead of int
```

The error occurs much later during model training:
```
TypeError: '<=' not supported between instances of 'str' and 'int'
```

## Expected Behavior
Early validation with clear error messages:
```
ConfigurationError: Invalid type for 'decision_tree.max_depth': expected int, got str ('five')
```

## Examples of Invalid Configs

**Example 1 - Wrong type:**
```yaml
model_evaluation:
  test_size: "0.2"  # String instead of float
```

**Example 2 - Out of range:**
```yaml
model_evaluation:
  test_size: 2.0  # Should be 0.0-1.0
```

**Example 3 - Invalid enum:**
```yaml
logging:
  level: TRACE  # Invalid log level
```

**Example 4 - Wrong structure:**
```yaml
decision_tree: "use_defaults"  # Should be dict, not string
```

## Proposed Solution

### Option 1: Manual Validation (Simple)
Add validation function:

```python
def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration types and ranges.

    Raises:
        ConfigurationError: If validation fails
    """
    # Validate logging level
    if "logging" in config and "level" in config["logging"]:
        level = config["logging"]["level"]
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level not in valid_levels:
            raise ConfigurationError(
                f"Invalid logging level: '{level}'. "
                f"Must be one of {valid_levels}"
            )

    # Validate model_evaluation
    if "model_evaluation" in config:
        test_size = config["model_evaluation"].get("test_size")
        if test_size is not None:
            if not isinstance(test_size, (int, float)):
                raise ConfigurationError(
                    f"model_evaluation.test_size must be numeric, "
                    f"got {type(test_size).__name__}"
                )
            if not 0.0 < test_size < 1.0:
                raise ConfigurationError(
                    f"model_evaluation.test_size must be between 0 and 1, "
                    f"got {test_size}"
                )

    # Validate decision_tree hyperparameters
    if "decision_tree" in config:
        dt_config = config["decision_tree"]

        # max_depth
        if "max_depth" in dt_config:
            if not isinstance(dt_config["max_depth"], int):
                raise ConfigurationError(
                    f"decision_tree.max_depth must be int, "
                    f"got {type(dt_config['max_depth']).__name__}"
                )
            if dt_config["max_depth"] < 1:
                raise ConfigurationError(
                    f"decision_tree.max_depth must be >= 1, "
                    f"got {dt_config['max_depth']}"
                )

        # Similar for other parameters...

    # Continue for random_forest, gradient_boosting...
```

Update load_config():
```python
def load_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = yaml.safe_load(f)
                merged = _merge_configs(DEFAULT_CONFIG, config)
                validate_config(merged)  # Add this line
                return merged
        except ConfigurationError:
            raise  # Re-raise validation errors
        except (FileNotFoundError, PermissionError) as e:
            # ... existing code ...
```

### Option 2: Use Pydantic (Recommended for Larger Projects)
Install pydantic and create schema:

```python
from pydantic import BaseModel, Field, validator
from typing import Literal

class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

class DataProcessingConfig(BaseModel):
    skiprows: int = Field(default=12, ge=0)

class ModelEvaluationConfig(BaseModel):
    test_size: float = Field(default=0.2, gt=0.0, lt=1.0)
    random_state: int = Field(default=42, ge=0)

class DecisionTreeConfig(BaseModel):
    max_depth: int = Field(default=5, ge=1)
    min_samples_split: int = Field(default=10, ge=2)
    min_samples_leaf: int = Field(default=5, ge=1)
    ccp_alpha: float = Field(default=0.01, ge=0.0)
    random_state: int = Field(default=42, ge=0)

class Config(BaseModel):
    logging: LoggingConfig = LoggingConfig()
    data_processing: DataProcessingConfig = DataProcessingConfig()
    model_evaluation: ModelEvaluationConfig = ModelEvaluationConfig()
    decision_tree: DecisionTreeConfig = DecisionTreeConfig()
    # ... other configs ...

def load_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                raw_config = yaml.safe_load(f)
                # Validate with pydantic
                validated = Config(**raw_config if raw_config else {})
                return validated.model_dump()
        except Exception as e:
            # Handle validation errors...
```

### Option 3: JSON Schema Validation
Use JSON Schema for YAML validation:

```python
import jsonschema

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "logging": {
            "type": "object",
            "properties": {
                "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
            }
        },
        "model_evaluation": {
            "type": "object",
            "properties": {
                "test_size": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "random_state": {"type": "integer", "minimum": 0}
            }
        },
        # ... more schema ...
    }
}

def validate_config(config: Dict[str, Any]) -> None:
    try:
        jsonschema.validate(config, CONFIG_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ConfigurationError(f"Invalid configuration: {e.message}") from e
```

## Recommendation
- **Short term:** Option 1 (Manual Validation) - no new dependencies
- **Long term:** Option 2 (Pydantic) - if project grows, provides better type safety

## Testing
Add tests in `tests/test_config.py`:

```python
def test_invalid_logging_level():
    """Test that invalid logging level raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="Invalid logging level"):
        validate_config({"logging": {"level": "TRACE"}})

def test_invalid_test_size_type():
    """Test that non-numeric test_size raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="must be numeric"):
        validate_config({"model_evaluation": {"test_size": "0.2"}})

def test_test_size_out_of_range():
    """Test that test_size > 1.0 raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="between 0 and 1"):
        validate_config({"model_evaluation": {"test_size": 2.0}})

def test_invalid_max_depth_type():
    """Test that non-int max_depth raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="must be int"):
        validate_config({"decision_tree": {"max_depth": "five"}})
```

## Benefits
1. Better user experience with clear error messages
2. Fail fast - errors at startup, not during training
3. Self-documenting configuration schema
4. Prevents subtle bugs from type mismatches
5. Easier debugging for users

## Labels
- enhancement
- configuration
- validation
- user-experience
