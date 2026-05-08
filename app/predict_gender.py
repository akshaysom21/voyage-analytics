# ============================================================
# VOYAGE ANALYTICS - GENDER PREDICTION HELPER
# app/predict_gender.py
# ============================================================

import joblib
import numpy as np
import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'models')

MODEL_PATH = os.path.join(MODELS_DIR, 'gender_classifier.pkl')
SCALER_PATH = os.path.join(MODELS_DIR, 'clf_scaler.pkl')
COLUMNS_PATH = os.path.join(MODELS_DIR, 'clf_feature_columns.pkl')
ENCODER_PATH = os.path.join(MODELS_DIR, 'gender_label_encoder.pkl')

# Load Artifacts
print("Loading gender classifier artifacts...")
clf_model = joblib.load(MODEL_PATH)
clf_scaler = joblib.load(SCALER_PATH)
clf_columns = joblib.load(COLUMNS_PATH)
clf_label_enc = joblib.load(ENCODER_PATH)
print(f"-> Gender classifier loaded successfully")
print(f"-> Classes: {clf_label_enc.classes_.tolist()}")

# Valid companies
VALID_COMPANIES = ['4You', 'Acme Factory', 'Monsters CYA',
                   'Umbrella LTDA', 'Wonka Company']


# Validation
def validate_gender_input(data):
    required = [
        'age', 'total_flights', 'avg_flight_price',
        'firstClass_ratio', 'premium_ratio', 'economic_ratio',
        'total_hotel_bookings', 'avg_hotel_price'
    ]
    for field in required:
        if field not in data:
            return False, f"Missing required field: '{field}'"

    try:
        age = int(data['age'])
        if not 1 <= age <= 120:
            return False, "age must be between 1 and 120"
    except (ValueError, TypeError):
        return False, "age must be a valid integer"

    try:
        tf = int(data['total_flights'])
        if tf < 0:
            return False, "total_flights must be >= 0"
    except (ValueError, TypeError):
        return False, "total_flights must be a valid integer"

    return True, None


# Feature Builder
def build_gender_features(data):
    """
    Build feature vector matching classification_model.ipynb training.
    """
    features = {
        'age' : float(data.get('age', 0)),
        'total_flights' : float(data.get('total_flights', 0)),
        'avg_flight_price' : float(data.get('avg_flight_price', 0)),
        'max_flight_price' : float(data.get('max_flight_price', 0)),
        'min_flight_price' : float(data.get('min_flight_price', 0)),
        'std_flight_price' : float(data.get('std_flight_price', 0)),
        'avg_distance' : float(data.get('avg_distance', 0)),
        'firstClass_count' : float(data.get('firstClass_count', 0)),
        'premium_count' : float(data.get('premium_count', 0)),
        'economic_count' : float(data.get('economic_count', 0)),
        'rainbow_count' : float(data.get('rainbow_count', 0)),
        'cloudfy_count' : float(data.get('cloudfy_count', 0)),
        'flyingdrops_count' : float(data.get('flyingdrops_count', 0)),
        'peak_month_bookings' : float(data.get('peak_month_bookings', 0)),
        'firstClass_ratio' : float(data.get('firstClass_ratio', 0)),
        'premium_ratio' : float(data.get('premium_ratio', 0)),
        'economic_ratio' : float(data.get('economic_ratio', 0)),
        'total_hotel_bookings' : float(data.get('total_hotel_bookings', 0)),
        'avg_hotel_price' : float(data.get('avg_hotel_price', 0)),
        'avg_stay_days' : float(data.get('avg_stay_days', 0)),
        'avg_total_spend' : float(data.get('avg_total_spend', 0)),
        'max_total_spend' : float(data.get('max_total_spend', 0)),
        # Company one-hot
        'company_4You' : 1 if data.get('company') == '4You' else 0,
        'company_Acme Factory' : 1 if data.get('company') == 'Acme Factory' else 0,
        'company_Monsters CYA' : 1 if data.get('company') == 'Monsters CYA' else 0,
        'company_Umbrella LTDA' : 1 if data.get('company') == 'Umbrella LTDA' else 0,
        'company_Wonka Company': 1 if data.get('company') == 'Wonka Company' else 0,
    }

    input_df = pd.DataFrame([features])[clf_columns]
    input_scaled = clf_scaler.transform(input_df)
    return input_scaled


# Main Predict Function
def predict_gender(data):
    """
    Predict gender from user travel behaviour features.
    """
    is_valid, error_msg = validate_gender_input(data)
    if not is_valid:
        return {'success': False, 'error': error_msg}

    input_scaled = build_gender_features(data)

    pred_enc = clf_model.predict(input_scaled)[0]
    pred_label = clf_label_enc.inverse_transform([pred_enc])[0]
    proba = clf_model.predict_proba(input_scaled)[0]
    proba_dict = {
        clf_label_enc.classes_[i]: round(float(p), 4)
        for i, p in enumerate(proba)
    }

    return {
        'success' : True,
        'predicted_gender' : pred_label,
        'probabilities' : proba_dict,
        'model_info' : {
            'model_type' : 'Logistic Regression (Tuned)',
            'accuracy' : 0.4030,
            'f1_macro' : 0.4036,
            'note' : 'Gender has weak signal in travel data — +6.97% above random baseline'
        }
    }