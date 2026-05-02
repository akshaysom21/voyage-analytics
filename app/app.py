# ============================================================
# VOYAGE ANALYTICS - FLASK REST API
# app/app.py
# ============================================================

from flask import Flask, request, jsonify
from predict import predict_price
import datetime

# Initialize App 
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# Root Route
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'api' : 'Voyage Analytics - Flight Price Prediction API',
        'version' : '1.0.0',
        'status' : 'running',
        'author' : 'Akshay Som',
        'endpoints' : {
            'GET /' : 'API info',
            'GET /health' : 'Health check',
            'GET /model/info' : 'Model metadata',
            'POST /predict' : 'Single flight price prediction',
            'POST /predict/batch' : 'Batch flight price predictions'
        }
    }), 200


# Health Check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status' : 'healthy',
        'timestamp' : datetime.datetime.now().isoformat(),
        'service' : 'flight-price-prediction-api'
    }), 200


# Model Info
@app.route('/model/info', methods=['GET'])
def model_info():
    return jsonify({
        'model_name' : 'Flight Price Regression Model',
        'model_type' : 'Random Forest Regressor',
        'version' : '1.0.0',
        'performance' : {
            'r2_score' : 0.9069,
            'mae' : 61.78,
            'rmse' : 110.75
        },
        'features' : [
            'distance - Route distance in km',
            'flightType - economic / premium / firstClass',
            'agency - CloudFy / Rainbow / FlyingDrops',
            'month - 1 to 12',
            'day_of_week - 0 (Monday) to 6 (Sunday)'
        ],
        'training_data' : {
            'dataset' : 'flights.csv',
            'total_rows' : 271888,
            'train_rows' : 217510,
            'test_rows' : 54378
        }
    }), 200


# Single Prediction
@app.route('/predict', methods=['POST'])
def predict():
    """
    Single flight price prediction.

    Request Body (JSON):
    {
        "distance" : 676.53,
        "flightType" : "firstClass",
        "agency" : "FlyingDrops",
        "month" : 10,
        "day_of_week" : 2
    }
    """
    if not request.is_json:
        return jsonify({
            'success' : False,
            'error' : 'Content-Type must be application/json'
        }), 400

    data = request.get_json()

    if not data:
        return jsonify({
            'success' : False,
            'error' : 'Request body is empty'
        }), 400

    result = predict_price(data)

    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


# Batch Prediction
@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Batch flight price predictions.

    Request Body (JSON):
    {
        "flights": [
            {"distance": 676.53, "flightType": "firstClass",
             "agency": "FlyingDrops", "month": 10, "day_of_week": 2},
            {"distance": 300.00, "flightType": "economic",
             "agency": "Rainbow", "month": 8, "day_of_week": 1}
        ]
    }
    """
    if not request.is_json:
        return jsonify({
            'success': False,
            'error' : 'Content-Type must be application/json'
        }), 400

    data = request.get_json()

    if 'flights' not in data:
        return jsonify({
            'success': False,
            'error'  : "Request must contain a 'flights' list"
        }), 400

    flights_list = data['flights']

    if not isinstance(flights_list, list) or len(flights_list) == 0:
        return jsonify({
            'success': False,
            'error'  : "'flights' must be a non-empty list"
        }), 400

    # Predict each flight
    results = []
    for i, flight in enumerate(flights_list):
        result = predict_price(flight)
        result['index'] = i
        results.append(result)

    # Summary stats
    successful = [r for r in results if r['success']]
    prices = [r['predicted_price'] for r in successful]

    return jsonify({
        'success': True,
        'total_requested': len(flights_list),
        'total_predicted': len(successful),
        'predictions': results,
        'summary': {
            'min_price': round(min(prices), 2) if prices else None,
            'max_price': round(max(prices), 2) if prices else None,
            'avg_price': round(sum(prices) / len(prices), 2) if prices else None
        }
    }), 200


# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'hint': 'Visit GET / to see all available endpoints'
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        'success': False,
        'error': 'Method not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# Run
if __name__ == '__main__':
    print("=" * 55)
    print("  VOYAGE ANALYTICS - FLIGHT PRICE PREDICTION API")
    print("=" * 55)
    print("  GET  http://localhost:5000/")
    print("  GET  http://localhost:5000/health")
    print("  GET  http://localhost:5000/model/info")
    print("  POST http://localhost:5000/predict")
    print("  POST http://localhost:5000/predict/batch")
    print("=" * 55)

    app.run(host='0.0.0.0', port=5000, debug=True)