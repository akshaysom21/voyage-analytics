# ============================================================
# VOYAGE ANALYTICS - API TESTS
# app/test_api.py
# ============================================================

import requests
import json

BASE_URL = "http://localhost:5000"

def print_result(test_name, response, passed):
    status = "PASSED" if passed else "FAILED"
    print(f"\n{'='*55}")
    print(f"TEST : {test_name}")
    print(f"CODE : {response.status_code}")
    print(f"BODY : {json.dumps(response.json(), indent=2)}")
    print(f"{status}")
    print('='*55)


def test_home():
    r = requests.get(f"{BASE_URL}/")
    passed = r.status_code == 200
    print_result("Home / Root", r, passed)


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    passed = (r.status_code == 200 and
              r.json()['status'] == 'healthy')
    print_result("Health Check", r, passed)


def test_model_info():
    r = requests.get(f"{BASE_URL}/model/info")
    passed = r.status_code == 200
    print_result("Model Info", r, passed)


def test_predict_firstclass():
    payload = {
        "distance" : 676.53,
        "flightType" : "firstClass",
        "agency" : "FlyingDrops",
        "month" : 10,
        "day_of_week" : 2
    }
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    passed = (r.status_code == 200 and
              r.json()['success'] == True and
              r.json()['predicted_price'] > 0)
    print_result("Predict - First Class", r, passed)


def test_predict_economic():
    payload = {
        "distance" : 300.00,
        "flightType" : "economic",
        "agency" : "Rainbow",
        "month" : 8,
        "day_of_week" : 1
    }
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    passed = (r.status_code == 200 and
              r.json()['success'] == True)
    print_result("Predict - Economic", r, passed)


def test_predict_premium():
    payload = {
        "distance" : 500.00,
        "flightType" : "premium",
        "agency" : "CloudFy",
        "month" : 6,
        "day_of_week" : 4
    }
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    passed = (r.status_code == 200 and
              r.json()['success'] == True)
    print_result("Predict - Premium", r, passed)


def test_batch_predict():
    payload = {
        "flights": [
            {"distance": 676.53, "flightType": "firstClass",
             "agency": "FlyingDrops", "month": 10, "day_of_week": 2},
            {"distance": 300.00, "flightType": "economic",
             "agency": "Rainbow", "month": 8, "day_of_week": 1},
            {"distance": 500.00, "flightType": "premium",
             "agency": "CloudFy", "month": 6, "day_of_week": 4}
        ]
    }
    r = requests.post(f"{BASE_URL}/predict/batch", json=payload)
    passed = (r.status_code == 200 and
              r.json()['total_predicted'] == 3)
    print_result("Batch Predict - 3 Flights", r, passed)


def test_batch_with_invalid():
    payload = {
        "flights": [
            {"distance": 676.53, "flightType": "firstClass",
             "agency": "FlyingDrops", "month": 10, "day_of_week": 2},
            {"distance": 300.00, "flightType": "business",  # INVALID
             "agency": "Rainbow", "month": 8, "day_of_week": 1}
        ]
    }
    r = requests.post(f"{BASE_URL}/predict/batch", json=payload)
    passed = (r.status_code == 200 and
              r.json()['total_predicted'] == 1)  # only 1 should succeed
    print_result("Batch with one invalid flight", r, passed)


def test_invalid_flight_type():
    payload = {
        "distance" : 500.00,
        "flightType" : "business",   # INVALID
        "agency" : "CloudFy",
        "month" : 6,
        "day_of_week" : 4
    }
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    passed = (r.status_code == 400 and
              r.json()['success'] == False)
    print_result("Invalid flightType (should fail)", r, passed)


def test_missing_field():
    payload = {
        "distance" : 500.00,
        "flightType" : "premium"
        # missing agency, month, day_of_week
    }
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    passed = (r.status_code == 400 and
              r.json()['success'] == False)
    print_result("Missing Fields (should fail)", r, passed)


def test_404():
    r = requests.get(f"{BASE_URL}/nonexistent")
    passed = r.status_code == 404
    print_result("404 Not Found", r, passed)


# Run All Tests
if __name__ == '__main__':
    print("\nVOYAGE ANALYTICS - API TEST SUITE")
    print("Ensure Flask is running: python app/app.py\n")

    tests = [
        test_home,
        test_health,
        test_model_info,
        test_predict_firstclass,
        test_predict_economic,
        test_predict_premium,
        test_batch_predict,
        test_invalid_flight_type,
        test_missing_field,
        test_404,
    ]

    passed_count = 0
    for test in tests:
        try:
            test()
            passed_count += 1
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")

    print(f"\n{'='*55}")
    print(f"RESULTS: {passed_count}/{len(tests)} tests passed")
    print(f"{'='*55}")