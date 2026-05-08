# ============================================================
# VOYAGE ANALYTICS - MLFLOW EXPERIMENT TRACKING
# mlflow_tracking/mlflow_experiments.py
# ============================================================

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, f1_score, classification_report
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')
MODELS_DIR = os.path.join(ROOT_DIR, 'models')

# Set MLflow tracking URI (saves locally in mlflow_tracking/)
mlflow.set_tracking_uri(f"file://{BASE_DIR}/mlruns")

print("=" * 60)
print("  VOYAGE ANALYTICS - MLFLOW EXPERIMENT TRACKING")
print("=" * 60)

# ============================================================
# EXPERIMENT 1 - FLIGHT PRICE REGRESSION
# ============================================================
print("\n[1/2] Running Regression Experiments...")

mlflow.set_experiment("Flight-Price-Regression")

flights = pd.read_csv(os.path.join(DATA_DIR, 'flights.csv'))

# Feature engineering (same as regression_model.ipynb)
flights['date'] = pd.to_datetime(flights['date'])
flights['month'] = flights['date'].dt.month
flights['day_of_week'] = flights['date'].dt.dayofweek

FLIGHT_TYPE_MAP = {'economic': 0, 'premium': 1, 'firstClass': 2}
flights['flightType_encoded'] = flights['flightType'].map(FLIGHT_TYPE_MAP)

agency_dummies = pd.get_dummies(flights['agency'], prefix='agency')
flights = pd.concat([flights, agency_dummies], axis=1)

FEATURES = ['distance', 'month', 'day_of_week', 'flightType_encoded',
            'agency_CloudFy', 'agency_FlyingDrops', 'agency_Rainbow']
TARGET = 'price'

X = flights[FEATURES]
y = flights[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Models to compare
reg_models = {
    'RandomForest_100': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'RandomForest_200': RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
    'RandomForest_Best': RandomForestRegressor(n_estimators=200, max_depth=20,
        min_samples_split=2, min_samples_leaf=1, random_state=42, n_jobs=-1
    ),
}

for model_name, model in reg_models.items():
    with mlflow.start_run(run_name=model_name):

        # Log parameters
        mlflow.log_param("model_type", "RandomForestRegressor")
        mlflow.log_param("n_estimators", model.n_estimators)
        mlflow.log_param("max_depth", model.max_depth)
        mlflow.log_param("min_samples_split", model.min_samples_split)
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("train_rows", len(X_train))
        mlflow.log_param("features", FEATURES)

        # Train
        print(f"  Training {model_name}...", end='', flush=True)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        # Log metrics
        mlflow.log_metric("r2_score", round(r2, 4))
        mlflow.log_metric("mae", round(mae, 2))
        mlflow.log_metric("rmse", round(rmse, 2))

        # Log model
        mlflow.sklearn.log_model(model, "model")

        print(f" -> R2: {r2:.4f} | MAE: {mae:.2f} | RMSE: {rmse:.2f}")

print("  -> Regression experiments logged!")

# ============================================================
# EXPERIMENT 2 - GENDER CLASSIFICATION
# ============================================================
print("\n[2/2] Running Classification Experiments...")

mlflow.set_experiment("Gender-Classification")

users = pd.read_csv(os.path.join(DATA_DIR, 'users.csv'))
flights = pd.read_csv(os.path.join(DATA_DIR, 'flights.csv'))
hotels = pd.read_csv(os.path.join(DATA_DIR, 'hotels.csv'))

# Feature engineering (same as classification_model.ipynb)
flights['date'] = pd.to_datetime(flights['date'])
flights['month'] = flights['date'].dt.month

flight_features = flights.groupby('userCode').agg(
    total_flights = ('travelCode', 'count'),
    avg_flight_price = ('price', 'mean'),
    firstClass_ratio = ('flightType', lambda x: (x == 'firstClass').sum() / len(x)),
    premium_ratio = ('flightType', lambda x: (x == 'premium').sum() / len(x)),
    economic_ratio = ('flightType', lambda x: (x == 'economic').sum() / len(x)),
    avg_distance = ('distance', 'mean'),
).reset_index()

hotel_features = hotels.groupby('userCode').agg(
    total_hotel_bookings = ('travelCode', 'count'),
    avg_hotel_price = ('price', 'mean'),
    avg_stay_days = ('days', 'mean'),
).reset_index()

df = users.copy()
df = df.merge(flight_features, left_on='code', right_on='userCode', how='left').drop(columns=['userCode'])
df = df.merge(hotel_features, left_on='code', right_on='userCode', how='left').drop(columns=['userCode'])

company_dummies = pd.get_dummies(df['company'], prefix='company')
df = pd.concat([df, company_dummies], axis=1)

FEATURES_CLF = [c for c in df.columns if c not in ['code', 'name', 'gender', 'company']]
df[FEATURES_CLF] = df[FEATURES_CLF].fillna(0)

le = LabelEncoder()
y = le.fit_transform(df['gender'])
X = df[FEATURES_CLF]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

clf_models = {
    'LogisticRegression_base': (
        LogisticRegression(max_iter=1000, random_state=42),
        X_train_scaled, X_test_scaled
    ),
    'LogisticRegression_tuned': (
        LogisticRegression(C=10.0, class_weight='balanced',
                           penalty='l2', solver='saga',
                           max_iter=2000, random_state=42),
        X_train_scaled, X_test_scaled
    ),
    'RandomForest_clf': (
        RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        X_train, X_test
    ),
    'GradientBoosting_clf': (
        GradientBoostingClassifier(n_estimators=100, random_state=42),
        X_train, X_test
    ),
}

for model_name, (model, X_tr, X_te) in clf_models.items():
    with mlflow.start_run(run_name=model_name):

        mlflow.log_param("model_type", type(model).__name__)
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("train_rows", len(X_train))
        mlflow.log_param("num_features", len(FEATURES_CLF))
        mlflow.log_param("classes", list(le.classes_))

        print(f"  Training {model_name}...", end='', flush=True)
        model.fit(X_tr, y_train)
        y_pred = model.predict(X_te)

        acc = accuracy_score(y_test, y_pred)
        f1_w = f1_score(y_test, y_pred, average='weighted')
        f1_m = f1_score(y_test, y_pred, average='macro')

        mlflow.log_metric("accuracy", round(acc, 4))
        mlflow.log_metric("f1_weighted", round(f1_w, 4))
        mlflow.log_metric("f1_macro", round(f1_m, 4))

        mlflow.sklearn.log_model(model, "model")

        print(f" -> Acc: {acc:.4f} | F1 Macro: {f1_m:.4f}")

print("  -> Classification experiments logged!")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("  ALL EXPERIMENTS LOGGED SUCCESSFULLY!")
print("=" * 60)
print(f"  Tracking URI : {mlflow.get_tracking_uri()}")
print(f"  To view UI : python -m mlflow ui --port 5001")
print(f"  Then open : http://localhost:5001")
print("=" * 60)
