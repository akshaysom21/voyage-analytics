# ============================================================
# VOYAGE ANALYTICS - PREDICTION HELPER
# app/predict.py
# ============================================================

import joblib
import numpy as np
import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'models')

MODEL_PATH = os.path.join(MODELS_DIR, 'flight_price_model.pkl')
SCALER_PATH = os.path.join(MODELS_DIR, 'scaler.pkl')
COLUMNS_PATH = os.path.join(MODELS_DIR, 'feature_columns.pkl')

# Load Artifacts
print("Loading model artifacts...")
model = joblib.load(MODEL_PATH)
# scaler loaded but not applied - Random Forest doesn't require scaling
scaler = joblib.load(SCALER_PATH)
feature_columns = joblib.load(COLUMNS_PATH)
print(f"-> Model loaded successfully")
print(f"-> Features: {feature_columns}")

# Constants
FLIGHT_TYPE_MAP = {
    'economic': 0, 'premium': 1, 'firstClass': 2
}

VALID_AGENCIES = ['CloudFy', 'Rainbow', 'FlyingDrops']

# Validation
def validate_input(data):
    """
    Validate incoming request data.
    Returns (is_valid: bool, error_message: str)
    """
    required = ['distance', 'flightType', 'agency', 'month', 'day_of_week']

    # Check required fields exist
    for field in required:
        if field not in data:
            return False, f"Missing required field: '{field}'"

    # Validate distance
    try:
        distance = float(data['distance'])
        if distance <= 0:
            return False, "distance must be greater than 0"
    except (ValueError, TypeError):
        return False, "distance must be a valid number"

    # Validate flightType
    if data['flightType'] not in FLIGHT_TYPE_MAP:
        return False, f"flightType must be one of: {list(FLIGHT_TYPE_MAP.keys())}"

    # Validate agency
    if data['agency'] not in VALID_AGENCIES:
        return False, f"agency must be one of: {VALID_AGENCIES}"

    # Validate month
    try:
        month = int(data['month'])
        if not 1 <= month <= 12:
            return False, "month must be between 1 and 12"
    except (ValueError, TypeError):
        return False, "month must be a valid integer"

    # Validate day_of_week
    try:
        dow = int(data['day_of_week'])
        if not 0 <= dow <= 6:
            return False, "day_of_week must be between 0 (Monday) and 6 (Sunday)"
    except (ValueError, TypeError):
        return False, "day_of_week must be a valid integer"

    return True, None


# Feature Builder
def build_features(data):
    """
    Convert raw input into model-ready DataFrame.
    Must match exact feature engineering from training.
    """
    features = {
        'distance': float(data['distance']),
        'month': int(data['month']),
        'day_of_week': int(data['day_of_week']),
        'flightType_encoded': FLIGHT_TYPE_MAP[data['flightType']],
        'agency_CloudFy': 1 if data['agency'] == 'CloudFy' else 0,
        'agency_FlyingDrops': 1 if data['agency'] == 'FlyingDrops' else 0,
        'agency_Rainbow': 1 if data['agency'] == 'Rainbow' else 0,
    }

    # Ensure correct column order matching training
    input_df = pd.DataFrame([features])[feature_columns]
    return input_df


# Main Predict Function
def predict_price(data):
    """
    Main prediction function called by Flask routes.

    Parameters:
        data (dict): Input with distance, flightType,
                     agency, month, day_of_week

    Returns:
        dict: prediction result or error
    """

    # Validate
    is_valid, error_msg = validate_input(data)
    if not is_valid:
        return {'success': False, 'error': error_msg}

    # Build features
    input_df = build_features(data)

    # Predict
    prediction = model.predict(input_df)[0]

    return {
        'success': True,
        'predicted_price': round(float(prediction), 2),
        'currency': 'USD',
        'input_received': {
            'distance': float(data['distance']),
            'flightType': data['flightType'],
            'agency': data['agency'],
            'month': int(data['month']),
            'day_of_week': int(data['day_of_week'])
        },
        'model_info': {
            'model_type': 'Random Forest Regressor',
            'r2_score': 0.9067,
            'mae': 61.8,
            'rmse': 110.9
        }
    }