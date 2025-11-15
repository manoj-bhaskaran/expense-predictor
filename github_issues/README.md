# GitHub Issues Templates

This directory contains pre-written GitHub issue templates ready to be published to the repository.

## 📋 Available Issues

| File | Severity | Category | Description |
|------|----------|----------|-------------|
| `issue_01_openpyxl_missing.md` | 🔴 Critical | Dependencies | Missing openpyxl in production dependencies |
| `issue_02_xlrd_xlsx_incompatibility.md` | 🔴 Critical | Dependencies | xlrd 2.0.1 cannot read .xlsx files |
| `issue_03_minimum_data_validation.md` | 🔴 Critical | Validation | No minimum data validation before training |
| `issue_04_version_mismatch_line_profiler.md` | 🟡 High | Dependencies | Version mismatch between setup.py and requirements-dev.txt |
| `issue_05_dry_violation_constants.md` | 🟡 High | Code Quality | DRY violation with duplicate constants |
| `issue_06_deprecated_pandas_inplace.md` | 🟡 High | Deprecation | Deprecated pandas inplace=True usage |
| `issue_07_config_type_validation.md` | 🟡 High | Validation | Missing type validation for config.yaml |

## 🚀 Quick Start

### Option 1: Automated Creation (Recommended)

Use the provided script to create all issues automatically:

```bash
# Preview what will be created (dry run)
./create_github_issues.sh --dry-run

# Create all issues
./create_github_issues.sh

# Create issues for a specific repository
./create_github_issues.sh --repo owner/repository
```

### Option 2: Manual Creation

1. Go to https://github.com/manoj-bhaskaran/expense-predictor/issues
2. Click "New Issue"
3. Copy the content from the desired `.md` file
4. The first line (`# Title`) becomes the issue title
5. Copy everything else as the issue body
6. Add labels as listed in the "Labels" section of each file
7. Click "Submit new issue"

### Option 3: GitHub CLI (Individual Issues)

Create issues one at a time using gh CLI:

```bash
# Example: Create the openpyxl missing issue
gh issue create \
  --title "Missing openpyxl in Production Dependencies" \
  --body-file github_issues/issue_01_openpyxl_missing.md \
  --label bug,dependencies,critical
```

## 🛠️ Script Usage

The `create_github_issues.sh` script provides a fully automated way to create all issues.

### Prerequisites

1. **Install GitHub CLI:**
   ```bash
   # macOS
   brew install gh

   # Ubuntu/Debian
   sudo apt install gh

   # Windows
   winget install GitHub.cli
   ```

2. **Authenticate:**
   ```bash
   gh auth login
   ```

### Script Features

- ✅ **Auto-detection** of repository from git remote
- ✅ **Duplicate checking** - won't create if issue title already exists
- ✅ **Dry-run mode** - preview before creating
- ✅ **Verbose output** - see exactly what's happening
- ✅ **Color-coded status** - easy to read progress
- ✅ **Error handling** - graceful failure with helpful messages
- ✅ **Label extraction** - automatically applies labels from templates

### Command Line Options

```
Usage: ./create_github_issues.sh [OPTIONS]

Options:
  --dry-run         Show what would be created without actually creating issues
  --repo OWNER/REPO Specify the repository (default: auto-detect from git)
  -h, --help        Show help message
```

### Examples

**Preview before creating:**
```bash
./create_github_issues.sh --dry-run
```

**Create all issues:**
```bash
./create_github_issues.sh
```

**Specify repository explicitly:**
```bash
./create_github_issues.sh --repo manoj-bhaskaran/expense-predictor
```

**Get help:**
```bash
./create_github_issues.sh --help
```

## 📝 Issue Template Format

Each template follows this structure:

```markdown
# Issue Title

## Summary
Brief description...

## Impact
- **Severity:** Critical/High/Medium/Low
- Impact details...

## Current Behavior
What happens now...

## Expected Behavior
What should happen...

## Technical Details
Code references, file locations...

## Proposed Solution
How to fix...

## Labels
- label1
- label2
```

## 🎯 Recommended Creation Order

For maximum impact, create issues in this order:

1. **Critical Issues (Week 1):**
   - issue_01 (openpyxl missing)
   - issue_02 (xlrd incompatibility)
   - issue_03 (minimum data validation)

2. **High Priority (Week 2-3):**
   - issue_04 (version mismatch)
   - issue_05 (DRY violations)
   - issue_06 (deprecated pandas)
   - issue_07 (config validation)

## 🔍 Verification

After creating issues, verify:

```bash
# List all open issues
gh issue list

# View a specific issue
gh issue view <issue-number>

# Check labels
gh issue list --label "critical"
```

## 📊 Expected Results

When all issues are created, you should see:
- 3 issues with `critical` priority
- 4 issues with `high` priority
- Issues properly labeled (bug, dependencies, etc.)
- All issues assigned to the correct repository

## 🐛 Troubleshooting

### Script fails with "gh: command not found"
**Solution:** Install GitHub CLI (see Prerequisites)

### Script fails with "authentication required"
**Solution:** Run `gh auth login`

### "Issue already exists" warning
**Solution:** This is normal - script detects duplicates. Check existing issues with `gh issue list`

### Permission denied when running script
**Solution:** Make script executable: `chmod +x create_github_issues.sh`

### Can't detect repository
**Solution:** Use `--repo` flag: `./create_github_issues.sh --repo owner/repo`

## 📚 Additional Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Issues Guide](https://docs.github.com/en/issues)
- [Main Review Document](../ISSUES_FOUND.md)
- [Review Summary](../REVIEW_SUMMARY.md)

## 💡 Tips

1. **Always run dry-run first** to preview what will be created
2. **Check for duplicates** before creating manually
3. **Add milestones** after creation to organize by release
4. **Assign owners** to distribute work
5. **Link related issues** using "Related to #X" in comments
6. **Update project board** if using GitHub Projects

## ❓ Questions?

If you encounter issues or need help:
1. Check the [troubleshooting section](#-troubleshooting)
2. Review the main [ISSUES_FOUND.md](../ISSUES_FOUND.md) document
3. Run script with `--dry-run` to diagnose issues
4. Check script output for detailed error messages
