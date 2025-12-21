"""
Update trandata.csv with new data from an Excel file.

This script reads transaction data from an Excel file and appends it to the
trandata.csv file, avoiding duplicates and maintaining the correct format.

Usage:
    python update_trandata.py --excel_dir <EXCEL_DIR> --excel_file <EXCEL_FILE> [--data_file <DATA_FILE>] [--dry_run]

Command-Line Arguments:
    --excel_dir     : (Required) The directory where the Excel file is located
    --excel_file    : (Required) The name of the Excel file containing new transaction data
    --data_file     : (Optional) The path to the CSV file to update. Default: trandata.csv
    --dry_run       : (Optional) Preview changes without modifying the file
    --log_dir       : (Optional) The directory where log files will be saved. Default: logs/

Example:
    python update_trandata.py --excel_dir "C:\\users\\manoj\\Downloads" --excel_file "OpTransactionHistory21-12-2025 (4).xls"
    python update_trandata.py --excel_dir ./data --excel_file transactions.xlsx --data_file ./trandata.csv --dry_run
"""

import argparse
import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

import python_logging_framework as plog
from config import config
from constants import TRANSACTION_AMOUNT_LABEL, VALUE_DATE_LABEL
from helpers import find_column_name, validate_csv_file, validate_excel_file
from security import (
    ALLOWED_CSV_EXTENSIONS,
    ALLOWED_EXCEL_EXTENSIONS,
    confirm_overwrite,
    create_backup,
    sanitize_dataframe_for_csv,
    validate_directory_path,
    validate_file_path,
)

# Load environment variables from .env file (if it exists)
load_dotenv()

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments object.
    """
    parser = argparse.ArgumentParser(description="Update trandata.csv with new Excel data")
    parser.add_argument(
        "--excel_dir",
        type=str,
        required=True,
        help="Directory where the Excel file is located",
    )
    parser.add_argument(
        "--excel_file",
        type=str,
        required=True,
        help="Name of the Excel file containing new transaction data",
    )
    parser.add_argument(
        "--data_file",
        type=str,
        default="trandata.csv",
        help="Path to the CSV file to update (default: trandata.csv)",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Preview changes without modifying the file",
    )
    parser.add_argument(
        "--log_dir",
        type=str,
        default="logs",
        help="Directory where log files will be saved (default: logs/)",
    )
    return parser.parse_args()


def read_existing_csv(file_path: str, logger: logging.Logger) -> pd.DataFrame:
    """
    Read existing CSV file.

    Args:
        file_path: Path to the CSV file.
        logger: Logger instance.

    Returns:
        pd.DataFrame: Existing data or empty DataFrame if file doesn't exist.
    """
    if os.path.exists(file_path):
        validate_csv_file(file_path, logger=logger)
        df = pd.read_csv(file_path)
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Date"])
        plog.log_info(logger, f"Loaded {len(df)} existing records from {file_path}")
        return df
    else:
        plog.log_info(logger, f"File {file_path} does not exist. Will create new file.")
        return pd.DataFrame(columns=["Date", TRANSACTION_AMOUNT_LABEL])


def read_excel_data(excel_path: str, logger: logging.Logger) -> pd.DataFrame:
    """
    Read and process Excel file.

    Args:
        excel_path: Path to the Excel file.
        logger: Logger instance.

    Returns:
        pd.DataFrame: Processed Excel data with Date and Tran Amt columns.
    """
    validate_excel_file(excel_path, logger=logger)

    engine = "xlrd" if excel_path.endswith(".xls") else "openpyxl"
    sheet_names = pd.ExcelFile(excel_path, engine=engine).sheet_names
    plog.log_info(logger, f"Available sheets: {sheet_names}")

    skiprows = config["data_processing"]["skiprows"]
    excel_data = pd.read_excel(excel_path, sheet_name=sheet_names[0], engine=engine, skiprows=skiprows)
    excel_data.columns = excel_data.columns.str.strip()
    plog.log_info(logger, f"Columns in the sheet: {excel_data.columns.tolist()}")

    # Find the value date column
    value_date_col = find_column_name(excel_data.columns, VALUE_DATE_LABEL)
    if value_date_col is None:
        plog.log_error(logger, f"{VALUE_DATE_LABEL} column not found. Available columns: {excel_data.columns.tolist()}")
        raise ValueError(f"{VALUE_DATE_LABEL} column not found in Excel file")

    plog.log_info(logger, f"Using '{value_date_col}' as {VALUE_DATE_LABEL} column")
    excel_data[value_date_col] = pd.to_datetime(excel_data[value_date_col], dayfirst=True, errors="coerce")
    excel_data = excel_data.dropna(subset=[value_date_col])

    # Rename to standard VALUE_DATE_LABEL for consistency
    if value_date_col != VALUE_DATE_LABEL:
        excel_data = excel_data.rename(columns={value_date_col: VALUE_DATE_LABEL})

    # Find the withdrawal and deposit columns
    withdrawal_col = find_column_name(excel_data.columns, "Withdrawal Amount (INR )")
    deposit_col = find_column_name(excel_data.columns, "Deposit Amount (INR )")

    if withdrawal_col is None or deposit_col is None:
        plog.log_error(
            logger,
            f"Required columns not found. Expected: 'Withdrawal Amount (INR )' and 'Deposit Amount (INR )'. "
            f"Found: {excel_data.columns.tolist()}",
        )
        raise ValueError("Required columns not found in Excel file")

    plog.log_info(logger, f"Using columns: '{withdrawal_col}' for withdrawals and '{deposit_col}' for deposits")

    # Calculate net expense (withdrawals as negative, deposits as positive)
    excel_data["expense"] = excel_data[withdrawal_col].fillna(0) * -1 + excel_data[deposit_col].fillna(0)

    # Group by date and sum the expenses
    daily_expenses = excel_data.groupby(VALUE_DATE_LABEL)["expense"].sum().reset_index()
    daily_expenses.columns = ["Date", TRANSACTION_AMOUNT_LABEL]

    plog.log_info(logger, f"Processed {len(daily_expenses)} daily records from Excel file")
    return daily_expenses


def merge_and_deduplicate(existing_df: pd.DataFrame, new_df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """
    Merge existing and new data, removing duplicates.

    Args:
        existing_df: Existing CSV data.
        new_df: New Excel data.
        logger: Logger instance.

    Returns:
        pd.DataFrame: Merged and deduplicated data.
    """
    # Combine the dataframes
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)

    # Remove duplicates, keeping the last occurrence (newer data)
    combined_df = combined_df.drop_duplicates(subset=["Date"], keep="last")

    # Sort by date
    combined_df = combined_df.sort_values(by="Date").reset_index(drop=True)

    # Calculate how many new records were added
    new_records = len(combined_df) - len(existing_df)
    plog.log_info(logger, f"Added {new_records} new records (after deduplication)")

    return combined_df


def write_csv(df: pd.DataFrame, file_path: str, dry_run: bool, logger: logging.Logger) -> None:
    """
    Write the updated data to CSV file.

    Args:
        df: DataFrame to write.
        file_path: Path to the output CSV file.
        dry_run: If True, only preview without writing.
        logger: Logger instance.
    """
    # Format dates to DD/MM/YYYY
    output_df = df.copy()
    output_df["Date"] = output_df["Date"].dt.strftime("%d/%m/%Y")

    if dry_run:
        plog.log_info(logger, "DRY RUN - Preview of changes:")
        plog.log_info(logger, f"Total records: {len(output_df)}")
        plog.log_info(logger, f"Date range: {output_df['Date'].min()} to {output_df['Date'].max()}")
        plog.log_info(logger, "\nFirst 10 records:")
        plog.log_info(logger, f"\n{output_df.head(10).to_string(index=False)}")
        plog.log_info(logger, "\nLast 10 records:")
        plog.log_info(logger, f"\n{output_df.tail(10).to_string(index=False)}")
        plog.log_info(logger, "\nNo changes were made (dry run mode)")
        return

    # Create backup if file exists
    if os.path.exists(file_path):
        if not confirm_overwrite(file_path, logger):
            plog.log_info(logger, f"Skipped writing to {file_path}")
            return

        try:
            backup_path = create_backup(file_path, logger)
            if backup_path:
                plog.log_info(logger, f"Created backup: {backup_path}")
        except IOError as e:
            plog.log_error(logger, f"Failed to create backup, aborting write: {e}")
            raise

    # Sanitize data to prevent CSV injection
    plog.log_info(logger, "Sanitizing data to prevent CSV injection")
    sanitized_df = sanitize_dataframe_for_csv(output_df)

    # Write to CSV
    try:
        sanitized_df.to_csv(file_path, index=False)
        plog.log_info(logger, f"Successfully updated {file_path}")
        plog.log_info(logger, f"Total records: {len(sanitized_df)}")
        plog.log_info(logger, f"Date range: {sanitized_df['Date'].min()} to {sanitized_df['Date'].max()}")
    except (IOError, OSError) as e:
        plog.log_error(logger, f"Failed to write to {file_path}: {e}")
        raise


def main() -> int:
    """
    Main entry point for the update script.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    args = parse_args()

    # Setup logging
    try:
        log_dir_path_str = os.path.join(SCRIPT_DIR, args.log_dir) if not os.path.isabs(args.log_dir) else args.log_dir
        log_dir_path_obj = validate_directory_path(log_dir_path_str, create_if_missing=True)
        log_dir_path = str(log_dir_path_obj)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: Invalid log directory path: {e}")
        return 1

    logger = plog.initialise_logger(script_name="update_trandata.py", log_dir=log_dir_path)

    try:
        # Validate and get Excel file path
        excel_dir_path = validate_directory_path(args.excel_dir, must_exist=True, logger=logger)
        excel_file_str = os.path.join(str(excel_dir_path), args.excel_file)
        excel_file_path = validate_file_path(
            excel_file_str, allowed_extensions=ALLOWED_EXCEL_EXTENSIONS, must_exist=True, logger=logger
        )

        # Validate and get data file path
        if os.path.isabs(args.data_file):
            data_file_str = args.data_file
        else:
            data_file_str = os.path.join(SCRIPT_DIR, args.data_file)

        # Read existing CSV data
        existing_df = read_existing_csv(data_file_str, logger)

        # Read and process Excel data
        plog.log_info(logger, f"Processing Excel file: {excel_file_path}")
        new_df = read_excel_data(str(excel_file_path), logger)

        # Merge and deduplicate
        plog.log_info(logger, "Merging and deduplicating data")
        merged_df = merge_and_deduplicate(existing_df, new_df, logger)

        # Write the updated data
        write_csv(merged_df, data_file_str, args.dry_run, logger)

        if args.dry_run:
            plog.log_info(logger, "Dry run completed successfully")
        else:
            plog.log_info(logger, "Update completed successfully")

        return 0

    except Exception as e:
        plog.log_error(logger, f"Error updating trandata.csv: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
