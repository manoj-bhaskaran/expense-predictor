# GitHub Issues - Repository Review

This directory contains GitHub issue templates generated from the comprehensive repository review conducted on 2025-11-15.

## Issue Summary

### 🔴 Critical Priority (3 issues)
1. **CRITICAL-01**: Replace GitHub dependency with PyPI package or vendored code
2. **CRITICAL-02**: Fix coverage configuration - model_runner.py excluded from coverage
3. **CRITICAL-03**: Fix CI/CD coverage threshold mismatch

### 🟠 High Priority (4 issues)
1. **HIGH-01**: Add type hints to all function signatures
2. **HIGH-02**: Implement main() function for console entry point
3. **HIGH-03**: Remove duplicate date range logic in helpers.py
4. **HIGH-04**: Standardize error handling across codebase

### 🟡 Medium Priority (3 issues)
1. **MEDIUM-01**: Clarify python_logging_framework usage strategy
2. **MEDIUM-02**: Add pytest markers to test files
3. **MEDIUM-03**: Create .env.example file and implement environment variable loading

### 🔵 Low Priority (3 issues)
1. **LOW-01**: Add .pre-commit-config.yaml file
2. **LOW-02**: Add configurable log levels
3. **LOW-03**: Add Python 3.12 to test matrix or remove from classifiers

## Creating Issues in GitHub

Since the `gh` CLI is not available in this environment, you can create these issues using one of the following methods:

### Method 1: Manual Creation via GitHub Web Interface
1. Go to https://github.com/manoj-bhaskaran/expense-predictor/issues
2. Click "New Issue"
3. Copy the content from each `.md` file
4. Set the title from the first line (without the `#`)
5. Add the labels mentioned in each issue
6. Create the issue

### Method 2: Using gh CLI (from your local machine)
```bash
cd /path/to/expense-predictor
gh issue create --title "Title from file" --body-file github-issues/CRITICAL-01-github-dependency.md --label "critical,dependencies,security,technical-debt"
```

### Method 3: Bulk Creation Script
Create a script to batch-create all issues:

```bash
#!/bin/bash
# create-issues.sh

# Critical issues
gh issue create --title "[CRITICAL] Replace GitHub dependency with PyPI package or vendored code" \
  --body-file github-issues/CRITICAL-01-github-dependency.md \
  --label "critical,dependencies,security,technical-debt"

gh issue create --title "[CRITICAL] Fix coverage configuration - model_runner.py excluded from coverage" \
  --body-file github-issues/CRITICAL-02-coverage-configuration.md \
  --label "critical,testing,ci-cd,configuration"

gh issue create --title "[CRITICAL] Fix CI/CD coverage threshold mismatch" \
  --body-file github-issues/CRITICAL-03-cicd-coverage-threshold.md \
  --label "critical,ci-cd,testing,configuration"

# High priority issues
gh issue create --title "[HIGH] Add type hints to all function signatures" \
  --body-file github-issues/HIGH-01-add-type-hints.md \
  --label "enhancement,code-quality,typing,good-first-issue"

gh issue create --title "[HIGH] Implement main() function for console entry point" \
  --body-file github-issues/HIGH-02-implement-main-function.md \
  --label "bug,enhancement,packaging"

gh issue create --title "[HIGH] Remove duplicate date range logic in helpers.py" \
  --body-file github-issues/HIGH-03-remove-code-duplication.md \
  --label "refactoring,code-quality,technical-debt"

gh issue create --title "[HIGH] Standardize error handling across codebase" \
  --body-file github-issues/HIGH-04-improve-error-handling.md \
  --label "bug,code-quality,error-handling"

# Medium priority issues
gh issue create --title "[MEDIUM] Clarify python_logging_framework usage strategy" \
  --body-file github-issues/MEDIUM-01-logging-framework-clarity.md \
  --label "documentation,dependencies,technical-debt"

gh issue create --title "[MEDIUM] Add pytest markers to test files" \
  --body-file github-issues/MEDIUM-02-add-test-markers.md \
  --label "enhancement,testing,good-first-issue"

gh issue create --title "[MEDIUM] Create .env.example file and implement environment variable loading" \
  --body-file github-issues/MEDIUM-03-env-file-configuration.md \
  --label "enhancement,configuration,documentation"

# Low priority issues
gh issue create --title "[LOW] Add .pre-commit-config.yaml file" \
  --body-file github-issues/LOW-01-pre-commit-config.md \
  --label "enhancement,developer-experience,good-first-issue"

gh issue create --title "[LOW] Add configurable log levels" \
  --body-file github-issues/LOW-02-configurable-log-levels.md \
  --label "enhancement,logging,good-first-issue"

gh issue create --title "[LOW] Add Python 3.12 to test matrix or remove from classifiers" \
  --body-file github-issues/LOW-03-python-312-support.md \
  --label "enhancement,ci-cd,testing"

echo "All issues created successfully!"
```

Make it executable and run:
```bash
chmod +x create-issues.sh
./create-issues.sh
```

## Recommended Order of Implementation

Based on dependencies and impact, here's the recommended order:

1. **CRITICAL-01** (GitHub dependency) - Blocks reliable deployment
2. **CRITICAL-02** (Coverage config) - Needed before fixing coverage
3. **CRITICAL-03** (CI/CD threshold) - Unblocks PR merges
4. **HIGH-02** (Main function) - Enables proper packaging
5. **HIGH-04** (Error handling) - Improves stability
6. **HIGH-03** (Code duplication) - Improves maintainability
7. **HIGH-01** (Type hints) - Can be done incrementally
8. **MEDIUM-01** (Logging framework) - Related to CRITICAL-01
9. **MEDIUM-03** (.env support) - Nice feature addition
10. **MEDIUM-02** (Test markers) - Improves test organization
11. **LOW-01** (Pre-commit) - Developer experience
12. **LOW-02** (Log levels) - Nice to have
13. **LOW-03** (Python 3.12) - Future compatibility

## Labels to Create in GitHub

If these labels don't exist in your repository, create them first:

### Priority Labels
- `critical` (red) - Requires immediate attention
- `high-priority` (orange) - Important but not blocking
- `medium-priority` (yellow) - Should be done soon
- `low-priority` (blue) - Nice to have

### Category Labels
- `bug` (red)
- `enhancement` (blue)
- `documentation` (blue)
- `testing` (green)
- `ci-cd` (purple)
- `dependencies` (orange)
- `security` (red)
- `code-quality` (yellow)
- `technical-debt` (brown)
- `configuration` (gray)
- `refactoring` (yellow)
- `good-first-issue` (green)

## Questions?

If you have questions about any of these issues:
1. Read the detailed description in the corresponding .md file
2. Check the "Related Issues" section for dependencies
3. Review the "Acceptance Criteria" for clarity on completion
4. Refer back to the full repository review document

## Next Steps

After creating the issues:
1. Add them to a GitHub Project board for tracking
2. Assign priorities using labels
3. Create milestones for grouping (e.g., "Q1 2024 Code Quality")
4. Start with Critical issues first
5. Consider creating PRs that address multiple related issues together
