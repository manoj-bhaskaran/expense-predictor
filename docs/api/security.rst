security module
===============

.. automodule:: security
   :members:
   :undoc-members:
   :show-inheritance:

Module Overview
---------------

The ``security`` module provides security utilities to protect against common
attack vectors including path traversal, CSV injection, and accidental file overwrites.

Security Functions
------------------

Path Validation
^^^^^^^^^^^^^^^

* :func:`validate_and_resolve_path` - Core path validation with security checks
* :func:`validate_file_path` - File-specific validation with extension checking
* :func:`validate_directory_path` - Directory validation with auto-creation

CSV Protection
^^^^^^^^^^^^^^

* :func:`sanitize_csv_value` - Sanitize individual values for CSV output
* :func:`sanitize_dataframe_for_csv` - Sanitize entire DataFrames

File Protection
^^^^^^^^^^^^^^^

* :func:`create_backup` - Create timestamped backups before modifications
* :func:`confirm_overwrite` - Interactive confirmation for file overwrites

Security Features
-----------------

Path Injection Protection
^^^^^^^^^^^^^^^^^^^^^^^^^

All user-provided file paths are validated to prevent path traversal attacks:

* Paths are resolved to absolute paths using ``pathlib.Path().resolve()``
* Path traversal patterns (``../``) are detected and rejected
* Invalid paths are rejected with clear error messages

.. code-block:: python

   from security import validate_file_path

   # Safe path
   path = validate_file_path("./data/file.csv", [".csv"])
   # Returns: /absolute/path/to/data/file.csv

   # Dangerous path (rejected)
   try:
       path = validate_file_path("../../etc/passwd", [".csv"])
   except ValueError as e:
       print(e)  # "Path traversal detected"

File Extension Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^

The application validates file extensions before processing:

* CSV files must have ``.csv`` extension
* Excel files must have ``.xls`` or ``.xlsx`` extension
* Invalid extensions are rejected before processing

.. code-block:: python

   from security import validate_file_path

   # Valid CSV
   csv_path = validate_file_path("data.csv", [".csv"])

   # Valid Excel
   excel_path = validate_file_path("data.xlsx", [".xls", ".xlsx"])

   # Invalid (rejected)
   try:
       validate_file_path("data.txt", [".csv"])
   except ValueError:
       print("Invalid extension")

CSV Injection Prevention
^^^^^^^^^^^^^^^^^^^^^^^^

All CSV output is sanitized to prevent formula injection attacks:

* Dangerous formula characters (``=``, ``+``, ``-``, ``@``, tabs, newlines) are escaped
* Values that could be interpreted as formulas are prefixed with a single quote
* Protects users who open CSVs in Excel or other spreadsheet applications

.. code-block:: python

   from security import sanitize_csv_value

   # Dangerous value
   value = "=1+1"
   safe_value = sanitize_csv_value(value)
   print(safe_value)  # "'=1+1"

   # Safe value (unchanged)
   value = "100.50"
   safe_value = sanitize_csv_value(value)
   print(safe_value)  # "100.50"

File Overwrite Protection
^^^^^^^^^^^^^^^^^^^^^^^^^^

The application protects against accidental data loss:

* **Automatic Backups**: Creates timestamped backups before overwriting
* **User Confirmation**: Prompts for confirmation before overwriting files
* **Fail-Safe**: If backup creation fails, write operation is aborted

.. code-block:: python

   from security import create_backup, confirm_overwrite

   # Create backup
   backup_path = create_backup("predictions.csv")
   print(f"Backup created: {backup_path}")

   # Confirm overwrite
   if confirm_overwrite("predictions.csv", skip_confirmation=False):
       # Proceed with writing
       pass

Usage Examples
--------------

Validate and Resolve Path
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from security import validate_and_resolve_path

   path = validate_and_resolve_path(
       "./data/file.csv",
       must_exist=True,
       path_type="file",
       description="Data file"
   )

Sanitize DataFrame for CSV
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from security import sanitize_dataframe_for_csv
   import pandas as pd

   df = pd.DataFrame({
       'Date': ['2024-01-01', '2024-01-02'],
       'Amount': ['=SUM(A1:A10)', '100.50']  # Dangerous!
   })

   safe_df = sanitize_dataframe_for_csv(df)
   print(safe_df['Amount'][0])  # "'=SUM(A1:A10)"

Validate Directory Path
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from security import validate_directory_path

   # Create directory if it doesn't exist
   dir_path = validate_directory_path(
       "./logs",
       create_if_missing=True,
       description="Log directory"
   )
