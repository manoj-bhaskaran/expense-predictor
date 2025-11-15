#!/bin/bash

################################################################################
# Script: create_github_issues.sh
# Description: Automatically create GitHub issues from markdown templates
# Usage: ./create_github_issues.sh [--dry-run] [--repo OWNER/REPO]
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISSUES_DIR="${SCRIPT_DIR}/github_issues"

# Configuration
DRY_RUN=false
REPO=""
CREATED_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BOLD}${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  GitHub Issue Creator${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════════${NC}\n"
}

print_info() {
    echo -e "${BLUE}ℹ${NC}  $1"
}

print_success() {
    echo -e "${GREEN}✓${NC}  $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_error() {
    echo -e "${RED}✗${NC}  $1"
}

print_step() {
    echo -e "\n${BOLD}${MAGENTA}▶${NC} ${BOLD}$1${NC}"
}

print_separator() {
    echo -e "${CYAN}───────────────────────────────────────────────────────────────────${NC}"
}

################################################################################
# Validation Functions
################################################################################

check_gh_cli() {
    print_step "Checking GitHub CLI installation..."

    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        echo ""
        echo "Please install it from: https://cli.github.com/"
        echo ""
        echo "Installation methods:"
        echo "  • macOS:   brew install gh"
        echo "  • Ubuntu:  sudo apt install gh"
        echo "  • Windows: winget install GitHub.cli"
        echo ""
        exit 1
    fi

    local gh_version=$(gh --version | head -n 1)
    print_success "GitHub CLI found: ${gh_version}"
}

check_gh_auth() {
    print_step "Checking GitHub authentication..."

    if ! gh auth status &> /dev/null; then
        print_error "Not authenticated with GitHub"
        echo ""
        echo "Please authenticate first:"
        echo "  gh auth login"
        echo ""
        exit 1
    fi

    local auth_user=$(gh auth status 2>&1 | grep "Logged in" | sed 's/.*as \(.*\) (.*/\1/')
    print_success "Authenticated as: ${auth_user}"
}

detect_repo() {
    print_step "Detecting repository..."

    if [ -n "$REPO" ]; then
        print_info "Using repository from command line: ${REPO}"
        return
    fi

    # Try to detect from git remote
    if git remote get-url origin &> /dev/null; then
        local remote_url=$(git remote get-url origin)

        # Extract owner/repo from various Git URL formats
        if [[ $remote_url =~ github\.com[:/]([^/]+)/([^/\.]+) ]]; then
            REPO="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
            print_success "Detected repository: ${REPO}"
        else
            print_warning "Could not parse repository from remote URL: ${remote_url}"
            ask_for_repo
        fi
    else
        print_warning "No git remote found"
        ask_for_repo
    fi
}

ask_for_repo() {
    echo ""
    echo -e "${YELLOW}Please enter the repository in format OWNER/REPO:${NC}"
    read -p "Repository: " REPO

    if [ -z "$REPO" ]; then
        print_error "Repository is required"
        exit 1
    fi

    print_info "Using repository: ${REPO}"
}

check_issues_directory() {
    print_step "Checking for issue templates..."

    if [ ! -d "$ISSUES_DIR" ]; then
        print_error "Issues directory not found: ${ISSUES_DIR}"
        exit 1
    fi

    local issue_count=$(find "$ISSUES_DIR" -name "issue_*.md" -type f | wc -l)

    if [ "$issue_count" -eq 0 ]; then
        print_error "No issue templates found in ${ISSUES_DIR}"
        print_info "Looking for files matching: issue_*.md"
        exit 1
    fi

    print_success "Found ${issue_count} issue template(s)"
}

################################################################################
# Issue Creation Functions
################################################################################

extract_title_from_markdown() {
    local file=$1
    # Extract first heading (# Title)
    local title=$(grep -m 1 "^# " "$file" | sed 's/^# //')
    echo "$title"
}

extract_labels_from_markdown() {
    local file=$1
    # Look for a "Labels" or "## Labels" section
    local labels=""

    # Try to find labels section
    if grep -q "^## Labels" "$file"; then
        # Extract bullet points after ## Labels
        labels=$(sed -n '/^## Labels/,/^##/{/^- /p}' "$file" | sed 's/^- //' | tr '\n' ',' | sed 's/,$//')
    elif grep -q "^Labels:" "$file"; then
        # Extract from "Labels: " line
        labels=$(grep "^Labels:" "$file" | sed 's/^Labels: *//' | tr '\n' ',' | sed 's/,$//')
    fi

    echo "$labels"
}

determine_priority_label() {
    local file=$1
    local filename=$(basename "$file")

    # Determine priority from content
    if grep -qi "severity.*critical" "$file" || grep -qi "\*\*severity:\*\* critical" "$file"; then
        echo "priority: critical"
    elif grep -qi "severity.*high" "$file" || grep -qi "\*\*severity:\*\* high" "$file"; then
        echo "priority: high"
    elif grep -qi "severity.*medium" "$file" || grep -qi "\*\*severity:\*\* medium" "$file"; then
        echo "priority: medium"
    elif grep -qi "severity.*low" "$file" || grep -qi "\*\*severity:\*\* low" "$file"; then
        echo "priority: low"
    else
        echo ""
    fi
}

create_issue() {
    local file=$1
    local filename=$(basename "$file")

    print_separator
    print_info "Processing: ${BOLD}${filename}${NC}"

    # Extract title
    local title=$(extract_title_from_markdown "$file")
    if [ -z "$title" ]; then
        print_warning "Could not extract title from ${filename}, skipping"
        ((SKIPPED_COUNT++))
        return
    fi
    print_info "Title: ${title}"

    # Extract labels from markdown
    local md_labels=$(extract_labels_from_markdown "$file")

    # Determine priority label
    local priority_label=$(determine_priority_label "$file")

    # Combine labels
    local all_labels=""
    if [ -n "$md_labels" ]; then
        all_labels="$md_labels"
    fi
    if [ -n "$priority_label" ]; then
        if [ -n "$all_labels" ]; then
            all_labels="${all_labels},${priority_label}"
        else
            all_labels="$priority_label"
        fi
    fi

    if [ -n "$all_labels" ]; then
        print_info "Labels: ${all_labels}"
    fi

    # Check if issue already exists
    print_info "Checking for existing issues with this title..."
    local existing=$(gh issue list --repo "$REPO" --search "in:title \"$title\"" --json number,title --jq '.[] | select(.title == "'"$title"'") | .number')

    if [ -n "$existing" ]; then
        print_warning "Issue already exists: #${existing}"
        print_warning "Skipping to avoid duplicates"
        ((SKIPPED_COUNT++))
        return
    fi

    if [ "$DRY_RUN" = true ]; then
        print_warning "[DRY RUN] Would create issue: ${title}"
        if [ -n "$all_labels" ]; then
            print_info "[DRY RUN] With labels: ${all_labels}"
        fi
        ((CREATED_COUNT++))
        return
    fi

    # Create the issue
    print_info "Creating issue..."

    local gh_command="gh issue create --repo \"$REPO\" --title \"$title\" --body-file \"$file\""

    if [ -n "$all_labels" ]; then
        gh_command="${gh_command} --label \"$all_labels\""
    fi

    # Execute the command
    local issue_url=""
    if [ -n "$all_labels" ]; then
        issue_url=$(gh issue create --repo "$REPO" --title "$title" --body-file "$file" --label "$all_labels" 2>&1)
    else
        issue_url=$(gh issue create --repo "$REPO" --title "$title" --body-file "$file" 2>&1)
    fi

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_success "Created: ${issue_url}"
        ((CREATED_COUNT++))
    else
        print_error "Failed to create issue"
        print_error "Error: ${issue_url}"
        ((FAILED_COUNT++))
    fi
}

################################################################################
# Main Execution
################################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --repo)
                REPO="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << EOF
${BOLD}Usage:${NC} ./create_github_issues.sh [OPTIONS]

${BOLD}Description:${NC}
  Automatically creates GitHub issues from markdown templates in the
  github_issues/ directory.

${BOLD}Options:${NC}
  --dry-run         Show what would be created without actually creating issues
  --repo OWNER/REPO Specify the repository (default: auto-detect from git)
  -h, --help        Show this help message

${BOLD}Examples:${NC}
  # Auto-detect repository and create issues
  ./create_github_issues.sh

  # Dry run to preview what would be created
  ./create_github_issues.sh --dry-run

  # Specify repository explicitly
  ./create_github_issues.sh --repo manoj-bhaskaran/expense-predictor

${BOLD}Requirements:${NC}
  • GitHub CLI (gh) must be installed
  • Must be authenticated with: gh auth login
  • Issue templates must exist in github_issues/ directory

${BOLD}Issue Templates:${NC}
  Templates should be in markdown format with:
  • First line as heading (# Title) for the issue title
  • Optional "## Labels" section with bullet points for labels
  • Full body content will be used as issue description

EOF
}

main() {
    print_header

    # Parse command line arguments
    parse_arguments "$@"

    if [ "$DRY_RUN" = true ]; then
        print_warning "DRY RUN MODE - No issues will be created"
    fi

    # Validation steps
    check_gh_cli
    check_gh_auth
    detect_repo
    check_issues_directory

    # Confirm before proceeding
    print_separator
    echo ""
    if [ "$DRY_RUN" = false ]; then
        echo -e "${YELLOW}${BOLD}Ready to create issues in repository: ${REPO}${NC}"
        read -p "Continue? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Cancelled by user"
            exit 0
        fi
    else
        print_info "Running in dry-run mode for repository: ${REPO}"
    fi

    # Process each issue file
    print_step "Creating issues..."
    echo ""

    # Sort files to ensure consistent order
    # Only process issue templates (issue_*.md), exclude README and other docs
    while IFS= read -r file; do
        create_issue "$file"
    done < <(find "$ISSUES_DIR" -name "issue_*.md" -type f | sort)

    # Final summary
    print_separator
    print_step "Summary"
    echo ""

    if [ "$DRY_RUN" = true ]; then
        print_info "DRY RUN - No actual issues were created"
    fi

    print_info "Total processed: $((CREATED_COUNT + FAILED_COUNT + SKIPPED_COUNT))"

    if [ $CREATED_COUNT -gt 0 ]; then
        if [ "$DRY_RUN" = true ]; then
            print_success "Would create: ${CREATED_COUNT}"
        else
            print_success "Created: ${CREATED_COUNT}"
        fi
    fi

    if [ $SKIPPED_COUNT -gt 0 ]; then
        print_warning "Skipped: ${SKIPPED_COUNT} (duplicates or invalid)"
    fi

    if [ $FAILED_COUNT -gt 0 ]; then
        print_error "Failed: ${FAILED_COUNT}"
    fi

    echo ""

    if [ "$DRY_RUN" = false ] && [ $CREATED_COUNT -gt 0 ]; then
        print_success "All issues created successfully!"
        echo ""
        echo "View issues at: https://github.com/${REPO}/issues"
    elif [ "$DRY_RUN" = true ]; then
        echo ""
        echo "To create issues for real, run without --dry-run:"
        echo "  ./create_github_issues.sh"
    fi

    echo ""
    print_separator
}

# Run main function
main "$@"
