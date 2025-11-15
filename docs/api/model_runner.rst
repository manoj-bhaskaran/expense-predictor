model_runner module
===================

.. automodule:: model_runner
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:
   :special-members: __init__

Main Workflow
-------------

The ``model_runner`` module orchestrates the complete machine learning pipeline:

1. Parse command-line arguments
2. Validate file paths and directories
3. Load and preprocess data
4. Train four regression models
5. Evaluate model performance
6. Generate future predictions
7. Save predictions to CSV files

Usage Example
-------------

.. code-block:: bash

   python model_runner.py \\
     --data_file ./data/trandata.csv \\
     --future_date 31/12/2025 \\
     --output_dir ./predictions

Models Trained
--------------

1. **Linear Regression** - Baseline model
2. **Decision Tree Regressor** - Non-linear patterns
3. **Random Forest Regressor** - Ensemble predictions
4. **Gradient Boosting Regressor** - Highest accuracy

Evaluation Metrics
------------------

Each model is evaluated using:

* RMSE (Root Mean Squared Error)
* MAE (Mean Absolute Error)
* R² Score (Coefficient of Determination)

Metrics are calculated for both training and test sets to detect overfitting.

Security Features
-----------------

* Path validation and sanitization
* File extension validation
* CSV injection prevention
* Automatic file backups
* User confirmation for overwrites
