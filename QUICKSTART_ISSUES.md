# Quick Start: Creating GitHub Issues

This guide shows you how to quickly create all identified issues in your GitHub repository.

## 🎯 One-Command Setup

If you have GitHub CLI installed and authenticated:

```bash
# 1. Preview what will be created
./create_github_issues.sh --dry-run

# 2. Create all issues
./create_github_issues.sh
```

Done! ✅

---

## 📋 Prerequisites

### Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Ubuntu/Debian:**
```bash
sudo apt install gh
```

**Windows:**
```bash
winget install GitHub.cli
```

**Other methods:** https://cli.github.com/

### Authenticate

```bash
gh auth login
```

Follow the prompts to authenticate with your GitHub account.

---

## 🚀 Usage

### Step 1: Preview (Recommended)

Always preview first to see what will be created:

```bash
./create_github_issues.sh --dry-run
```

**Expected output:**
```
═══════════════════════════════════════════════════════════════════
  GitHub Issue Creator
═══════════════════════════════════════════════════════════════════

⚠  DRY RUN MODE - No issues will be created

▶ Checking GitHub CLI installation...
✓  GitHub CLI found: gh version 2.XX.X

▶ Checking GitHub authentication...
✓  Authenticated as: your-username

▶ Detecting repository...
✓  Detected repository: manoj-bhaskaran/expense-predictor

▶ Checking for issue templates...
✓  Found 7 issue template(s)

▶ Creating issues...

───────────────────────────────────────────────────────────────────
ℹ  Processing: issue_01_openpyxl_missing.md
ℹ  Title: Missing openpyxl in Production Dependencies
ℹ  Labels: bug,dependencies,critical,good first issue,priority: critical
⚠  [DRY RUN] Would create issue: Missing openpyxl in Production Dependencies
ℹ  [DRY RUN] With labels: bug,dependencies,critical,good first issue,priority: critical

... (continues for all 7 issues) ...

───────────────────────────────────────────────────────────────────
▶ Summary

ℹ  DRY RUN - No actual issues were created
ℹ  Total processed: 7
✓  Would create: 7
```

### Step 2: Create Issues

If the preview looks good, create the issues:

```bash
./create_github_issues.sh
```

**You'll be asked to confirm:**
```
Ready to create issues in repository: manoj-bhaskaran/expense-predictor
Continue? [y/N]
```

Type `y` and press Enter.

**Expected output:**
```
▶ Creating issues...

───────────────────────────────────────────────────────────────────
ℹ  Processing: issue_01_openpyxl_missing.md
ℹ  Title: Missing openpyxl in Production Dependencies
ℹ  Labels: bug,dependencies,critical,good first issue,priority: critical
ℹ  Checking for existing issues with this title...
ℹ  Creating issue...
✓  Created: https://github.com/manoj-bhaskaran/expense-predictor/issues/105

... (continues for all issues) ...

───────────────────────────────────────────────────────────────────
▶ Summary

ℹ  Total processed: 7
✓  Created: 7

✓  All issues created successfully!

View issues at: https://github.com/manoj-bhaskaran/expense-predictor/issues
```

---

## 🎨 Script Features

### Automatic Label Application
The script automatically applies labels based on:
- Labels listed in each issue template
- Priority extracted from severity (critical, high, medium, low)

### Duplicate Detection
The script checks if an issue with the same title already exists:
```
⚠  Issue already exists: #105
⚠  Skipping to avoid duplicates
```

### Color-Coded Output
- 🔵 Blue `ℹ` - Information
- 🟢 Green `✓` - Success
- 🟡 Yellow `⚠` - Warning
- 🔴 Red `✗` - Error

### Verbose Feedback
Every action is logged:
- Which file is being processed
- Title and labels extracted
- Whether issue exists
- Creation status and URL

---

## 🛠️ Advanced Usage

### Specify Repository

If auto-detection doesn't work or you want to create issues in a different repo:

```bash
./create_github_issues.sh --repo owner/repository
```

### Test Without Installation

See what would be parsed without requiring gh CLI:

```bash
./test_issue_parsing.sh
```

**Output:**
```
Issue Parsing Test

[1] issue_01_openpyxl_missing.md
    Title: Missing openpyxl in Production Dependencies
    Labels: bug,dependencies,critical,good first issue,priority: critical

[2] issue_02_xlrd_xlsx_incompatibility.md
    Title: xlrd 2.0.1 Cannot Read .xlsx Files
    Labels: bug,dependencies,documentation,critical,priority: critical

... (shows all 7 issues) ...

Total issues found: 7
```

### Get Help

```bash
./create_github_issues.sh --help
```

---

## 📊 What Gets Created

Running the script will create **7 GitHub issues**:

| # | Title | Severity | Labels |
|---|-------|----------|--------|
| 1 | Missing openpyxl in Production Dependencies | 🔴 Critical | bug, dependencies, critical |
| 2 | xlrd 2.0.1 Cannot Read .xlsx Files | 🔴 Critical | bug, dependencies, critical |
| 3 | Add Minimum Data Validation Before Model Training | 🔴 Critical | enhancement, validation, critical |
| 4 | Version Mismatch: line-profiler | 🟡 High | bug, dependencies |
| 5 | DRY Violation: Constants Defined Multiple Times | 🟡 High | refactoring, code-quality |
| 6 | Replace Deprecated pandas inplace=True | 🟡 High | refactoring, dependencies |
| 7 | Add Type Validation for config.yaml | 🟡 High | enhancement, validation |

---

## ✅ Verification

After creating issues, verify they were created:

```bash
# List all open issues
gh issue list

# List only critical issues
gh issue list --label "critical"

# View a specific issue
gh issue view 105
```

Or visit: https://github.com/manoj-bhaskaran/expense-predictor/issues

---

## 🐛 Troubleshooting

### "gh: command not found"
**Solution:** Install GitHub CLI (see Prerequisites section)

### "Not authenticated with GitHub"
**Solution:** Run `gh auth login` and follow prompts

### "Permission denied: ./create_github_issues.sh"
**Solution:** Make script executable:
```bash
chmod +x create_github_issues.sh
```

### "Could not detect repository"
**Solution:** Specify repository explicitly:
```bash
./create_github_issues.sh --repo manoj-bhaskaran/expense-predictor
```

### Issues already exist
**Solution:** This is normal if you've already created them. The script will skip duplicates:
```
⚠  Issue already exists: #105
⚠  Skipping to avoid duplicates
```

---

## 📚 Additional Documentation

- **Detailed issue list:** [ISSUES_FOUND.md](ISSUES_FOUND.md)
- **Review summary:** [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md)
- **Issue templates:** [github_issues/README.md](github_issues/README.md)
- **GitHub CLI docs:** https://cli.github.com/manual/

---

## 💡 Pro Tips

1. **Always dry-run first** to preview what will be created
2. **Create issues in batches** if you prefer (edit the github_issues/ directory)
3. **Assign immediately** after creation to distribute work
4. **Add to milestones** to organize by release
5. **Link related issues** using "Related to #X" in comments
6. **Use project boards** to track progress visually

---

## 🎯 Next Steps After Creation

Once issues are created:

1. **Review and prioritize** - Confirm the priority levels
2. **Assign owners** - Distribute work to team members
3. **Create milestones** - Group by release or sprint
4. **Add to projects** - Track on GitHub project boards
5. **Start fixing** - Begin with critical issues

**Recommended order:**
- Week 1: Critical issues (#1, #2, #3)
- Week 2-3: High priority issues (#4, #5, #6, #7)

---

## ❓ Questions?

- Check the [troubleshooting section](#-troubleshooting)
- Review [ISSUES_FOUND.md](ISSUES_FOUND.md) for detailed context
- Run with `--dry-run` to diagnose issues
- Check script output for detailed error messages

**Happy issue tracking! 🎉**
