#!/bin/bash

################################################################################
# Script: test_issue_parsing.sh
# Description: Test script to show how issues would be parsed and created
#              (doesn't require gh CLI - just demonstrates the parsing)
################################################################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISSUES_DIR="${SCRIPT_DIR}/github_issues"

echo -e "${BOLD}${CYAN}Issue Parsing Test${NC}\n"

extract_title() {
    local file=$1
    grep -m 1 "^# " "$file" | sed 's/^# //'
}

extract_labels() {
    local file=$1
    if grep -q "^## Labels" "$file"; then
        sed -n '/^## Labels/,/^##/{/^- /p}' "$file" | sed 's/^- //' | tr '\n' ',' | sed 's/,$//'
    fi
}

determine_priority() {
    local file=$1
    if grep -qi "\*\*severity:\*\* critical" "$file"; then
        echo "priority: critical"
    elif grep -qi "\*\*severity:\*\* high" "$file"; then
        echo "priority: high"
    elif grep -qi "\*\*severity:\*\* medium" "$file"; then
        echo "priority: medium"
    else
        echo "priority: low"
    fi
}

count=0
# Only process issue templates (issue_*.md), exclude README and other docs
for file in $(find "$ISSUES_DIR" -name "issue_*.md" -type f | sort); do
    ((count++))
    filename=$(basename "$file")
    title=$(extract_title "$file")
    labels=$(extract_labels "$file")
    priority=$(determine_priority "$file")

    # Combine labels
    all_labels="$labels"
    if [ -n "$labels" ] && [ -n "$priority" ]; then
        all_labels="${labels},${priority}"
    elif [ -n "$priority" ]; then
        all_labels="$priority"
    fi

    echo -e "${BOLD}${BLUE}[$count]${NC} ${BOLD}$filename${NC}"
    echo -e "    ${GREEN}Title:${NC} $title"
    if [ -n "$all_labels" ]; then
        echo -e "    ${YELLOW}Labels:${NC} $all_labels"
    fi
    echo ""
done

echo -e "${BOLD}Total issues found:${NC} $count"
echo ""
echo -e "${CYAN}Command that would be executed for each issue:${NC}"
echo -e "${YELLOW}gh issue create --repo <REPO> --title \"<TITLE>\" --body-file <FILE> --label \"<LABELS>\"${NC}"
