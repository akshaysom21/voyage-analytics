# classification.py
# This file trains classification models.
# Target: flight_type
# Goal: Predict whether the flight is economic, premium, or firstClass.
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
from sklearn.preprocessing import OneHotEncoder, StandardScaler, label_binarize
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ==============================
# BASIC PATH CONFIGURATION
# ==============================

# Gets the main project folder path.
# This helps the file run correctly from any terminal location.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Input dataset path.
# This file is created from your EDA / preprocessing step.
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "processed_data.csv")

# Classification target column.
# This target is taken based on your EDA.
TARGET_COLUMN = "flight_type"

# Output folders.
MODEL_OUTPUT_DIR = os.path.join(BASE_DIR, "models")
REPORT_OUTPUT_DIR = os.path.join(BASE_DIR, "reports")

# Output file paths.
BEST_MODEL_PATH = os.path.join(MODEL_OUTPUT_DIR, "best_classification_model.pkl")
METRICS_CSV_PATH = os.path.join(REPORT_OUTPUT_DIR, "classification_metrics.csv")
CONFUSION_MATRIX_PATH = os.path.join(REPORT_OUTPUT_DIR, "classification_confusion_matrix.csv")
CLASSIFICATION_REPORT_PATH = os.path.join(REPORT_OUTPUT_DIR, "classification_report.txt")

# MLflow experiment name.
EXPERIMENT_NAME = "classification_experiment"


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

# If DagsHub details are available, connect MLflow with DagsHub.
if repo_owner and repo_name:
    dagshub.init(
        repo_owner=repo_owner,
        repo_name=repo_name,
        mlflow=True
    )
else:
    print("DagsHub details not found. Running MLflow locally only.")

# Set MLflow experiment name.
mlflow.set_experiment(EXPERIMENT_NAME)


# ==============================
# LOAD DATA
# ==============================

# Read processed dataset.
df = pd.read_csv(DATA_PATH)

# Check whether target column exists.
if TARGET_COLUMN not in df.columns:
    raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataset.")

# Drop rows where target is missing.
df = df.dropna(subset=[TARGET_COLUMN])

# Remove unwanted artificial columns if present.
# These should not be used for final classification.
drop_cols = [
    "trip_cost_category",
    "total_trip_cost",
    "flight_price"
]

df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors="ignore")


# ==============================
# SPLIT FEATURES AND TARGET
# ==============================

# X contains input features.
X = df.drop(columns=[TARGET_COLUMN])

# y contains output class.
y = df[TARGET_COLUMN]


# ==============================
# REMOVE ID COLUMNS IF PRESENT
# ==============================

# ID columns usually do not help general prediction.
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

# Missing numeric values are replaced with median.
# Numeric values are scaled for linear models.
numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]
)


# ==============================
# CATEGORICAL PREPROCESSING
# ==============================

# Missing categorical values are replaced with most frequent value.
# Text/category columns are converted into numeric columns using OneHotEncoder.
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

# stratify=y keeps class distribution balanced in train and test data.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==============================
# MODELS TO COMPARE
# ==============================

models = {
    "LogisticRegression": LogisticRegression(max_iter=1000),

    "RandomForestClassifier": RandomForestClassifier(
        n_estimators=200,
        random_state=42
    ),

    "GradientBoostingClassifier": GradientBoostingClassifier(
        random_state=42
    )
}


# ==============================
# TRAIN MODELS AND EVALUATE
# ==============================

results = []

best_model = None
best_model_name = None
best_f1_score = -1

for model_name, model in models.items():

    with mlflow.start_run(run_name=model_name):

        # Combine preprocessing and model into one pipeline.
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model)
            ]
        )

        # Train the model.
        pipeline.fit(X_train, y_train)

        # Predict test data.
        y_pred = pipeline.predict(X_test)

        # Calculate classification metrics.
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        # ROC AUC calculation.
        roc_auc = None

        try:
            if hasattr(pipeline.named_steps["model"], "predict_proba"):
                y_proba = pipeline.predict_proba(X_test)
                classes = np.unique(y)

                if len(classes) == 2:
                    roc_auc = roc_auc_score(y_test, y_proba[:, 1])
                else:
                    y_test_bin = label_binarize(y_test, classes=classes)
                    roc_auc = roc_auc_score(
                        y_test_bin,
                        y_proba,
                        average="weighted",
                        multi_class="ovr"
                    )
        except Exception:
            roc_auc = None

        # Log parameters to MLflow.
        mlflow.log_param("model_name", model_name)
        mlflow.log_param("target_column", TARGET_COLUMN)
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("random_state", 42)

        # Log metrics to MLflow.
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision_weighted", precision)
        mlflow.log_metric("recall_weighted", recall)
        mlflow.log_metric("f1_weighted", f1)

        if roc_auc is not None:
            mlflow.log_metric("roc_auc", roc_auc)

        # Log model to MLflow.
        mlflow.sklearn.log_model(pipeline, name="model")

        # Store results locally.
        results.append(
            {
                "model": model_name,
                "accuracy": accuracy,
                "precision_weighted": precision,
                "recall_weighted": recall,
                "f1_weighted": f1,
                "roc_auc": roc_auc
            }
        )

        # Select best model based on F1 score.
        if f1 > best_f1_score:
            best_f1_score = f1
            best_model = pipeline
            best_model_name = model_name


# ==============================
# SAVE MODEL COMPARISON RESULTS
# ==============================

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="f1_weighted", ascending=False)
results_df.to_csv(METRICS_CSV_PATH, index=False)


# ==============================
# SAVE BEST MODEL
# ==============================

joblib.dump(best_model, BEST_MODEL_PATH)


# ==============================
# SAVE CONFUSION MATRIX AND REPORT
# ==============================

best_predictions = best_model.predict(X_test)

cm = confusion_matrix(y_test, best_predictions)
cm_df = pd.DataFrame(cm)
cm_df.to_csv(CONFUSION_MATRIX_PATH, index=False)

report = classification_report(y_test, best_predictions, zero_division=0)

with open(CLASSIFICATION_REPORT_PATH, "w") as f:
    f.write(f"Best Classification Model: {best_model_name}\n\n")
    f.write(report)


# ==============================
# LOG FINAL BEST MODEL DETAILS
# ==============================

with mlflow.start_run(run_name="Best_Classification_Model"):

    mlflow.log_param("best_model_name", best_model_name)
    mlflow.log_metric("best_f1_weighted", best_f1_score)

    mlflow.log_artifact(METRICS_CSV_PATH)
    mlflow.log_artifact(CONFUSION_MATRIX_PATH)
    mlflow.log_artifact(CLASSIFICATION_REPORT_PATH)

    mlflow.sklearn.log_model(best_model, name="best_classification_model")


# ==============================
# FINAL OUTPUT
# ==============================

print("Classification training completed.")
print(f"Best Classification Model: {best_model_name}")
print(f"Best F1 Score: {best_f1_score}")
print(f"Saved model at: {BEST_MODEL_PATH}")
print(f"Saved metrics at: {METRICS_CSV_PATH}")