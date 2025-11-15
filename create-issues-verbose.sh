#!/bin/bash
set -e

echo "Creating GitHub issues..."
echo ""

# CRITICAL
echo "Creating CRITICAL-01..."
gh issue create --title "[CRITICAL] Replace GitHub dependency with PyPI package or vendored code" \
  --body-file "github-issues/CRITICAL-01-github-dependency.md" \
  --label "critical,dependencies,security,technical-debt" || echo "Failed: CRITICAL-01"

echo "Creating CRITICAL-02..."
gh issue create --title "[CRITICAL] Fix coverage configuration - model_runner.py excluded from coverage" \
  --body-file "github-issues/CRITICAL-02-coverage-configuration.md" \
  --label "critical,testing,ci-cd,configuration" || echo "Failed: CRITICAL-02"

echo "Creating CRITICAL-03..."
gh issue create --title "[CRITICAL] Fix CI/CD coverage threshold mismatch" \
  --body-file "github-issues/CRITICAL-03-cicd-coverage-threshold.md" \
  --label "critical,ci-cd,testing,configuration" || echo "Failed: CRITICAL-03"

# HIGH
echo "Creating HIGH-01..."
gh issue create --title "[HIGH] Add type hints to all function signatures" \
  --body-file "github-issues/HIGH-01-add-type-hints.md" \
  --label "enhancement,code-quality,typing,good-first-issue" || echo "Failed: HIGH-01"

echo "Creating HIGH-02..."
gh issue create --title "[HIGH] Implement main() function for console entry point" \
  --body-file "github-issues/HIGH-02-implement-main-function.md" \
  --label "bug,enhancement,packaging" || echo "Failed: HIGH-02"

echo "Creating HIGH-03..."
gh issue create --title "[HIGH] Remove duplicate date range logic in helpers.py" \
  --body-file "github-issues/HIGH-03-remove-code-duplication.md" \
  --label "refactoring,code-quality,technical-debt" || echo "Failed: HIGH-03"

echo "Creating HIGH-04..."
gh issue create --title "[HIGH] Standardize error handling across codebase" \
  --body-file "github-issues/HIGH-04-improve-error-handling.md" \
  --label "bug,code-quality,error-handling" || echo "Failed: HIGH-04"

# MEDIUM
echo "Creating MEDIUM-01..."
gh issue create --title "[MEDIUM] Clarify python_logging_framework usage strategy" \
  --body-file "github-issues/MEDIUM-01-logging-framework-clarity.md" \
  --label "documentation,dependencies,technical-debt" || echo "Failed: MEDIUM-01"

echo "Creating MEDIUM-02..."
gh issue create --title "[MEDIUM] Add pytest markers to test files" \
  --body-file "github-issues/MEDIUM-02-add-test-markers.md" \
  --label "enhancement,testing,good-first-issue" || echo "Failed: MEDIUM-02"

echo "Creating MEDIUM-03..."
gh issue create --title "[MEDIUM] Create .env.example file and implement environment variable loading" \
  --body-file "github-issues/MEDIUM-03-env-file-configuration.md" \
  --label "enhancement,configuration,documentation" || echo "Failed: MEDIUM-03"

# LOW
echo "Creating LOW-01..."
gh issue create --title "[LOW] Add .pre-commit-config.yaml file" \
  --body-file "github-issues/LOW-01-pre-commit-config.md" \
  --label "enhancement,developer-experience,good-first-issue" || echo "Failed: LOW-01"

echo "Creating LOW-02..."
gh issue create --title "[LOW] Add configurable log levels" \
  --body-file "github-issues/LOW-02-configurable-log-levels.md" \
  --label "enhancement,logging,good-first-issue" || echo "Failed: LOW-02"

echo "Creating LOW-03..."
gh issue create --title "[LOW] Add Python 3.12 to test matrix or remove from classifiers" \
  --body-file "github-issues/LOW-03-python-312-support.md" \
  --label "enhancement,ci-cd,testing" || echo "Failed: LOW-03"

echo ""
echo "Done! Check issues at: https://github.com/manoj-bhaskaran/expense-predictor/issues"
