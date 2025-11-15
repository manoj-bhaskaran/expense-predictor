# [MEDIUM] Create .env.example file and implement environment variable loading

## Priority
🟡 **Medium Priority**

## Labels
`enhancement`, `configuration`, `documentation`

## Description

README.md mentions `.env.example` and environment-based configuration, but:
1. The `.env.example` file doesn't exist
2. No code loads environment variables
3. The feature is mentioned but not implemented

## Current State

### README.md (line 94)
```markdown
No environment variables are strictly required, but you can create a `.env`
file based on `.env.example` for custom default paths.
```

### Problems
- ❌ `.env.example` file doesn't exist
- ❌ No `python-dotenv` in requirements
- ❌ No code to load `.env` file
- ❌ Feature is mentioned but not functional

## Proposed Solution

### Option 1: Implement the Feature (Recommended)

This makes sense for users who want to:
- Set default paths without command-line arguments
- Configure different environments (dev, staging, prod)
- Keep sensitive paths out of version control

#### Step 1: Create `.env.example`
```bash
# .env.example
# Expense Predictor Environment Configuration
# Copy this file to .env and customize the values

# Default data file path (optional)
# If not set, will use --data_file argument or default 'trandata.csv'
# EXPENSE_PREDICTOR_DATA_FILE=./data/trandata.csv

# Default Excel directory (optional)
# EXPENSE_PREDICTOR_EXCEL_DIR=./data

# Default Excel file name (optional)
# EXPENSE_PREDICTOR_EXCEL_FILE=bank_statement.xls

# Default log directory (optional)
# EXPENSE_PREDICTOR_LOG_DIR=./logs

# Default output directory (optional)
# EXPENSE_PREDICTOR_OUTPUT_DIR=./predictions

# Default future date for predictions (optional, format: DD/MM/YYYY)
# EXPENSE_PREDICTOR_FUTURE_DATE=31/12/2025

# Skip confirmation prompts (optional, true/false)
# EXPENSE_PREDICTOR_SKIP_CONFIRMATION=false
```

#### Step 2: Add python-dotenv to requirements.txt
```python
# requirements.txt
...
pyyaml==6.0.1
python-dotenv==1.0.0  # Add this
```

#### Step 3: Load environment variables in model_runner.py
```python
# model_runner.py - at the top
from dotenv import load_dotenv
import os

# Load .env file if it exists
load_dotenv()

# Set up argument parser with env var defaults
parser = argparse.ArgumentParser(description='Expense Predictor')
parser.add_argument(
    '--future_date',
    type=str,
    default=os.getenv('EXPENSE_PREDICTOR_FUTURE_DATE'),
    help='Future date for prediction (e.g., 31/12/2025)'
)
parser.add_argument(
    '--excel_dir',
    type=str,
    default=os.getenv('EXPENSE_PREDICTOR_EXCEL_DIR', '.'),
    help='Directory where the Excel file is located'
)
parser.add_argument(
    '--excel_file',
    type=str,
    default=os.getenv('EXPENSE_PREDICTOR_EXCEL_FILE'),
    help='Name of the Excel file containing additional data'
)
parser.add_argument(
    '--data_file',
    type=str,
    default=os.getenv('EXPENSE_PREDICTOR_DATA_FILE', 'trandata.csv'),
    help='Path to the CSV file containing transaction data'
)
parser.add_argument(
    '--log_dir',
    type=str,
    default=os.getenv('EXPENSE_PREDICTOR_LOG_DIR', 'logs'),
    help='Directory where log files will be saved'
)
parser.add_argument(
    '--output_dir',
    type=str,
    default=os.getenv('EXPENSE_PREDICTOR_OUTPUT_DIR', '.'),
    help='Directory where prediction files will be saved'
)
parser.add_argument(
    '--skip_confirmation',
    action='store_true',
    default=os.getenv('EXPENSE_PREDICTOR_SKIP_CONFIRMATION', 'false').lower() == 'true',
    help='Skip confirmation prompts for overwriting files'
)
```

#### Step 4: Update .gitignore
```gitignore
# .gitignore
...
# Environment
.env        # Keep this - already there
venv/
...
```

#### Step 5: Update documentation

README.md:
```markdown
## Configuration

The project supports multiple configuration methods (in priority order):

1. **Command-line arguments** (highest priority)
2. **Environment variables** (.env file)
3. **Configuration file** (config.yaml)
4. **Default values** (lowest priority)

### Environment Variables

Create a `.env` file for default values:

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred defaults
nano .env
```

Example `.env`:
```bash
EXPENSE_PREDICTOR_DATA_FILE=./data/transactions.csv
EXPENSE_PREDICTOR_LOG_DIR=./my_logs
EXPENSE_PREDICTOR_OUTPUT_DIR=./predictions
```

Command-line arguments override environment variables:
```bash
# Uses .env values
python model_runner.py

# Overrides .env data_file
python model_runner.py --data_file ./other_data.csv
```
```

### Option 2: Remove the Feature Reference

If environment variables aren't needed, remove references:

```diff
- No environment variables are strictly required, but you can create a `.env`
- file based on `.env.example` for custom default paths.
```

## Recommendation

**Implement Option 1** - It's a useful feature that:
- Makes the tool more user-friendly
- Allows different configurations per environment
- Follows common Python project practices
- Minimal implementation effort

## Use Cases

### Use Case 1: Development Environment
```bash
# .env
EXPENSE_PREDICTOR_DATA_FILE=./test_data/sample.csv
EXPENSE_PREDICTOR_LOG_DIR=./dev_logs
EXPENSE_PREDICTOR_SKIP_CONFIRMATION=true
```

### Use Case 2: Production Environment
```bash
# .env
EXPENSE_PREDICTOR_DATA_FILE=/data/production/transactions.csv
EXPENSE_PREDICTOR_EXCEL_DIR=/data/production
EXPENSE_PREDICTOR_LOG_DIR=/var/log/expense-predictor
EXPENSE_PREDICTOR_OUTPUT_DIR=/data/predictions
EXPENSE_PREDICTOR_SKIP_CONFIRMATION=true
```

### Use Case 3: Docker Container
```dockerfile
# Dockerfile
ENV EXPENSE_PREDICTOR_DATA_FILE=/app/data/transactions.csv
ENV EXPENSE_PREDICTOR_LOG_DIR=/app/logs
```

## Implementation Checklist

- [ ] Create `.env.example` file with all supported variables
- [ ] Add `python-dotenv==1.0.0` to `requirements.txt`
- [ ] Add `python-dotenv==1.0.0` to `setup.py` install_requires
- [ ] Update `model_runner.py` to load and use environment variables
- [ ] Verify `.env` is in `.gitignore`
- [ ] Update README with environment variable documentation
- [ ] Add environment variables section to CONTRIBUTING.md
- [ ] Test with various combinations of env vars and CLI args
- [ ] Test with no `.env` file (should use defaults)
- [ ] Update CHANGELOG

## Testing

Add tests for environment variable loading:

```python
# tests/test_env_loading.py

def test_env_var_loading(monkeypatch, tmp_path):
    """Test that environment variables are loaded correctly."""
    monkeypatch.setenv('EXPENSE_PREDICTOR_DATA_FILE', '/custom/path.csv')

    # Load and parse args
    # Verify environment variable is used as default
    pass

def test_cli_args_override_env_vars(monkeypatch):
    """Test that CLI arguments override environment variables."""
    monkeypatch.setenv('EXPENSE_PREDICTOR_DATA_FILE', '/env/path.csv')

    # Parse with --data_file /cli/path.csv
    # Verify CLI argument takes precedence
    pass
```

## Acceptance Criteria

- [ ] `.env.example` file created and documented
- [ ] `python-dotenv` added to dependencies
- [ ] Environment variables loaded in `model_runner.py`
- [ ] CLI arguments override environment variables
- [ ] Works without `.env` file (uses defaults)
- [ ] Documentation updated
- [ ] Tests added for environment variable loading
- [ ] `.env` confirmed in `.gitignore`

## Related Files
- New: `.env.example`
- `requirements.txt`
- `requirements-dev.txt`
- `setup.py`
- `model_runner.py`
- `README.md`
- `CONTRIBUTING.md`
- `.gitignore`
