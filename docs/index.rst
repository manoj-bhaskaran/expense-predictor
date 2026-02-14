Expense Predictor Documentation
=================================

Welcome to the Expense Predictor documentation! This system uses machine learning
to analyze historical transaction data and forecast future expenses.

.. image:: https://img.shields.io/badge/python-3.10+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Quick Start
-----------

Install the package and run predictions:

.. code-block:: bash

   pip install -r requirements.txt
   python model_runner.py --data_file trandata.csv

Features
--------

* **Multiple ML Models**: Linear Regression, Decision Tree, Random Forest, Gradient Boosting
* **Flexible Data Input**: CSV transaction data and Excel bank statements
* **Robust Validation**: Comprehensive input validation and security features
* **Performance Metrics**: RMSE, MAE, and R² evaluation metrics
* **Configurable**: YAML-based configuration for hyperparameters
* **Complete CI/CD**: Automated testing, code quality, and security scanning

User Guide
----------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   usage
   configuration

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   data_formats
   models
   architecture
   api/index

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   testing
   changelog

API Reference
-------------

Complete API documentation for all modules:

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Support
=======

* GitHub: https://github.com/manoj-bhaskaran/expense-predictor
* Issues: https://github.com/manoj-bhaskaran/expense-predictor/issues

License
=======

This project is licensed under the MIT License.
