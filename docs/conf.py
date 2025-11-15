# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Expense Predictor'
copyright = '2025, Manoj Bhaskaran'
author = 'Manoj Bhaskaran'
release = '1.7.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',       # Auto-generate docs from docstrings
    'sphinx.ext.napoleon',      # Support Google/NumPy docstring formats
    'sphinx.ext.viewcode',      # Add links to source code
    'sphinx.ext.intersphinx',   # Link to other projects' documentation
    'sphinx.ext.autosummary',   # Generate summary tables
    'sphinx.ext.coverage',      # Check documentation coverage
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Autosummary settings
autosummary_generate = True
add_module_names = False

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'display_version': True,
}

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
}

# -- Additional options ------------------------------------------------------

# The suffix(es) of source filenames
source_suffix = '.rst'

# The master toctree document
master_doc = 'index'

# Output file base name for HTML help builder
htmlhelp_basename = 'ExpensePredictordoc'

# Grouping the document tree into LaTeX files
latex_documents = [
    (master_doc, 'ExpensePredictor.tex', 'Expense Predictor Documentation',
     'Manoj Bhaskaran', 'manual'),
]

# Grouping the document tree into Texinfo files
texinfo_documents = [
    (master_doc, 'ExpensePredictor', 'Expense Predictor Documentation',
     author, 'ExpensePredictor', 'ML-based expense prediction system.',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# Coverage configuration
coverage_show_missing_items = True
