config module
=============

.. automodule:: config
   :members:
   :undoc-members:
   :show-inheritance:

Module Overview
---------------

The ``config`` module manages configuration loading from YAML files with fallback
to sensible defaults.

Functions
---------

* :func:`load_config` - Load configuration from YAML file
* :func:`get_config` - Get the current configuration
* :func:`_merge_configs` - Merge custom config with defaults (internal)

Configuration Structure
-----------------------

The configuration is organized into the following sections:

Data Processing
^^^^^^^^^^^^^^^

.. code-block:: yaml

   data_processing:
     skiprows: 12  # Number of header rows to skip in Excel files

Model Evaluation
^^^^^^^^^^^^^^^^

.. code-block:: yaml

   model_evaluation:
     test_size: 0.2      # 20% of data for testing
     random_state: 42    # Seed for reproducibility

Decision Tree Hyperparameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   decision_tree:
     max_depth: 5
     min_samples_split: 10
     min_samples_leaf: 5
     ccp_alpha: 0.01
     random_state: 42

Random Forest Hyperparameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   random_forest:
     n_estimators: 100
     max_depth: 10
     min_samples_split: 10
     min_samples_leaf: 5
     max_features: "sqrt"
     ccp_alpha: 0.01
     random_state: 42

Gradient Boosting Hyperparameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   gradient_boosting:
     n_estimators: 100
     learning_rate: 0.1
     max_depth: 5
     min_samples_split: 10
     min_samples_leaf: 5
     max_features: "sqrt"
     random_state: 42

Default Configuration
---------------------

If ``config.yaml`` is missing or invalid, the system uses these defaults:

.. code-block:: python

   DEFAULT_CONFIG = {
       "data_processing": {
           "skiprows": 12
       },
       "model_evaluation": {
           "test_size": 0.2,
           "random_state": 42
       },
       "decision_tree": {
           "max_depth": 5,
           "min_samples_split": 10,
           "min_samples_leaf": 5,
           "ccp_alpha": 0.01,
           "random_state": 42
       },
       # ... (full default config)
   }

Usage Examples
--------------

Load Configuration
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from config import load_config

   config = load_config()
   print(config['decision_tree']['max_depth'])  # 5

Get Configuration
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from config import get_config

   # Load config (if not already loaded)
   config = get_config()

   # Access configuration values
   test_size = config['model_evaluation']['test_size']
   n_estimators = config['random_forest']['n_estimators']

Custom Configuration File
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from config import load_config

   # Load from custom path
   config = load_config("custom_config.yaml")

Configuration Fallback
^^^^^^^^^^^^^^^^^^^^^^^

The module implements graceful fallback:

1. Try to load ``config.yaml``
2. If file missing or invalid YAML → use defaults
3. If partial config → merge with defaults
4. Always returns complete configuration

Error Handling
--------------

The module handles errors gracefully:

* **File Not Found**: Uses defaults, logs info message
* **Invalid YAML**: Uses defaults, logs error message
* **Missing Sections**: Fills with defaults, no error
* **Invalid Values**: Uses defaults for that section

This ensures the application always runs, even with configuration issues.
