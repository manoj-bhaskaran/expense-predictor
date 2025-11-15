# [LOW] Add .pre-commit-config.yaml file

## Priority
🔵 **Low Priority**

## Labels
`enhancement`, `developer-experience`, `good-first-issue`

## Description

`pre-commit` is included in `requirements-dev.txt` and there's a pre-commit workflow in CI/CD, but there's no `.pre-commit-config.yaml` file to enable local pre-commit hooks.

## Current State

### pre-commit in dependencies
```python
# requirements-dev.txt:39
pre-commit==3.4.0
```

### Pre-commit workflow exists
```yaml
# .github/workflows/pre-commit.yml
name: Pre-commit Checks
# ... runs flake8, black, isort, mypy
```

### Missing
- ❌ No `.pre-commit-config.yaml` file
- ❌ Developers can't run `pre-commit install`
- ❌ No automatic local checks before commit

## Benefits of Pre-commit Hooks

1. **Catch issues early**: Before pushing to CI/CD
2. **Faster feedback**: Local checks are faster than CI/CD
3. **Consistent formatting**: Auto-format code on commit
4. **Reduced CI failures**: Fewer failed builds
5. **Better DX**: Developers know about issues immediately

## Proposed Solution

Create `.pre-commit-config.yaml`:

```yaml
# .pre-commit-config.yaml
# See https://pre-commit.com for more information

default_language_version:
  python: python3.9

repos:
  # Code formatting
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.9
        args: ['--line-length=127']

  # Import sorting
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ['--profile', 'black', '--line-length=127']

  # Linting
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=127', '--max-complexity=10']
        additional_dependencies: [flake8-docstrings]

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]
        args: ['--ignore-missing-imports']

  # Security scanning
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', '.', '--exclude', './tests']

  # Basic checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-case-conflict
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements
      - id: mixed-line-ending

  # YAML linting
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.32.0
    hooks:
      - id: yamllint
        args: ['-d', '{extends: default, rules: {line-length: {max: 120}}}']
```

## Setup Instructions (for developers)

Add to CONTRIBUTING.md:

```markdown
### Setting Up Pre-commit Hooks

Pre-commit hooks automatically check your code before each commit.

1. **Install pre-commit** (included in dev dependencies):
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Install the git hooks**:
   ```bash
   pre-commit install
   ```

3. **Run on all files** (optional, first time):
   ```bash
   pre-commit run --all-files
   ```

Now pre-commit hooks will run automatically on `git commit`.

### Skipping Hooks (when necessary)

In rare cases, you may need to skip hooks:
```bash
git commit --no-verify -m "Emergency fix"
```

**Note**: Use sparingly - CI/CD will still run the checks.

### Updating Hooks

Keep hooks up to date:
```bash
pre-commit autoupdate
```
```

## Configuration Options

### Auto-fix vs Check-only

**Auto-fix** (recommended for formatters):
- `black` - Auto-formats code
- `isort` - Auto-sorts imports
- `trailing-whitespace` - Auto-removes trailing whitespace

**Check-only** (for linters):
- `flake8` - Reports issues, doesn't fix
- `mypy` - Reports type errors
- `bandit` - Reports security issues

### Performance Optimization

For faster commits, you can:

1. **Run only on changed files** (default behavior)
2. **Skip slow hooks during development**:
   ```bash
   SKIP=mypy,bandit git commit -m "WIP"
   ```

3. **Run checks in parallel** (pre-commit does this automatically)

## Testing the Configuration

After creating the file:

```bash
# Install hooks
pre-commit install

# Run on all files to test
pre-commit run --all-files

# Make a test commit
echo "test" >> README.md
git add README.md
git commit -m "Test pre-commit hooks"
```

## Integration with CI/CD

The pre-commit configuration should match CI/CD checks:

| Check | Pre-commit | CI/CD Workflow |
|-------|-----------|----------------|
| black | ✅ Auto-fix | ✅ Check in pre-commit.yml |
| isort | ✅ Auto-fix | ✅ Check in pre-commit.yml |
| flake8 | ✅ Check | ✅ Check in pre-commit.yml |
| mypy | ✅ Check | ✅ Check in pre-commit.yml |
| bandit | ✅ Check | ✅ security.yml |
| pytest | ❌ Too slow | ✅ test.yml |

## Acceptance Criteria

- [ ] `.pre-commit-config.yaml` created
- [ ] Configuration matches CI/CD checks
- [ ] Hooks install successfully: `pre-commit install`
- [ ] Hooks run successfully: `pre-commit run --all-files`
- [ ] Documentation added to CONTRIBUTING.md
- [ ] README mentions pre-commit hooks
- [ ] File versions match requirements-dev.txt versions
- [ ] All team members can install and use hooks

## Optional Enhancements

### 1. Add commit message linting
```yaml
- repo: https://github.com/commitizen-tools/commitizen
  rev: v3.5.0
  hooks:
    - id: commitizen
```

### 2. Add Markdown linting
```yaml
- repo: https://github.com/igorshubovych/markdownlint-cli
  rev: v0.35.0
  hooks:
    - id: markdownlint
```

### 3. Add Python docstring coverage check
```yaml
- repo: https://github.com/econchick/interrogate
  rev: 1.5.0
  hooks:
    - id: interrogate
      args: [--fail-under=80]
```

## Related Files
- New: `.pre-commit-config.yaml`
- `requirements-dev.txt`
- `.github/workflows/pre-commit.yml`
- `CONTRIBUTING.md`
- `README.md`

## References
- [pre-commit documentation](https://pre-commit.com/)
- [Supported hooks](https://pre-commit.com/hooks.html)
