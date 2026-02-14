# Branch Protection Rules for Coverage Enforcement

This guide explains how to set up GitHub branch protection rules to enforce the 80% test coverage requirement on pull requests.

## Quick Setup

1. Go to your repository on GitHub
2. Navigate to: **Settings** → **Branches** → **Add rule**
3. Configure the following settings:

## Branch Protection Configuration

### Branch name pattern
```
main
```
(or `master` if that's your default branch)

### Protect matching branches

#### ✅ Required Settings

**Require a pull request before merging**
- ✅ Require approvals: 1
- ✅ Dismiss stale pull request approvals when new commits are pushed

**Require status checks to pass before merging**
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

**Status checks that are required:**
- ✅ `test (3.10)` - Tests on Python 3.10
- ✅ `test (3.11)` - Tests on Python 3.11
- ✅ `test (3.12)` - Tests on Python 3.12
- ✅ `test (3.13)` - Tests on Python 3.13
- ✅ `pre-commit` - Code quality checks

**Additional protections:**
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings

#### 📋 Optional Settings

**Restrict who can push to matching branches**
- Configure if you want to limit who can push to main

**Allow force pushes**
- ⚠️ **Not recommended** - Keep this disabled

**Allow deletions**
- ⚠️ **Not recommended** - Keep this disabled

## How It Works

Once configured, the branch protection will:

1. **Block merging** if any test fails
2. **Block merging** if coverage drops below 80%
3. **Require** all status checks to pass (all Python versions)
4. **Require** at least 1 approval from reviewers
5. **Ensure** branch is up-to-date with main before merging

## Coverage Enforcement

The CI/CD pipeline enforces 80% coverage in two ways:

### 1. GitHub Actions Workflow
```yaml
- name: Check coverage threshold
  run: coverage report --fail-under=80
```
This step will **fail** if total coverage is below 80%.

### 2. Coverage Configuration (.coveragerc)
```ini
[report]
fail_under = 80
```
This ensures local test runs also enforce the threshold.

## Testing the Setup

### Before Creating a Pull Request

Run tests locally to ensure they pass:
```bash
# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Check if coverage meets threshold
coverage report --fail-under=80
```

If coverage is below 80%, you'll see:
```
Coverage failure: total of XX is less than fail-under=80
```

### Creating a Test Pull Request

1. Create a new branch with changes
2. Push to GitHub
3. Create a pull request
4. Watch the status checks run:
  - Tests on Python 3.10, 3.11, 3.12, 3.13
   - Coverage enforcement
   - Code quality checks

If coverage is below 80%, the PR will show:
- ❌ **test (3.11)** - Check coverage threshold - **Failed**
- 🔴 **Merge blocked** due to failing required status checks

## Handling Coverage Failures

If your PR fails due to low coverage:

### Option 1: Add More Tests
The preferred solution - write tests for uncovered code:
```bash
# Find uncovered lines
coverage report --show-missing

# Or view HTML report
coverage html
open htmlcov/index.html
```

### Option 2: Mark Code as No Cover (Sparingly)
For truly untestable code (rare), use:
```python
def debug_only_function():  # pragma: no cover
    # This won't count against coverage
    pass
```

### Option 3: Temporarily Lower Threshold (Not Recommended)
If absolutely necessary (during large refactors):
1. Update `.coveragerc`: `fail_under = 70`
2. Create an issue to restore to 80%
3. This should be exceptional and temporary

## Monitoring Coverage Over Time

### Codecov Integration
If you've set up Codecov (optional):
- Coverage trends visible in PR comments
- Historical coverage graphs
- Diff coverage (only new code)

### Coverage Badge
Add to README.md:
```markdown
[![Coverage](https://codecov.io/gh/YOUR-USERNAME/expense-predictor/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR-USERNAME/expense-predictor)
```

## Troubleshooting

### Status checks don't appear
- Ensure workflows are in `.github/workflows/`
- Check Actions tab for workflow runs
- Verify workflows run on `pull_request` events

### Coverage report differs locally vs CI
- Ensure same Python version
- Check that all dependencies are installed
- Verify `.coveragerc` is committed to repo

### False failures
- Clear pytest cache: `rm -rf .pytest_cache`
- Delete coverage data: `rm -rf .coverage htmlcov`
- Re-run tests

## Best Practices

1. **Run tests locally** before pushing
2. **Keep coverage high** as you add features
3. **Review coverage reports** in PR comments
4. **Write tests first** (TDD) when possible
5. **Test edge cases** not just happy paths
6. **Monitor coverage trends** over time

## Additional Resources

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Pytest Coverage Documentation](https://pytest-cov.readthedocs.io/)
- [Writing Good Tests Guide](https://docs.pytest.org/en/stable/goodpractices.html)
