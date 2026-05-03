# Models Directory

This folder stores trained ML model artifacts.

## Files

| File | Size | Description |
|------|------|-------------|
| `flight_price_model.pkl` | ~260MB | Random Forest Regressor (flight price) |
| `scaler.pkl` | ~1KB | StandardScaler for regression |
| `feature_columns.pkl` | ~125B | Regression feature column names |
| `gender_classifier.pkl` | ~2KB | Logistic Regression (gender classification) |
| `gender_label_encoder.pkl` | ~1KB | Gender label encoder |
| `clf_scaler.pkl` | ~2KB | StandardScaler for classification |
| `clf_feature_columns.pkl` | ~1KB | Classification feature column names |
| `hotel_similarity.pkl` | ~1KB | Hotel cosine similarity matrix |
| `collaborative_matrix.pkl` | ~50KB | SVD collaborative filtering matrix |
| `user_hotel_matrix.pkl` | ~50KB | User-hotel interaction matrix |
| `user_profiles.pkl` | ~100KB | Enriched user profiles |
| `hotel_features.pkl` | ~1KB | Hotel feature matrix |
| `rec_scaler.pkl` | ~1KB | StandardScaler for recommendation |

## Model Performance

### Regression Model
- **Algorithm** : Random Forest Regressor
- **R² Score**  : 0.9067
- **MAE**       : $61.78
- **RMSE**      : $110.86

### Classification Model
- **Algorithm** : Logistic Regression (Tuned)
- **Accuracy**  : 40.30%
- **F1 Macro**  : 0.4036
- **Note**      : +6.97% above random baseline (33.33%)

### Recommendation Model
- **Approach**  : Hybrid (Content-Based + Collaborative SVD)
- **Coverage**  : 9/9 hotels (100%)
- **Eligible Users** : 934/1310 (71.3%)

## How to Regenerate Models
```bash
# Regression model
jupyter nbconvert --to notebook --execute notebooks/regression_model.ipynb --inplace

# Classification model
jupyter nbconvert --to notebook --execute notebooks/classification_model.ipynb --inplace

# Recommendation model
jupyter nbconvert --to notebook --execute notebooks/recommendation_model.ipynb --inplace
```