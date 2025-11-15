# Building the Documentation

This directory contains the Sphinx documentation for the Expense Predictor.

## Prerequisites

Install Sphinx and dependencies:

```bash
pip install -r ../requirements-dev.txt
```

This includes:
- sphinx
- sphinx-rtd-theme

## Building HTML Documentation

### Linux/macOS

```bash
cd docs
make html
```

### Windows

```batch
cd docs
make.bat html
```

## Viewing Documentation

After building, open the documentation in your browser:

```bash
# Linux/macOS
open _build/html/index.html

# Windows
start _build/html/index.html
```

Or navigate to: `docs/_build/html/index.html`

## Other Output Formats

Sphinx supports multiple output formats:

```bash
make pdf      # PDF (requires LaTeX)
make epub     # EPUB ebook
make man      # Man pages
make text     # Plain text
make latexpdf # PDF via LaTeX
```

## Cleaning Build Files

Remove generated documentation:

```bash
make clean
```

## Auto-Building Documentation

For development, you can use sphinx-autobuild to automatically rebuild docs when files change:

```bash
pip install sphinx-autobuild
sphinx-autobuild . _build/html
```

Then open http://127.0.0.1:8000 in your browser.

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation page
├── installation.rst     # Installation guide
├── api/                 # API documentation
│   ├── index.rst
│   ├── modules.rst
│   ├── model_runner.rst
│   ├── helpers.rst
│   ├── security.rst
│   └── config.rst
├── Makefile            # Build script (Linux/macOS)
├── make.bat            # Build script (Windows)
└── _build/             # Generated documentation (gitignored)
```

## Troubleshooting

**Issue: "sphinx-build not found"**

Solution: Install Sphinx:
```bash
pip install sphinx sphinx-rtd-theme
```

**Issue: "No module named 'helpers'"**

Solution: Run make from the docs directory, not the parent directory.

**Issue: Warnings about missing docstrings**

This is expected for functions without docstrings. Add docstrings to resolve warnings.

## Contributing to Documentation

When adding new modules or functions:

1. Add docstrings in Google format
2. Create corresponding .rst file in `docs/api/`
3. Add to the toctree in `index.rst`
4. Rebuild documentation to verify
