# [CRITICAL] Replace GitHub dependency with PyPI package or vendored code

## Priority
🔴 **Critical**

## Labels
`critical`, `dependencies`, `security`, `technical-debt`

## Description

The project currently installs `python_logging_framework` directly from a GitHub repository using an unpinned branch reference:

```python
# requirements.txt:16
git+https://github.com/manoj-bhaskaran/My-Scripts.git@main
```

This creates several critical issues:

### Problems

1. **No Version Pinning**: Installing from `@main` branch means the code can change unexpectedly, potentially introducing breaking changes
2. **Security Risk**: The GitHub repository could be compromised, deleted, or made private
3. **Installation Fragility**: Requires Git to be installed on all systems, plus network access to GitHub during installation
4. **No Integrity Verification**: Unlike PyPI packages, there's no hash verification for security
5. **CI/CD Reliability**: GitHub rate limiting or outages will break all builds
6. **Offline Installation**: Cannot install the package without internet access to GitHub

### Current State

The repository already contains `python_logging_framework.py` locally, making it unclear which version is actually being used.

## Proposed Solutions

Choose one of the following approaches:

### Option 1: Use Local Version (Recommended for quick fix)
1. Remove the Git dependency from `requirements.txt`
2. Keep the local `python_logging_framework.py` file
3. Document this decision in README.md

### Option 2: Pin to Specific Commit (Temporary fix)
```python
git+https://github.com/manoj-bhaskaran/My-Scripts.git@<commit-hash>#subdirectory=python_logging_framework
```

### Option 3: Publish to PyPI (Best long-term solution)
1. Package `python_logging_framework` as a proper Python package
2. Publish to PyPI
3. Install from PyPI with pinned version

## Acceptance Criteria

- [ ] Git dependency removed from `requirements.txt`
- [ ] Installation works without Git installed
- [ ] Installation works in offline environments (if using local version)
- [ ] No breaking changes to existing functionality
- [ ] Documentation updated to reflect the change
- [ ] CI/CD pipeline passes

## Additional Context

This issue blocks reliable deployment in production environments and should be addressed before any production release.

## Related Files
- `requirements.txt`
- `python_logging_framework.py`
- `README.md`
