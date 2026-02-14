Installation
============

This guide walks through installing the Expense Predictor system.

Requirements
------------

* Python 3.10 or higher
* Git (required for installing dependencies from GitHub)
* pip (Python package installer)

Step 1: Clone the Repository
-----------------------------

.. code-block:: bash

   git clone https://github.com/manoj-bhaskaran/expense-predictor.git
   cd expense-predictor

Step 2: Create Virtual Environment
-----------------------------------

It's recommended to use a virtual environment to isolate dependencies:

**On Linux/macOS:**

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate

**On Windows:**

.. code-block:: batch

   python -m venv venv
   venv\Scripts\activate

Step 3: Install Dependencies
-----------------------------

Production Dependencies
^^^^^^^^^^^^^^^^^^^^^^^

Install the core dependencies needed to run the application:

.. code-block:: bash

   pip install -r requirements.txt

This will install:

* numpy - Numerical computing
* pandas - Data manipulation
* scikit-learn - Machine learning models
* xlrd - Excel file reading (.xls)
* pyyaml - Configuration parsing
* python_logging_framework - Logging (from GitHub)

Development Dependencies (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For development work (testing, linting, documentation):

.. code-block:: bash

   pip install -r requirements-dev.txt

This includes:

* Testing: pytest, pytest-cov, pytest-mock, openpyxl
* Linting: flake8, pylint, black, isort
* Type checking: mypy
* Documentation: sphinx, sphinx-rtd-theme
* Development tools: ipython, jupyter, notebook

Step 4: Verify Installation
----------------------------

Test that everything is installed correctly:

.. code-block:: bash

   python -c "import pandas, sklearn, yaml; print('Installation successful!')"

Run the tests (if development dependencies installed):

.. code-block:: bash

   pytest tests/ -v

Troubleshooting
---------------

Common Installation Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Issue: Git not found**

Install Git before running pip install:

* Ubuntu/Debian: ``sudo apt-get install git``
* macOS: ``brew install git`` (requires Homebrew)
* Windows: Download from https://git-scm.com/

**Issue: python_logging_framework fails to install**

This dependency is installed from GitHub. Ensure:

1. Git is installed and available in PATH
2. You have internet connectivity
3. GitHub is accessible from your network

**Issue: Permission errors**

Use ``--user`` flag for user-level installation:

.. code-block:: bash

   pip install --user -r requirements.txt

Or use ``sudo`` on Linux/macOS (not recommended):

.. code-block:: bash

   sudo pip install -r requirements.txt

**Issue: Python version too old**

Verify your Python version:

.. code-block:: bash

   python --version

If < 3.10, install a newer version from https://www.python.org/downloads/

Docker Installation (Alternative)
----------------------------------

A Dockerfile is not currently provided but could be added in future versions.

Next Steps
----------

After installation, proceed to:

* :doc:`quickstart` - Run your first prediction
* :doc:`usage` - Learn command-line options
* :doc:`configuration` - Configure hyperparameters
