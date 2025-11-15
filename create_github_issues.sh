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
VERBOSE=false
SKIP_LABELS=false
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

    local gh_version
    gh_version=$(gh --version | head -n 1)
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

    local auth_user
    auth_user=$(gh auth status 2>&1 | grep "Logged in" | sed 's/.*as \(.*\) (.*/\1/')
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
        local remote_url
        remote_url=$(git remote get-url origin)

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
    read -r -p "Repository: " REPO

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

    local issue_count
    issue_count=$(find "$ISSUES_DIR" -name "issue_*.md" -type f | wc -l)

    if [ "$issue_count" -eq 0 ]; then
        print_error "No issue templates found in ${ISSUES_DIR}"
        print_info "Looking for files matching: issue_*.md"
        exit 1
    fi

    print_success "Found ${issue_count} issue template(s)"
}

################################################################################
# Label Management Functions
################################################################################

get_all_labels_from_templates() {
    local all_labels=""

    while IFS= read -r file; do
        local md_labels
        local priority
        md_labels=$(extract_labels_from_markdown "$file")
        priority=$(determine_priority_label "$file")

        if [ -n "$md_labels" ]; then
            all_labels="${all_labels},${md_labels}"
        fi
        if [ -n "$priority" ]; then
            all_labels="${all_labels},${priority}"
        fi
    done < <(find "$ISSUES_DIR" -name "issue_*.md" -type f)

    # Remove leading comma and get unique labels
    all_labels=$(echo "$all_labels" | sed 's/^,//' | tr ',' '\n' | sed '/^$/d' | sort -u | tr '\n' ',' | sed 's/,$//')
    echo "$all_labels"
}

check_and_create_labels() {
    print_step "Checking and creating labels..."

    # Get all labels from templates
    local needed_labels
    needed_labels=$(get_all_labels_from_templates)

    if [ -z "$needed_labels" ]; then
        print_info "No labels found in templates"
        return
    fi

    print_info "Labels needed: ${needed_labels}"
    echo ""

    # Get existing labels from repo
    print_info "Fetching existing labels from repository..."

    local existing_labels_raw=""
    local fetch_exit_code=0

    if command -v timeout &> /dev/null; then
        existing_labels_raw=$(timeout 30s gh label list --repo "$REPO" --json name --jq '.[].name' 2>&1) || fetch_exit_code=$?
    elif command -v gtimeout &> /dev/null; then
        existing_labels_raw=$(gtimeout 30s gh label list --repo "$REPO" --json name --jq '.[].name' 2>&1) || fetch_exit_code=$?
    else
        print_warning "No timeout command available, this might hang..."
        existing_labels_raw=$(gh label list --repo "$REPO" --json name --jq '.[].name' 2>&1) || fetch_exit_code=$?
    fi

    if [ $fetch_exit_code -eq 124 ]; then
        print_error "Timed out fetching labels (30s limit)"
        print_warning "Proceeding without checking existing labels..."
        existing_labels_raw=""
    elif [ $fetch_exit_code -ne 0 ]; then
        print_warning "Could not fetch existing labels"
        if [ "$VERBOSE" = true ]; then
            print_info "Error output: ${existing_labels_raw}"
        fi
        print_info "Will attempt to create all labels (may get 'already exists' errors)..."
        existing_labels_raw=""
    else
        print_success "Successfully fetched existing labels"
    fi

    local created_count=0
    local exists_count=0

    IFS=',' read -ra LABELS <<< "$needed_labels"
    local total_labels=${#LABELS[@]}
    local current=0

    for label in "${LABELS[@]}"; do
        ((current++))
        # Trim whitespace
        label=$(echo "$label" | xargs)
        print_info "Processing label: ${label}"

        # Skip empty
        if [ -z "$label" ]; then
            continue
        fi

        # Check if label exists in existing_labels_raw
        if [ -n "$existing_labels_raw" ] && printf '%s\n' "$existing_labels_raw" | grep -Fxq -- "$label"; then
            print_info "  [$current/$total_labels] ✓ Label exists: ${label}"
            ((exists_count++))
        else
            local color
            color=$(get_label_color "$label")
            print_info "  [$current/$total_labels] + Creating label: ${label} (color: #${color})"

            local create_output=""
            local create_exit_code=0

            if command -v timeout &> /dev/null; then
                create_output=$(timeout 15s gh label create "$label" --color "$color" --repo "$REPO" 2>&1) || create_exit_code=$?
            elif command -v gtimeout &> /dev/null; then
                create_output=$(gtimeout 15s gh label create "$label" --color "$color" --repo "$REPO" 2>&1) || create_exit_code=$?
            else
                create_output=$(gh label create "$label" --color "$color" --repo "$REPO" 2>&1) || create_exit_code=$?
            fi

            if [ $create_exit_code -eq 0 ]; then
                print_success "    Created: ${label}"
                ((created_count++))
            elif [ $create_exit_code -eq 124 ]; then
                print_error "    Timed out creating label: ${label}"
                ((exists_count++))
            else
                if [ "$VERBOSE" = true ]; then
                    print_warning "    Could not create label: ${label}"
                    print_info "    Error: ${create_output}"
                else
                    print_warning "    Could not create label: ${label} (may already exist)"
                fi
                ((exists_count++))
            fi
        fi
    done

    print_success "Label check complete: ${exists_count} existing, ${created_count} created"
    echo ""
}

get_label_color() {
    local label=$1

    case "$label" in
        # Priority labels
        "priority: critical"|"critical")
            echo "d73a4a"  # Red
            ;;
        "priority: high"|"high")
            echo "ff6b6b"  # Light red
            ;;
        "priority: medium"|"medium")
            echo "fbca04"  # Yellow
            ;;
        "priority: low"|"low")
            echo "0e8a16"  # Green
            ;;

        # Type labels
        "bug")
            echo "d73a4a"  # Red
            ;;
        "enhancement"|"feature")
            echo "a2eeef"  # Light blue
            ;;
        "documentation"|"docs")
            echo "0075ca"  # Blue
            ;;

        # Category labels
        "dependencies")
            echo "0366d6"  # Dark blue
            ;;
        "security")
            echo "ee0701"  # Bright red
            ;;
        "refactoring"|"code-quality")
            echo "d4c5f9"  # Purple
            ;;
        "testing"|"tests")
            echo "c5def5"  # Light blue
            ;;
        "validation")
            echo "1d76db"  # Blue
            ;;
        "configuration")
            echo "5319e7"  # Purple
            ;;
        "maintenance")
            echo "fbca04"  # Yellow
            ;;
        "user-experience"|"ux")
            echo "c2e0c6"  # Light green
            ;;
        "pandas")
            echo "150458"  # Dark purple
            ;;
        "deprecation")
            echo "fef2c0"  # Light yellow
            ;;
        "python-3.12"|"python")
            echo "3572a5"  # Python blue
            ;;

        # Status/meta labels
        "good first issue")
            echo "7057ff"  # Purple
            ;;
        "help wanted")
            echo "008672"  # Teal
            ;;
        "wontfix")
            echo "ffffff"  # White
            ;;
        "duplicate")
            echo "cfd3d7"  # Gray
            ;;

        # Default for any other label
        *)
            echo "ededed"  # Light gray
            ;;
    esac
}

################################################################################
# Issue Creation Functions
################################################################################

extract_title_from_markdown() {
    local file=$1
    # Extract first heading (# Title)
    local title
    title=$(grep -m 1 "^# " "$file" | sed 's/^# //')
    echo "$title"
}

extract_labels_from_markdown() {
    local file=$1
    local labels=""

    if grep -q "^## Labels" "$file"; then
        labels=$(sed -n '/^## Labels/,/^##/{/^- /p}' "$file" | sed 's/^- //' | tr '\n' ',' | sed 's/,$//')
    elif grep -q "^Labels:" "$file"; then
        labels=$(grep "^Labels:" "$file" | sed 's/^Labels: *//' | tr '\n' ',' | sed 's/,$//')
    fi

    echo "$labels"
}

determine_priority_label() {
    local file=$1

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

build_label_args() {
    local all_labels="$1"
    local -a args=()

    IFS=',' read -ra LABELS <<< "$all_labels"
    for label in "${LABELS[@]}"; do
        label=$(echo "$label" | xargs)
        [ -z "$label" ] && continue
        args+=("--label" "$label")
    done

    printf '%s\n' "${args[@]}"
}

create_issue() {
    local file=$1
    local filename
    filename=$(basename "$file")

    print_separator
    print_info "Processing: ${BOLD}${filename}${NC}"

    local title
    title=$(extract_title_from_markdown "$file")
    if [ -z "$title" ]; then
        print_warning "Could not extract title from ${filename}, skipping"
        ((SKIPPED_COUNT++))
        return
    fi
    print_info "Title: ${title}"

    local md_labels
    local priority_label
    local all_labels=""

    md_labels=$(extract_labels_from_markdown "$file")
    priority_label=$(determine_priority_label "$file")

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

    local existing=""
    # Use a robust search that tolerates quotes in title
    if ! existing=$(gh issue list \
        --repo "$REPO" \
        --search "$title in:title" \
        --json number,title \
        --jq '.[] | select(.title == "'"$title"'") | .number' 2>/dev/null); then
        print_warning "Could not check for existing issues (gh issue list failed)"
        existing=""
    fi

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

    print_info "Creating issue..."

    # Build label args array
    local -a label_args=()
    if [ -n "$all_labels" ]; then
        # shellcheck disable=SC2207
        label_args=($(build_label_args "$all_labels"))
    fi

    if [ "$VERBOSE" = true ]; then
        # This is just for display; not perfectly quoted, but indicative
        local cmd_preview="gh issue create --repo \"$REPO\" --title \"$title\" --body-file \"$file\""
        if [ ${#label_args[@]} -gt 0 ]; then
            cmd_preview+=" ${label_args[*]}"
        fi
        print_info "Command: ${cmd_preview}"
    fi

    local temp_output
    temp_output=$(mktemp)
    local exit_code=0

    if command -v timeout &> /dev/null; then
        if [ ${#label_args[@]} -gt 0 ]; then
            timeout 60s gh issue create \
                --repo "$REPO" \
                --title "$title" \
                --body-file "$file" \
                "${label_args[@]}" >"$temp_output" 2>&1 || exit_code=$?
        else
            timeout 60s gh issue create \
                --repo "$REPO" \
                --title "$title" \
                --body-file "$file" >"$temp_output" 2>&1 || exit_code=$?
        fi
    elif command -v gtimeout &> /dev/null; then
        if [ ${#label_args[@]} -gt 0 ]; then
            gtimeout 60s gh issue create \
                --repo "$REPO" \
                --title "$title" \
                --body-file "$file" \
                "${label_args[@]}" >"$temp_output" 2>&1 || exit_code=$?
        else
            gtimeout 60s gh issue create \
                --repo "$REPO" \
                --title "$title" \
                --body-file "$file" >"$temp_output" 2>&1 || exit_code=$?
        fi
    else
        print_warning "No timeout available, command might hang..."
        if [ ${#label_args[@]} -gt 0 ]; then
            gh issue create \
                --repo "$REPO" \
                --title "$title" \
                --body-file "$file" \
                "${label_args[@]}" >"$temp_output" 2>&1 || exit_code=$?
        else
            gh issue create \
                --repo "$REPO" \
                --title "$title" \
                --body-file "$file" >"$temp_output" 2>&1 || exit_code=$?
        fi
    fi

    local issue_url
    issue_url=$(cat "$temp_output")
    rm -f "$temp_output"

    if [ $exit_code -eq 124 ]; then
        print_error "Timed out creating issue (60s limit)"
        print_error "GitHub API may be unreachable. Check your network connection."
        ((FAILED_COUNT++))
    elif [ $exit_code -eq 0 ] && [ -n "$issue_url" ]; then
        print_success "Created: ${issue_url}"
        ((CREATED_COUNT++))
    elif [ $exit_code -eq 0 ]; then
        print_warning "Command succeeded but no URL returned"
        print_info "Output: ${issue_url}"
        ((CREATED_COUNT++))
    else
        print_error "Failed to create issue (exit code: $exit_code)"
        if [ -n "$issue_url" ]; then
            print_error "Output: ${issue_url}"
        fi
        ((FAILED_COUNT++))
    fi
}

################################################################################
# Argument Parsing & Help
################################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --skip-labels)
                SKIP_LABELS=true
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
  github_issues/ directory. The script will automatically create any
  missing labels before creating issues.

${BOLD}Options:${NC}
  --dry-run         Show what would be created without actually creating issues
  --verbose, -v     Show verbose output including gh commands being executed
  --skip-labels     Skip automatic label creation (useful if gh label commands hang)
  --repo OWNER/REPO Specify the repository (default: auto-detect from git)
  -h, --help        Show this help message

${BOLD}Examples:${NC}
  # Auto-detect repository and create issues
  ./create_github_issues.sh

  # Dry run to preview what would be created
  ./create_github_issues.sh --dry-run

  # Verbose mode to see all commands
  ./create_github_issues.sh --verbose

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

################################################################################
# Main
################################################################################

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
        read -r -p "Continue? [y/N] " -n 1 REPLY
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Cancelled by user"
            exit 0
        fi
    else
        print_info "Running in dry-run mode for repository: ${REPO}"
    fi

    # Check and create labels (skip in dry-run mode or if --skip-labels flag set)
    if [ "$DRY_RUN" = false ] && [ "$SKIP_LABELS" = false ]; then
        check_and_create_labels
    else
        if [ "$SKIP_LABELS" = true ]; then
            print_warning "Skipping label creation (--skip-labels flag set)"
        else
            print_info "Skipping label creation in dry-run mode"
        fi
        echo ""
    fi

    # Process each issue file
    print_step "Creating issues..."
    echo ""

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
