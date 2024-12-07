import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from helpers import preprocess_and_append_csv, prepare_future_dates, write_predictions

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
    future_df, future_dates = prepare_future_dates()

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
