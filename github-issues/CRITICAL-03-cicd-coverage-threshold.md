# [CRITICAL] Fix CI/CD coverage threshold mismatch

## Priority
🔴 **Critical**

## Labels
`critical`, `ci-cd`, `testing`, `configuration`

## Description

There is a critical mismatch between the actual test coverage (43% per README) and the CI/CD requirement (80%), which causes all pull requests to fail the coverage check.

### Current State

```yaml
# .github/workflows/test.yml:44-45
- name: Check coverage threshold
  run: coverage report --fail-under=80
```

```markdown
# README.md:429
Current test coverage: **43%** (needs improvement to meet CI/CD requirements)
```

### Problem

Every PR will fail with:
```
FAILED: coverage report --fail-under=80
Total coverage: 43.00%
Error: Coverage is below 80%
```

This makes the CI/CD pipeline ineffective because:
1. Contributors cannot merge PRs
2. The check becomes "noise" that people ignore
3. It blocks legitimate improvements
4. Forces disabling the check or ignoring failures

## Root Causes

1. Main file (`model_runner.py`) excluded from coverage (see Issue #2)
2. Insufficient test coverage overall
3. Threshold set aspirationally rather than practically

## Proposed Solutions

### Option 1: Progressive Threshold (Recommended)
Set a realistic current threshold and gradually increase:

```yaml
# Start with current coverage
- name: Check coverage threshold
  run: coverage report --fail-under=50

# Add TODO comment to increase over time
# TODO: Increase to 60% by Q2 2024
# TODO: Increase to 70% by Q3 2024
# TODO: Increase to 80% by Q4 2024
```

### Option 2: Fix Coverage First
1. Remove `model_runner.py` from coverage omit (Issue #2)
2. Add comprehensive integration tests
3. Achieve 80% coverage
4. Then enforce the threshold

### Option 3: Differential Coverage
Only require 80% coverage for **new code** in PRs:
```yaml
- name: Check diff coverage
  run: diff-cover coverage.xml --compare-branch=origin/main --fail-under=80
```

## Recommended Approach

**Immediate** (this week):
1. Lower threshold to `50` (current realistic level)
2. Document the roadmap to 80% in README

**Short-term** (next sprint):
1. Fix Issue #2 (coverage configuration)
2. Add integration tests
3. Measure actual coverage including `model_runner.py`

**Medium-term** (next month):
1. Increase threshold to `60`
2. Add more unit tests
3. Continue improving

**Long-term** (next quarter):
1. Achieve 80% coverage
2. Enforce 80% threshold

## Acceptance Criteria

- [ ] CI/CD pipeline passes for existing code
- [ ] Coverage threshold matches actual achievable coverage
- [ ] Roadmap documented for reaching 80%
- [ ] README updated with current threshold
- [ ] Team agrees on approach

## Alternative: Make Check Advisory

If immediate fix isn't possible, make the check advisory:
```yaml
- name: Check coverage threshold
  run: coverage report --fail-under=80
  continue-on-error: true
```

But this is **not recommended** as it makes the check meaningless.

## Related Files
- `.github/workflows/test.yml`
- `.coveragerc`
- `README.md`

## Related Issues
- Issue #2 (Coverage configuration)
- Issue #4 (Improve test coverage)
