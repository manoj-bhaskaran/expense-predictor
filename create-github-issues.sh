#!/bin/bash
# Script to create GitHub issues from the repository review
# Generated: 2025-11-15
# Usage: ./create-github-issues.sh

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════"
echo "  Creating GitHub Issues from Repository Review"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed."
    echo ""
    echo "Please install it:"
    echo "  - macOS: brew install gh"
    echo "  - Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo "  - Windows: https://github.com/cli/cli/releases"
    echo ""
    echo "After installation, authenticate with: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI."
    echo ""
    echo "Please authenticate with: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Verify we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

echo "📁 Working directory: $(pwd)"
echo ""

# Ask for confirmation
echo "This will create 13 GitHub issues in the current repository."
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Creating issues..."
echo ""

# Counter
CREATED=0
FAILED=0

# Function to create an issue
create_issue() {
    local priority=$1
    local number=$2
    local title=$3
    local file=$4
    local labels=$5

    echo "[$priority-$number] Creating: $title"

    if gh issue create \
        --title "$title" \
        --body-file "github-issues/$file" \
        --label "$labels" > /dev/null 2>&1; then
        echo "  ✅ Created"
        ((CREATED++))
    else
        echo "  ❌ Failed"
        ((FAILED++))
    fi
    echo ""
}

# Critical Issues
echo "════════════════════════════════════════════════════════════"
echo "🔴 CRITICAL PRIORITY ISSUES"
echo "════════════════════════════════════════════════════════════"
echo ""

create_issue "CRITICAL" "01" \
    "[CRITICAL] Replace GitHub dependency with PyPI package or vendored code" \
    "CRITICAL-01-github-dependency.md" \
    "critical,dependencies,security,technical-debt"

create_issue "CRITICAL" "02" \
    "[CRITICAL] Fix coverage configuration - model_runner.py excluded from coverage" \
    "CRITICAL-02-coverage-configuration.md" \
    "critical,testing,ci-cd,configuration"

create_issue "CRITICAL" "03" \
    "[CRITICAL] Fix CI/CD coverage threshold mismatch" \
    "CRITICAL-03-cicd-coverage-threshold.md" \
    "critical,ci-cd,testing,configuration"

# High Priority Issues
echo "════════════════════════════════════════════════════════════"
echo "🟠 HIGH PRIORITY ISSUES"
echo "════════════════════════════════════════════════════════════"
echo ""

create_issue "HIGH" "01" \
    "[HIGH] Add type hints to all function signatures" \
    "HIGH-01-add-type-hints.md" \
    "enhancement,code-quality,typing,good-first-issue"

create_issue "HIGH" "02" \
    "[HIGH] Implement main() function for console entry point" \
    "HIGH-02-implement-main-function.md" \
    "bug,enhancement,packaging"

create_issue "HIGH" "03" \
    "[HIGH] Remove duplicate date range logic in helpers.py" \
    "HIGH-03-remove-code-duplication.md" \
    "refactoring,code-quality,technical-debt"

create_issue "HIGH" "04" \
    "[HIGH] Standardize error handling across codebase" \
    "HIGH-04-improve-error-handling.md" \
    "bug,code-quality,error-handling"

# Medium Priority Issues
echo "════════════════════════════════════════════════════════════"
echo "🟡 MEDIUM PRIORITY ISSUES"
echo "════════════════════════════════════════════════════════════"
echo ""

create_issue "MEDIUM" "01" \
    "[MEDIUM] Clarify python_logging_framework usage strategy" \
    "MEDIUM-01-logging-framework-clarity.md" \
    "documentation,dependencies,technical-debt"

create_issue "MEDIUM" "02" \
    "[MEDIUM] Add pytest markers to test files" \
    "MEDIUM-02-add-test-markers.md" \
    "enhancement,testing,good-first-issue"

create_issue "MEDIUM" "03" \
    "[MEDIUM] Create .env.example file and implement environment variable loading" \
    "MEDIUM-03-env-file-configuration.md" \
    "enhancement,configuration,documentation"

# Low Priority Issues
echo "════════════════════════════════════════════════════════════"
echo "🔵 LOW PRIORITY ISSUES"
echo "════════════════════════════════════════════════════════════"
echo ""

create_issue "LOW" "01" \
    "[LOW] Add .pre-commit-config.yaml file" \
    "LOW-01-pre-commit-config.md" \
    "enhancement,developer-experience,good-first-issue"

create_issue "LOW" "02" \
    "[LOW] Add configurable log levels" \
    "LOW-02-configurable-log-levels.md" \
    "enhancement,logging,good-first-issue"

create_issue "LOW" "03" \
    "[LOW] Add Python 3.12 to test matrix or remove from classifiers" \
    "LOW-03-python-312-support.md" \
    "enhancement,ci-cd,testing"

# Summary
echo "════════════════════════════════════════════════════════════"
echo "📊 SUMMARY"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ Successfully created: $CREATED issues"
if [ $FAILED -gt 0 ]; then
    echo "❌ Failed to create: $FAILED issues"
fi
echo ""
echo "View all issues: gh issue list"
echo "Or visit: https://github.com/manoj-bhaskaran/expense-predictor/issues"
echo ""
echo "✨ Done!"
