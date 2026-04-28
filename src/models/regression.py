# regression.py
# This file trains regression models.
# Target: flight_price
# Goal: Predict flight ticket price.
# MLOps: Uses MLflow and DagsHub for experiment tracking.

import os
import joblib
import dagshub
import mlflow
import mlflow.sklearn

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==============================
# BASIC PATH CONFIGURATION
# ==============================

# Gets the main project folder path.
# This helps the file run correctly from any terminal location.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Input dataset path.
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "processed_data.csv")

# Regression target column.
# This target is taken based on your EDA.
TARGET_COLUMN = "flight_price"

# Output folders.
MODEL_OUTPUT_DIR = os.path.join(BASE_DIR, "models")
REPORT_OUTPUT_DIR = os.path.join(BASE_DIR, "reports")

# Output file paths.
BEST_MODEL_PATH = os.path.join(MODEL_OUTPUT_DIR, "best_regression_model.pkl")
METRICS_CSV_PATH = os.path.join(REPORT_OUTPUT_DIR, "regression_metrics.csv")
PREDICTIONS_CSV_PATH = os.path.join(REPORT_OUTPUT_DIR, "regression_predictions.csv")

# MLflow experiment name.
EXPERIMENT_NAME = "regression_experiment"


# ==============================
# CREATE REQUIRED FOLDERS
# ==============================

os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)


# ==============================
# DAGSHUB + MLFLOW SETUP
# ==============================

# Modify these with your DagsHub details if you want to log to DagsHub. Otherwise, it will log to MLflow locally.
repo_owner = "Shyamsr1"
repo_name = "VoyageAnalyticsMIOpsProject"

if repo_owner and repo_name:
    dagshub.init(
        repo_owner=repo_owner,
        repo_name=repo_name,
        mlflow=True
    )
else:
    print("DagsHub details not found. Running MLflow locally only.")

mlflow.set_experiment(EXPERIMENT_NAME)


# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv(DATA_PATH)

if TARGET_COLUMN not in df.columns:
    raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataset.")

# Remove rows where regression target is missing.
df = df.dropna(subset=[TARGET_COLUMN])

# Convert target column to numeric.
df[TARGET_COLUMN] = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")

# Remove rows where target became missing after conversion.
df = df.dropna(subset=[TARGET_COLUMN])


# ==============================
# REMOVE UNWANTED COLUMNS
# ==============================

# Do not use artificial targets.
drop_cols = [
    "trip_cost_category",
    "total_trip_cost"
]

# Do not use classification target as input for regression.
if "flight_type" in df.columns:
    drop_cols.append("flight_type")

df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors="ignore")


# ==============================
# SPLIT FEATURES AND TARGET
# ==============================

X = df.drop(columns=[TARGET_COLUMN])
y = df[TARGET_COLUMN]


# ==============================
# REMOVE ID COLUMNS IF PRESENT
# ==============================

id_cols = ["travelCode", "userCode"]

X = X.drop(columns=[col for col in id_cols if col in X.columns], errors="ignore")


# ==============================
# IDENTIFY NUMERIC AND CATEGORICAL COLUMNS
# ==============================

numeric_columns = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
categorical_columns = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()


# ==============================
# NUMERIC PREPROCESSING
# ==============================

numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]
)


# ==============================
# CATEGORICAL PREPROCESSING
# ==============================

categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ]
)


# ==============================
# COMPLETE PREPROCESSOR
# ==============================

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_pipeline, numeric_columns),
        ("cat", categorical_pipeline, categorical_columns)
    ]
)


# ==============================
# TRAIN TEST SPLIT
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ==============================
# MODELS TO COMPARE
# ==============================

models = {
    "LinearRegression": LinearRegression(),

    "Ridge": Ridge(alpha=1.0),

    "Lasso": Lasso(alpha=0.01, max_iter=5000),

    "ElasticNet": ElasticNet(
        alpha=0.01,
        l1_ratio=0.5,
        max_iter=5000
    ),

    "RandomForestRegressor": RandomForestRegressor(
        n_estimators=200,
        random_state=42
    ),

    "GradientBoostingRegressor": GradientBoostingRegressor(
        random_state=42
    )
}


# ==============================
# TRAIN MODELS AND EVALUATE
# ==============================

results = []

best_model = None
best_model_name = None
best_rmse = float("inf")

for model_name, model in models.items():

    with mlflow.start_run(run_name=model_name):

        # Combine preprocessing and model into one pipeline.
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model)
            ]
        )

        # Train model.
        pipeline.fit(X_train, y_train)

        # Predict test data.
        y_pred = pipeline.predict(X_test)

        # Calculate regression metrics.
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        # Log parameters to MLflow.
        mlflow.log_param("model_name", model_name)
        mlflow.log_param("target_column", TARGET_COLUMN)
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("random_state", 42)

        # Log metrics to MLflow.
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2_score", r2)

        # Log model to MLflow.
        mlflow.sklearn.log_model(pipeline, name="model")

        # Store results locally.
        results.append(
            {
                "model": model_name,
                "mae": mae,
                "mse": mse,
                "rmse": rmse,
                "r2_score": r2
            }
        )

        # Best model is selected based on lowest RMSE.
        if rmse < best_rmse:
            best_rmse = rmse
            best_model = pipeline
            best_model_name = model_name


# ==============================
# SAVE MODEL COMPARISON RESULTS
# ==============================

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="rmse", ascending=True)
results_df.to_csv(METRICS_CSV_PATH, index=False)


# ==============================
# SAVE BEST MODEL
# ==============================

joblib.dump(best_model, BEST_MODEL_PATH)


# ==============================
# SAVE BEST MODEL PREDICTIONS
# ==============================

best_predictions = best_model.predict(X_test)

predictions_df = pd.DataFrame(
    {
        "actual": y_test.values,
        "predicted": best_predictions
    }
)

predictions_df.to_csv(PREDICTIONS_CSV_PATH, index=False)


# ==============================
# LOG FINAL BEST MODEL DETAILS
# ==============================

with mlflow.start_run(run_name="Best_Regression_Model"):

    mlflow.log_param("best_model_name", best_model_name)
    mlflow.log_metric("best_rmse", best_rmse)

    mlflow.log_artifact(METRICS_CSV_PATH)
    mlflow.log_artifact(PREDICTIONS_CSV_PATH)

    mlflow.sklearn.log_model(best_model, name="best_regression_model")


# ==============================
# FINAL OUTPUT
# ==============================

print("Regression training completed.")
print(f"Best Regression Model: {best_model_name}")
print(f"Best RMSE: {best_rmse}")
print(f"Saved model at: {BEST_MODEL_PATH}")
print(f"Saved metrics at: {METRICS_CSV_PATH}")