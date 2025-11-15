# Contributing to Expense Predictor

Thank you for your interest in contributing to the Expense Predictor! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize the community's best interests

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Publishing others' private information
- Unprofessional conduct

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of machine learning concepts
- Familiarity with pandas and scikit-learn

### Areas for Contribution

We welcome contributions in these areas:

1. **Bug Fixes**: Fix reported issues
2. **Features**: Implement new functionality
3. **Documentation**: Improve or add documentation
4. **Tests**: Add or improve test coverage
5. **Performance**: Optimize code performance
6. **Security**: Enhance security features

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/expense-predictor.git
cd expense-predictor
```

### 2. Add Upstream Remote

```bash
git remote add upstream https://github.com/manoj-bhaskaran/expense-predictor.git
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 5. Configure Environment Variables (Optional)

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your development settings
nano .env

# Example development .env:
# EXPENSE_PREDICTOR_DATA_FILE=./test_data/sample.csv
# EXPENSE_PREDICTOR_LOG_DIR=./dev_logs
# EXPENSE_PREDICTOR_SKIP_CONFIRMATION=true
```

**Note:** The `.env` file is in `.gitignore` and will not be committed to version control. This allows each developer to have their own local configuration without affecting others.

### 6. Verify Setup

```bash
# Run tests to verify everything works
pytest tests/ -v

# Check code style
flake8 .
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a new branch for your work
git checkout -b feature/your-feature-name
```

**Branch Naming Conventions**:
- `feature/` - New features (e.g., `feature/add-lstm-model`)
- `fix/` - Bug fixes (e.g., `fix/date-parsing-error`)
- `docs/` - Documentation only (e.g., `docs/update-readme`)
- `test/` - Test additions/improvements (e.g., `test/add-helpers-tests`)
- `refactor/` - Code refactoring (e.g., `refactor/extract-validation`)

### 2. Make Your Changes

- Write clean, readable code
- Follow the code style guidelines (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_helpers.py -v

# Run code quality checks
flake8 .
black --check .
isort --check .
mypy .
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

See [Commit Message Guidelines](#commit-message-guidelines) for details.

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a pull request on GitHub.

## Code Style Guidelines

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some specific preferences:

#### General Rules

- **Line Length**: Maximum 100 characters (not the default 79)
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8
- **Imports**: Organized with isort
- **Formatting**: Automated with Black

#### Code Formatting Tools

**Black** (code formatter):
```bash
# Check formatting
black --check .

# Auto-format code
black .
```

**isort** (import sorting):
```bash
# Check import sorting
isort --check .

# Auto-sort imports
isort .
```

**flake8** (linting):
```bash
flake8 .
```

**mypy** (type checking):
```bash
mypy .
```

#### Naming Conventions

- **Functions/Variables**: `snake_case`
  ```python
  def preprocess_data(df, logger=None):
      transaction_amount = df['Tran Amt']
  ```

- **Classes**: `PascalCase`
  ```python
  class DataValidator:
      pass
  ```

- **Constants**: `UPPER_SNAKE_CASE`
  ```python
  DEFAULT_LOG_DIR = "logs"
  MAX_ITERATIONS = 100
  ```

- **Private Functions**: Prefix with `_`
  ```python
  def _process_dataframe(df):
      pass
  ```

#### Docstring Format

Use Google-style docstrings:

```python
def validate_csv_file(file_path, logger=None):
    """Validate that a CSV file exists and contains required columns.

    Args:
        file_path (str): Path to the CSV file to validate.
        logger (object, optional): Logger instance for logging messages.
            Defaults to None.

    Returns:
        tuple: (is_valid, error_message) where is_valid is a boolean
            and error_message is a string (empty if valid).

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns are missing.

    Example:
        >>> is_valid, error = validate_csv_file("trandata.csv")
        >>> if not is_valid:
        ...     print(error)
    """
    pass
```

#### Type Hints

Use type hints for function signatures (Python 3.9+):

```python
from typing import Optional, Tuple
import pandas as pd

def preprocess_data(
    file_path: str,
    logger: Optional[object] = None
) -> Tuple[pd.DataFrame, pd.Series]:
    """Process the input data."""
    pass
```

#### Comments

- Use comments for **why**, not **what**
- Keep comments up-to-date with code changes
- Use TODO comments for future improvements

```python
# Good: Explains why
# Use shuffle=False to preserve temporal order for time series data
X_train, X_test = train_test_split(X, shuffle=False)

# Bad: States the obvious
# Split the data into train and test
X_train, X_test = train_test_split(X)
```

### Configuration Files

- **YAML**: Use 2-space indentation for `config.yaml`
- **JSON**: Use 2-space indentation
- **Markdown**: Follow CommonMark specification

## Testing Requirements

### Test Coverage

- **Minimum Coverage**: 80% (enforced by CI/CD)
- **New Code**: All new code must have tests
- **Bug Fixes**: Add test case that reproduces the bug

### Writing Tests

#### Test Structure

```python
import pytest
from helpers import validate_csv_file

class TestValidateCsvFile:
    """Test suite for validate_csv_file function."""

    def test_valid_csv_file(self, temp_csv_file):
        """Test that a valid CSV file passes validation."""
        is_valid, error = validate_csv_file(temp_csv_file)
        assert is_valid
        assert error == ""

    def test_missing_file(self):
        """Test that a non-existent file fails validation."""
        is_valid, error = validate_csv_file("nonexistent.csv")
        assert not is_valid
        assert "not found" in error.lower()
```

#### Test Fixtures

Use pytest fixtures for reusable test data:

```python
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'Date': ['01/01/2024', '02/01/2024'],
        'Tran Amt': [100.0, 150.0]
    })
```

#### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_data_validation():
    """Unit test for data validation."""
    pass

@pytest.mark.integration
def test_full_pipeline():
    """Integration test for complete pipeline."""
    pass

@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset (slow)."""
    pass
```

Run specific test categories:
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

#### Mocking

Use pytest-mock for external dependencies:

```python
def test_with_logger(mocker):
    """Test function with mocked logger."""
    mock_logger = mocker.Mock()
    result = my_function(logger=mock_logger)

    # Verify logger was called
    mock_logger.log_info.assert_called_once()
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_helpers.py

# Run specific test class
pytest tests/test_helpers.py::TestValidateCsvFile

# Run specific test function
pytest tests/test_helpers.py::TestValidateCsvFile::test_valid_csv_file

# Run with verbose output
pytest tests/ -v

# Run with short traceback
pytest tests/ --tb=short
```

## Pull Request Process

### Before Submitting

1. **Update from upstream**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature
   git rebase main
   ```

2. **Run all checks**
   ```bash
   # Code formatting
   black .
   isort .

   # Linting
   flake8 .

   # Type checking
   mypy .

   # Tests with coverage
   pytest tests/ --cov=. --cov-report=term-missing
   ```

3. **Update documentation**
   - Update README.md if needed
   - Update CHANGELOG.md
   - Add docstrings to new functions
   - Update relevant .md files

### Pull Request Template

Use this template for your PR description:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Related Issue
Fixes #(issue number)

## Changes Made
- Bullet point list of changes

## Testing
- [ ] All tests pass locally
- [ ] Added tests for new functionality
- [ ] Test coverage meets 80% threshold

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. **Automated Checks**: CI/CD runs automatically
   - Tests must pass (Python 3.9, 3.10, 3.11)
   - Code coverage ≥ 80%
   - Linting (flake8) must pass
   - Type checking (mypy) must pass
   - Security scans must pass

2. **Code Review**: Maintainer reviews your code
   - Responds within 3-5 business days
   - May request changes or clarifications

3. **Merge**: Once approved and checks pass
   - Squash and merge for clean history
   - Delete feature branch after merge

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring (no functional changes)
- `perf`: Performance improvements
- `style`: Code style changes (formatting, no logic changes)
- `chore`: Build process or auxiliary tool changes
- `ci`: CI/CD configuration changes

### Examples

```bash
# Simple feature
git commit -m "feat: add support for Excel 2019 format"

# Bug fix with issue reference
git commit -m "fix: resolve date parsing error for DD/MM/YYYY format

Fixes #42"

# Breaking change
git commit -m "feat!: change prediction output format to JSON

BREAKING CHANGE: Prediction files now output JSON instead of CSV.
Update your parsing code accordingly."

# Documentation
git commit -m "docs: add architecture documentation"

# Scoped commit
git commit -m "test(helpers): add validation tests for Excel files"
```

### Subject Line Rules

- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters
- Be specific and descriptive

## Documentation Guidelines

### When to Update Documentation

- Adding new features
- Changing existing functionality
- Fixing bugs that affect usage
- Adding new dependencies
- Changing configuration options
- Adding new environment variables

### Documentation Files

- **README.md**: User-facing documentation, installation, usage
- **ARCHITECTURE.md**: System design, technical decisions
- **CONTRIBUTING.md**: This file - contributor guidelines
- **CHANGELOG.md**: Version history and changes
- **DATA.md**: Data format specifications
- **MODELS.md**: Model evaluation and selection guide

### Docstring Requirements

All public functions must have docstrings:

```python
def public_function(arg1, arg2, logger=None):
    """Brief one-line description.

    Longer description if needed, explaining what the function
    does, why it exists, and any important details.

    Args:
        arg1 (str): Description of arg1.
        arg2 (int): Description of arg2.
        logger (object, optional): Logger instance. Defaults to None.

    Returns:
        bool: Description of return value.

    Raises:
        ValueError: When validation fails.

    Example:
        >>> result = public_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

### Code Comments

- Document complex algorithms
- Explain non-obvious decisions
- Reference issue numbers for bug fixes
- Use TODO for future improvements

```python
# TODO(#123): Optimize this loop for large datasets
# Using quadratic search here because dataset is small (<100 items)
# and code clarity is more important than performance
```

## Reporting Bugs

### Before Reporting

1. **Check existing issues**: Search for similar bugs
2. **Verify it's a bug**: Test with clean installation
3. **Gather information**: Logs, error messages, steps to reproduce

### Bug Report Template

```markdown
**Bug Description**
A clear and concise description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With input file '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Error Messages**
```
Paste error messages here
```

**Environment**
- OS: [e.g., Ubuntu 22.04, Windows 11, macOS 13]
- Python version: [e.g., 3.11.2]
- Package versions: [run `pip list`]

**Additional Context**
- Sample data (anonymized)
- Log files
- Screenshots if applicable
```

## Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature.

**Problem It Solves**
What problem does this feature address?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
What other approaches did you consider?

**Additional Context**
- Use cases
- Examples from other projects
- Mockups or diagrams
```

### Feature Evaluation Criteria

Features are evaluated based on:
- **Usefulness**: Benefits to users
- **Scope**: Fits project goals
- **Complexity**: Implementation effort
- **Maintenance**: Long-term support cost
- **Breaking Changes**: Impact on existing users

## Development Tips

### Environment Variables for Development

You can set environment variables in your `.env` file for easier development:

```bash
# .env file for development
EXPENSE_PREDICTOR_DATA_FILE=./test_data/sample.csv
EXPENSE_PREDICTOR_LOG_DIR=./dev_logs
EXPENSE_PREDICTOR_OUTPUT_DIR=./dev_predictions
EXPENSE_PREDICTOR_SKIP_CONFIRMATION=true
```

This allows you to run the application without specifying command-line arguments:

```bash
# Uses values from .env
python model_runner.py

# Override specific values
python model_runner.py --data_file ./other_data.csv
```

**Priority order:**
1. Command-line arguments (highest)
2. Environment variables (.env file)
3. Configuration file (config.yaml)
4. Default values (lowest)

### Helpful Commands

```bash
# Auto-fix code style issues
black .
isort .

# Check for security issues
bandit -r .

# Profile code performance
python -m cProfile model_runner.py --data_file trandata.csv

# Generate test coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html  # View in browser

# Find todos in code
grep -r "TODO" --include="*.py" .
```

### Debugging

Enable detailed logging:
```bash
python model_runner.py --data_file trandata.csv --log_dir ./debug_logs
```

Use IPython for interactive debugging:
```python
# Add this line where you want to break
import ipdb; ipdb.set_trace()
```

### Performance Profiling

```bash
# Line-by-line profiling
pip install line-profiler
kernprof -l -v model_runner.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler model_runner.py
```

## Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Security issues**: Email maintainers privately (see SECURITY.md)
- **Pull requests**: Create PR and request review

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Thank you for contributing to the Expense Predictor! Your efforts help make this project better for everyone.
