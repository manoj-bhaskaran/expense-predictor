"""
Expense Predictor Script - model_runner.py

This script processes transaction data to train and evaluate multiple machine learning models. It predicts future transaction amounts for a specified future date. The predictions are saved as CSV files.

Usage:
    python model_runner.py [--future_date DD/MM/YYYY]

Command-Line Arguments:
    --future_date : (Optional) The future date for which you want to predict transaction amounts. Format: DD/MM/YYYY

Example:
    python model_runner.py --future_date 31/12/2025

If no future date is provided, the script will use the last day of the current quarter.

Steps:
1. Import Libraries and Parse Arguments:
   - The script imports necessary libraries and sets up command-line argument parsing for future_date.
   
2. Preprocess Input Data:
   - The script preprocesses input data using a helper function.

3. Define and Train Models:
   - Various machine learning models (Linear Regression, Decision Tree, Random Forest, Gradient Boosting) are defined and trained on the preprocessed data.

4. Evaluate Models:
   - Each model is evaluated using metrics like Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and R-squared.

5. Make Predictions for Future Dates:
   - The script prepares future dates and makes predictions using the trained models. Predictions are saved as CSV files.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from helpers import preprocess_and_append_csv, prepare_future_dates, write_predictions
import argparse
from datetime import datetime, timedelta

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Expense Predictor')
parser.add_argument('--future_date', type=str, help='Future date for prediction (e.g., 31/12/2025)')
args = parser.parse_args()

# Function to calculate the last day of the current quarter
def get_last_day_of_current_quarter():
    today = datetime.today()
    current_month = today.month
    if current_month <= 3:
        return datetime(today.year, 3, 31)
    elif current_month <= 6:
        return datetime(today.year, 6, 30)
    elif current_month <= 9:
        return datetime(today.year, 9, 30)
    else:
        return datetime(today.year, 12, 31)

# Use the command-line argument for future_date and convert format if needed
if args.future_date:
    try:
        future_date = datetime.strptime(args.future_date, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be DD/MM/YYYY")
else:
    future_date = get_last_day_of_current_quarter().strftime('%Y-%m-%d')

# Define constants
TRANSACTION_AMOUNT_LABEL = 'Tran Amt'

# Define file path for input data
file_path = r'D:\Python\Projects\Expense Predictor\trandata.csv'  # Use raw string literal

# Preprocess input data
X_train, y_train, df = preprocess_and_append_csv(file_path, excel_path=r'C:\Users\manoj\Downloads\OpTransactionHistory07-12-2024.xls')  # Optional Excel path

# Define a dictionary to hold model details
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        ccp_alpha=0.01,  # Added ccp_alpha parameter
        random_state=42
    ),
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",  # Changed max_features from "auto" to "sqrt"
        ccp_alpha=0.01,  # Added ccp_alpha parameter
        random_state=42
    ),
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",  # Add max_features parameter
        random_state=42
    ),
}

# Loop through models and evaluate
for model_name, model in models.items():
    """
    Train and evaluate each model, and make future predictions.

    Parameters:
    model_name (str): The name of the machine learning model.
    model (object): The machine learning model instance.
    """
    print(f"\n--- {model_name} ---")

    # Train the model
    model.fit(X_train, y_train)

    # Model performance on training data
    y_train_predictor = model.predict(X_train)

    # Use mean_squared_error to calculate RMSE
    rmse = np.sqrt(mean_squared_error(y_train, y_train_predictor))
    mae = mean_absolute_error(y_train, y_train_predictor)
    r2 = r2_score(y_train, y_train_predictor)

    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"R-squared: {r2}")

    # Prepare future dates for prediction
    future_df, future_dates = prepare_future_dates(future_date)

    # Match columns with training data
    future_df = future_df.reindex(columns=X_train.columns, fill_value=0)

    # Make predictions for future dates
    y_predict = model.predict(future_df)

    # Round the predicted transaction amounts to two decimal places
    y_predict = np.round(y_predict, 2)

    # Create a new DataFrame to store predictions with the original dates
    predicted_df = pd.DataFrame({'Date': future_dates, f'Predicted {TRANSACTION_AMOUNT_LABEL}': y_predict})

    # Save predictions to a CSV file
    output_path = rf'D:\Python\Projects\Expense Predictor\future_predictions_{model_name.replace(" ", "_").lower()}.csv'
    write_predictions(predicted_df, output_path)
