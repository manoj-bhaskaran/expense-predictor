helpers module
==============

.. automodule:: helpers
   :members:
   :undoc-members:
   :show-inheritance:

Module Overview
---------------

The ``helpers`` module provides data preprocessing, validation, and utility functions
for the Expense Predictor system.

Key Functions
-------------

Validation Functions
^^^^^^^^^^^^^^^^^^^^

* :func:`validate_csv_file` - Validate CSV file existence and required columns
* :func:`validate_excel_file` - Validate Excel file format and existence
* :func:`validate_date_range` - Validate date ranges in data

Data Processing Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^

* :func:`preprocess_data` - Preprocess CSV transaction data
* :func:`preprocess_and_append_csv` - Merge CSV and Excel data
* :func:`prepare_future_dates` - Generate future date features

Utility Functions
^^^^^^^^^^^^^^^^^

* :func:`find_column_name` - Flexible column name matching
* :func:`get_quarter_end_date` - Calculate quarter-end dates
* :func:`write_predictions` - Securely write prediction CSV files

Internal Functions
^^^^^^^^^^^^^^^^^^

* :func:`_process_dataframe` - Core DataFrame processing logic (not exported)

Constants
---------

The module defines several constants for column naming:

* ``DATE_LABEL`` = "Date"
* ``TRANSACTION_AMOUNT_LABEL`` = "Tran Amt"
* ``PREDICTED_AMOUNT_LABEL`` = "Predicted Tran Amt"
* ``VALUE_DATE_LABEL`` = "Value Date"
* ``WITHDRAWAL_AMOUNT_LABEL`` = "Withdrawal Amount (INR )"
* ``DEPOSIT_AMOUNT_LABEL`` = "Deposit Amount (INR )"
* ``DAY_OF_WEEK_LABEL`` = "Day of the Week"
* ``MONTH_LABEL`` = "Month"
* ``DAY_OF_MONTH_LABEL`` = "Day of the Month"

Usage Examples
--------------

Validate CSV File
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from helpers import validate_csv_file

   is_valid, error = validate_csv_file("trandata.csv")
   if not is_valid:
       print(f"Validation error: {error}")

Preprocess Data
^^^^^^^^^^^^^^^

.. code-block:: python

   from helpers import preprocess_data

   X, y = preprocess_data("trandata.csv", logger=my_logger)
   print(f"Features shape: {X.shape}")
   print(f"Target shape: {y.shape}")

Prepare Future Dates
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from helpers import prepare_future_dates
   from datetime import datetime

   future_date = datetime(2025, 12, 31)
   X_train = pd.DataFrame(...)  # Training features

   future_df = prepare_future_dates(
       future_date=future_date,
       X_train=X_train
   )
