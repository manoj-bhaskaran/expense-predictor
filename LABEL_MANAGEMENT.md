# Automatic Label Creation Feature

## Overview

The script now **automatically creates any missing labels** before creating issues. This prevents failures due to non-existent labels and ensures consistent label colors across your repository.

## How It Works

### Step-by-Step Process

1. **Extract Labels** - Scans all issue templates to find required labels
2. **Check Existing** - Queries repository for existing labels
3. **Create Missing** - Creates only labels that don't exist
4. **Proceed** - Creates issues with guaranteed labels

### Example Output

```
▶ Checking and creating labels...

ℹ  Labels needed: bug,dependencies,critical,good first issue,priority: critical,
   priority: high,enhancement,validation,user-experience,refactoring,code-quality,
   maintenance,pandas,deprecation,python-3.12,configuration

ℹ  Fetching existing labels from repository...
ℹ  ✓ Label exists: bug
ℹ  ✓ Label exists: dependencies
ℹ  + Creating label: priority: critical (color: #d73a4a)
✓    Created: priority: critical
ℹ  + Creating label: priority: high (color: #ff6b6b)
✓    Created: priority: high
ℹ  + Creating label: good first issue (color: #7057ff)
✓    Created: good first issue
ℹ  ✓ Label exists: enhancement
ℹ  + Creating label: validation (color: #1d76db)
✓    Created: validation

✓  Label check complete: 8 existing, 9 created
```

## Label Color Scheme

The script uses GitHub-standard colors for common labels and custom colors for specific categories:

### Priority Labels
| Label | Color | Usage |
|-------|-------|-------|
| `priority: critical` | 🔴 Red (#d73a4a) | Critical issues requiring immediate attention |
| `priority: high` | 🔴 Light Red (#ff6b6b) | High priority issues |
| `priority: medium` | 🟡 Yellow (#fbca04) | Medium priority issues |
| `priority: low` | 🟢 Green (#0e8a16) | Low priority issues |

### Type Labels
| Label | Color | Usage |
|-------|-------|-------|
| `bug` | 🔴 Red (#d73a4a) | Bug reports |
| `enhancement` | 🔵 Light Blue (#a2eeef) | Feature requests |
| `documentation` | 🔵 Blue (#0075ca) | Documentation improvements |

### Category Labels
| Label | Color | Usage |
|-------|-------|-------|
| `dependencies` | 🔵 Dark Blue (#0366d6) | Dependency-related issues |
| `security` | 🔴 Bright Red (#ee0701) | Security issues |
| `refactoring` | 🟣 Purple (#d4c5f9) | Code refactoring |
| `code-quality` | 🟣 Purple (#d4c5f9) | Code quality improvements |
| `validation` | 🔵 Blue (#1d76db) | Validation-related issues |
| `configuration` | 🟣 Purple (#5319e7) | Configuration issues |
| `maintenance` | 🟡 Yellow (#fbca04) | Maintenance tasks |
| `user-experience` | 🟢 Light Green (#c2e0c6) | UX improvements |
| `pandas` | 🟣 Dark Purple (#150458) | Pandas-specific issues |
| `deprecation` | 🟡 Light Yellow (#fef2c0) | Deprecation warnings |
| `python-3.12` | 🔵 Python Blue (#3572a5) | Python 3.12 compatibility |

### Meta Labels
| Label | Color | Usage |
|-------|-------|-------|
| `good first issue` | 🟣 Purple (#7057ff) | Good for newcomers |
| `help wanted` | 🔵 Teal (#008672) | Extra attention needed |
| `wontfix` | ⚪ White (#ffffff) | Won't be fixed |
| `duplicate` | ⚪ Gray (#cfd3d7) | Duplicate issue |

## Features

### ✅ Automatic Detection
- Scans all `issue_*.md` templates
- Extracts labels from `## Labels` sections
- Automatically determines priority from severity level

### ✅ Smart Creation
- Only creates labels that don't exist
- Skips labels that already exist (no duplicates)
- Uses appropriate colors for each label type
- Handles errors gracefully

### ✅ Verbose Output
- Shows which labels exist vs created
- Displays color codes being used
- Reports final count (existing + created)

### ✅ Dry-Run Support
- Skips label creation in `--dry-run` mode
- Shows message: "Skipping label creation in dry-run mode"

## Usage

### Normal Mode
```bash
./create_github_issues.sh
```

Labels are automatically created before issues.

### Dry-Run Mode
```bash
./create_github_issues.sh --dry-run
```

Label creation is skipped (issues aren't created anyway).

### Verbose Mode
```bash
./create_github_issues.sh --verbose
```

Shows detailed output including label operations.

## Benefits

### 1. **Zero Manual Setup**
No need to manually create labels in the GitHub UI before running the script.

### 2. **Prevents Failures**
Issues won't fail to create due to missing labels.

### 3. **Consistent Colors**
All labels use predefined, meaningful colors.

### 4. **Scalable**
Adding new issue templates automatically adds new labels.

### 5. **Idempotent**
Running multiple times won't create duplicate labels.

## Technical Details

### Functions Added

#### `get_all_labels_from_templates()`
Extracts all unique labels from all issue templates.

**Returns:** Comma-separated list of unique labels

#### `check_and_create_labels()`
Main function that checks and creates labels.

**Process:**
1. Get all needed labels from templates
2. Fetch existing labels from repository
3. Compare and identify missing labels
4. Create missing labels with appropriate colors
5. Report summary

#### `get_label_color(label_name)`
Returns appropriate hex color code for a label.

**Arguments:** Label name
**Returns:** Hex color code (without #)

### Integration

The label check runs automatically:
- **After** user confirmation
- **Before** creating issues
- **Only** in normal mode (skipped in dry-run)

## Examples

### Example 1: First Run (No Labels)
```
▶ Checking and creating labels...
ℹ  Labels needed: bug,critical,priority: critical
ℹ  Fetching existing labels from repository...
ℹ  + Creating label: bug (color: #d73a4a)
✓    Created: bug
ℹ  + Creating label: critical (color: #d73a4a)
✓    Created: critical
ℹ  + Creating label: priority: critical (color: #d73a4a)
✓    Created: priority: critical
✓  Label check complete: 0 existing, 3 created
```

### Example 2: Subsequent Run (Labels Exist)
```
▶ Checking and creating labels...
ℹ  Labels needed: bug,critical,priority: critical
ℹ  Fetching existing labels from repository...
ℹ  ✓ Label exists: bug
ℹ  ✓ Label exists: critical
ℹ  ✓ Label exists: priority: critical
✓  Label check complete: 3 existing, 0 created
```

### Example 3: Partial Update (Some New Labels)
```
▶ Checking and creating labels...
ℹ  Labels needed: bug,enhancement,priority: critical,priority: high
ℹ  Fetching existing labels from repository...
ℹ  ✓ Label exists: bug
ℹ  + Creating label: enhancement (color: #a2eeef)
✓    Created: enhancement
ℹ  ✓ Label exists: priority: critical
ℹ  + Creating label: priority: high (color: #ff6b6b)
✓    Created: priority: high
✓  Label check complete: 2 existing, 2 created
```

## Troubleshooting

### "Could not fetch existing labels"
**Cause:** Network issue or permissions
**Effect:** Script continues anyway (labels created on-demand)
**Fix:** Check network and authentication

### "Could not create label"
**Cause:** Label might already exist (race condition) or permissions
**Effect:** Counted as existing, script continues
**Fix:** Verify repository write permissions

## Adding New Labels

To add support for a new label color:

1. Edit `create_github_issues.sh`
2. Find the `get_label_color()` function
3. Add your label to the appropriate case statement:

```bash
"your-new-label")
    echo "abc123"  # Your hex color
    ;;
```

4. The label will automatically be created with that color next run

## Summary

The automatic label creation feature makes the issue creation process:
- ✅ Fully automated
- ✅ Error-resistant
- ✅ Consistent
- ✅ Scalable
- ✅ Zero-configuration

No manual setup required - just run the script and all labels are created automatically! 🎉
