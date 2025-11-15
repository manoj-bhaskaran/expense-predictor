# [LOW] Add configurable log levels

## Priority
🔵 **Low Priority**

## Labels
`enhancement`, `logging`, `good-first-issue`

## Description

Log level is currently hardcoded to `logging.INFO` in `model_runner.py`. Users cannot easily change verbosity for debugging or production environments without modifying code.

## Current State

```python
# model_runner.py:78-82
logger = plog.initialise_logger(
    script_name='model_runner.py',
    log_dir=log_dir_path,
    log_level=logging.INFO  # ❌ Hardcoded
)
```

## Use Cases

### Development
```bash
# Debug level for troubleshooting
python model_runner.py --log-level DEBUG --data_file sample.csv
```

### Production
```bash
# Warning level to reduce log volume
python model_runner.py --log-level WARNING --data_file production.csv
```

### CI/CD
```bash
# Error level for cleaner CI output
python model_runner.py --log-level ERROR --data_file test.csv
```

## Proposed Solutions

### Option 1: Command-Line Argument (Recommended)

```python
# model_runner.py

# Add to argument parser
parser.add_argument(
    '--log-level',
    type=str,
    default='INFO',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    help='Logging level (default: INFO)'
)

# Convert string to logging level
log_level = getattr(logging, args.log_level.upper())

logger = plog.initialise_logger(
    script_name='model_runner.py',
    log_dir=log_dir_path,
    log_level=log_level
)
```

### Option 2: Environment Variable

```python
import os

# Get from environment or use default
log_level_str = os.getenv('EXPENSE_PREDICTOR_LOG_LEVEL', 'INFO')
log_level = getattr(logging, log_level_str.upper(), logging.INFO)

logger = plog.initialise_logger(
    script_name='model_runner.py',
    log_dir=log_dir_path,
    log_level=log_level
)
```

### Option 3: Configuration File

```yaml
# config.yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

```python
# config.py - add to DEFAULT_CONFIG
DEFAULT_CONFIG = {
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    },
    # ... rest of config
}
```

### Recommendation: Combine Options 1 & 2

Priority order:
1. Command-line argument (highest)
2. Environment variable
3. Config file
4. Default (INFO)

```python
# model_runner.py

# Add CLI argument
parser.add_argument(
    '--log-level',
    type=str,
    default=None,  # Will check other sources
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    help='Logging level (default: INFO)'
)

args = parser.parse_args()

# Determine log level (priority order)
if args.log_level:
    log_level_str = args.log_level
elif os.getenv('EXPENSE_PREDICTOR_LOG_LEVEL'):
    log_level_str = os.getenv('EXPENSE_PREDICTOR_LOG_LEVEL')
elif 'logging' in config and 'level' in config['logging']:
    log_level_str = config['logging']['level']
else:
    log_level_str = 'INFO'

# Convert to logging constant
log_level = getattr(logging, log_level_str.upper(), logging.INFO)

logger = plog.initialise_logger(
    script_name='model_runner.py',
    log_dir=log_dir_path,
    log_level=log_level
)

plog.log_info(logger, f"Log level set to: {log_level_str}")
```

## Implementation Checklist

### Minimal Implementation (Option 1 only)
- [ ] Add `--log-level` argument to argparse
- [ ] Convert string to logging level constant
- [ ] Pass to `initialise_logger()`
- [ ] Test with different log levels
- [ ] Update README with --log-level usage

### Full Implementation (Options 1 + 2 + 3)
- [ ] Add `--log-level` CLI argument
- [ ] Check `EXPENSE_PREDICTOR_LOG_LEVEL` env var
- [ ] Add `logging.level` to `config.yaml`
- [ ] Implement priority order
- [ ] Add validation for invalid log levels
- [ ] Update `.env.example`
- [ ] Update README
- [ ] Add tests

## Usage Examples

### Command-line
```bash
# Debug mode
python model_runner.py --log-level DEBUG --data_file data.csv

# Quiet mode (warnings and errors only)
python model_runner.py --log-level WARNING --data_file data.csv

# Very quiet (errors only)
python model_runner.py --log-level ERROR --data_file data.csv
```

### Environment variable
```bash
export EXPENSE_PREDICTOR_LOG_LEVEL=DEBUG
python model_runner.py --data_file data.csv
```

### Configuration file
```yaml
# config.yaml
logging:
  level: DEBUG
```

## Testing

Add tests for log level configuration:

```python
def test_log_level_cli_argument(capsys, monkeypatch):
    """Test that --log-level CLI argument sets log level."""
    # Set up test args
    test_args = ['model_runner.py', '--log-level', 'DEBUG', '--data_file', 'test.csv']
    monkeypatch.setattr('sys.argv', test_args)

    # Verify DEBUG level is set
    # Check that DEBUG messages appear in logs
    pass

def test_log_level_env_variable(monkeypatch):
    """Test that env variable sets log level."""
    monkeypatch.setenv('EXPENSE_PREDICTOR_LOG_LEVEL', 'WARNING')

    # Verify WARNING level is set
    pass

def test_log_level_priority(monkeypatch):
    """Test that CLI argument overrides env variable."""
    monkeypatch.setenv('EXPENSE_PREDICTOR_LOG_LEVEL', 'ERROR')
    test_args = ['model_runner.py', '--log-level', 'DEBUG']

    # Verify DEBUG level is used (CLI takes precedence)
    pass
```

## Documentation Updates

### README.md

```markdown
### Logging

By default, the application logs at INFO level. You can adjust the verbosity:

```bash
# Debug mode (most verbose)
python model_runner.py --log-level DEBUG --data_file data.csv

# Normal mode (default)
python model_runner.py --data_file data.csv

# Quiet mode (warnings and errors only)
python model_runner.py --log-level WARNING --data_file data.csv

# Very quiet (errors only)
python model_runner.py --log-level ERROR --data_file data.csv
```

#### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical errors that may cause the program to fail

#### Setting Log Level

Three ways to set log level (in priority order):

1. **Command-line argument** (highest priority):
   ```bash
   python model_runner.py --log-level DEBUG
   ```

2. **Environment variable**:
   ```bash
   export EXPENSE_PREDICTOR_LOG_LEVEL=DEBUG
   python model_runner.py
   ```

3. **Configuration file** (lowest priority):
   ```yaml
   # config.yaml
   logging:
     level: DEBUG
   ```
```

### .env.example

```bash
# Logging configuration (optional)
# Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
# EXPENSE_PREDICTOR_LOG_LEVEL=INFO
```

## Benefits

1. **Debugging**: Enable DEBUG level when troubleshooting
2. **Production**: Use WARNING or ERROR to reduce log noise
3. **CI/CD**: Use ERROR level for cleaner CI output
4. **Flexibility**: Users can choose verbosity without code changes
5. **Standards**: Follows standard logging best practices

## Acceptance Criteria

- [ ] Log level can be set via CLI argument
- [ ] Invalid log levels handled gracefully
- [ ] Default level remains INFO
- [ ] Log level logged at startup
- [ ] Documentation updated
- [ ] Tests added for log level configuration
- [ ] Works with all existing functionality

## Related Files
- `model_runner.py`
- `config.yaml`
- `.env.example`
- `README.md`
- `tests/test_model_runner.py`

## Nice-to-Have Enhancements

1. **Per-module log levels**: Different levels for different modules
2. **Log format configuration**: Customizable log message format
3. **Log rotation**: Automatic log file rotation
4. **Colored output**: Color-coded log levels in console (using colorama)
