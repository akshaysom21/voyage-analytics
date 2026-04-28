# Models Directory

This folder stores trained ML model artifacts (generated locally).

## Files Generated After Running Notebooks

| File | Size | Description |
|------|------|-------------|
| `flight_price_model.pkl` | ~260MB | Random Forest Regressor |
| `scaler.pkl` | ~1KB | StandardScaler |
| `feature_columns.pkl` | ~125B | Feature column names |

## Model Performance
- **Algorithm** : Random Forest Regressor
- **R² Score**  : 0.9069
- **MAE**       : $61.78
- **RMSE**      : $110.75

## How to Regenerate Models
```bash
jupyter notebook notebooks/regression_model.ipynb
# Run all cells → models will be saved to this folder