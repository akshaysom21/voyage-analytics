<div align="center">

# ✈️ Voyage Analytics
### Integrating MLOps in Travel — Productionization of ML Systems

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-29.3-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![MLflow](https://img.shields.io/badge/MLflow-3.11-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)

<br/>

> **A complete end-to-end MLOps project** — from raw travel data to production-deployed machine learning models, served through a Flask REST API, containerized with Docker, orchestrated with Kubernetes, tracked with MLflow, and visualized in a Streamlit web application.

<br/>

[🚀 Live App](#-live-demo) • [📖 Documentation](#-project-structure) • [🛠️ Quick Start](#️-quick-start) • [📊 Model Performance](#-model-performance) • [🐳 Docker](#-docker-deployment) • [☸️ Kubernetes](#️-kubernetes-deployment)

</div>

---

## 📌 Table of Contents

- [Business Context](#-business-context)
- [Project Objectives](#-project-objectives)
- [Dataset Overview](#-dataset-overview)
- [Project Structure](#-project-structure)
- [Model Performance](#-model-performance)
- [Quick Start](#️-quick-start)
- [API Documentation](#-api-documentation)
- [Docker Deployment](#-docker-deployment)
- [Kubernetes Deployment](#️-kubernetes-deployment)
- [MLflow Experiment Tracking](#-mlflow-experiment-tracking)
- [Streamlit Application](#️-streamlit-application)
- [Tech Stack](#-tech-stack)
- [Key MLOps Concepts](#-key-mlops-concepts)

---

## 🏢 Business Context

In the travel and tourism industry, the intersection of data analytics and machine learning presents a significant opportunity to revolutionize how travel experiences are curated and delivered.

This project leverages three interconnected datasets — **users**, **flights**, and **hotels** — to build and deploy sophisticated machine learning models that serve a dual purpose:

1. **Enhance predictive capabilities** in travel-related decision-making
2. **Demonstrate end-to-end MLOps** through hands-on productionization

The goal is not just to build models — it is to take those models all the way from a Jupyter notebook to a live, scalable, production-ready system.

---

## 🎯 Project Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Exploratory Data Analysis on 3 travel datasets | ✅ Complete |
| 2 | Statistical Hypothesis Testing (7 tests) | ✅ Complete |
| 3 | Flight Price Regression Model | ✅ Complete |
| 4 | Gender Classification Model | ✅ Complete |
| 5 | Hybrid Hotel Recommendation System | ✅ Complete |
| 6 | Flask REST API (6 endpoints) | ✅ Complete |
| 7 | Docker Containerization (production hardened) | ✅ Complete |
| 8 | Kubernetes Deployment (2 replicas) | ✅ Complete |
| 9 | MLflow Experiment Tracking (7 runs) | ✅ Complete |
| 10 | Streamlit Web Application (4 pages) | ✅ Complete |

---

## 📊 Dataset Overview

| Dataset | Rows | Columns | Description |
|---------|------|---------|-------------|
| `users.csv` | 1,340 | 5 | User profiles — code, company, name, gender, age |
| `flights.csv` | 271,888 | 10 | Flight records — price, distance, agency, type, date |
| `hotels.csv` | 40,552 | 8 | Hotel bookings — price, stay duration, location, total |

### Key EDA Findings

- **time vs distance** — Perfect correlation of 1.000 → `time` dropped from all models
- **Flight Class Pricing** — firstClass avg $1,293 > premium $964 > economic $658
- **Seasonal Pattern** — October is peak booking month with highest prices
- **Data Quality** — Zero missing values and zero duplicates across all datasets

### Hypothesis Testing Results (α = 0.05)

| Test | Variables | Method | Result |
|------|-----------|--------|--------|
| 1 | Age vs Gender | Kruskal-Wallis | Not Significant |
| 2 | Flight Price vs Gender | Kruskal-Wallis | **Significant** ✓ |
| 3 | Flight Class vs Gender | Chi-Square | **Significant** ✓ |
| 4 | Company vs Gender | Chi-Square | Not Significant |
| 5 | Hotel Spending vs Gender | Kruskal-Wallis | Not Significant |
| 6 | Price vs Flight Class | Kruskal-Wallis | **Significant** ✓ |
| 7 | Price vs Month | Kruskal-Wallis | **Significant** ✓ |

> Shapiro-Wilk normality test confirmed non-normal distribution → Kruskal-Wallis used instead of ANOVA

---

## 📁 Project Structure

```
voyage-analytics/
│
├── 📓 notebooks/
│   ├── eda.ipynb                    # Exploratory Data Analysis
│   ├── hypothesis_testing.ipynb     # Statistical Hypothesis Testing
│   ├── regression_model.ipynb       # Flight Price Regression
│   ├── classification_model.ipynb   # Gender Classification
│   └── recommendation_model.ipynb   # Hotel Recommendation System
│
├── 🌐 app/
│   ├── app.py                       # Flask REST API — 6 endpoints
│   ├── predict.py                   # Regression inference engine
│   ├── predict_gender.py            # Classification inference engine
│   └── test_api.py                  # Automated API test suite (11 tests)
│
├── 🤖 models/
│   ├── flight_price_model.pkl       # Random Forest Regressor (~260MB)
│   ├── scaler.pkl                   # StandardScaler (regression)
│   ├── feature_columns.pkl          # Feature column order (regression)
│   ├── gender_classifier.pkl        # Logistic Regression (classification)
│   ├── gender_label_encoder.pkl     # Label encoder (female/male/none)
│   ├── clf_scaler.pkl               # StandardScaler (classification)
│   ├── clf_feature_columns.pkl      # Feature column order (classification)
│   ├── hotel_similarity.pkl         # Cosine similarity matrix
│   ├── collaborative_matrix.pkl     # SVD predicted ratings
│   ├── user_hotel_matrix.pkl        # User-Hotel interaction matrix
│   ├── user_profiles.pkl            # Enriched user profiles
│   ├── hotel_features.pkl           # Hotel feature matrix
│   └── rec_scaler.pkl               # StandardScaler (recommendation)
│
├── 🐳 docker/
│   ├── Dockerfile                   # Production-hardened container
│   └── docker-compose.yml           # Container orchestration
│
├── ☸️  kubernetes/
│   ├── deployment.yaml              # 2 replicas + security context
│   ├── service.yaml                 # LoadBalancer service
│   └── configmap.yaml               # Environment configuration
│
├── 📊 mlflow_tracking/
│   └── mlflow_experiments.py        # Experiment tracking script
│
├── 🖥️  streamlit_app/
│   └── streamlit_app.py             # 4-page interactive web app
│
├── 📂 data/
│   ├── users.csv
│   ├── flights.csv
│   └── hotels.csv
│
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📈 Model Performance

### 1. Flight Price Regression (Random Forest)

| Metric | Value | Meaning |
|--------|-------|---------|
| **R² Score** | **0.9067** | 90.67% of price variance explained |
| **MAE** | **$61.80** | Average prediction error |
| **RMSE** | **$110.90** | Error with large mistakes penalized |
| Train Size | 217,510 rows (80%) | |
| Test Size | 54,378 rows (20%) | |

**Top Features by Importance:**
```
flightType_encoded  ████████████████████████████████  65%
distance            ████████                           22%
agency_FlyingDrops  ██                                  6%
month               █                                   4%
agency_CloudFy      █                                   3%
```

**GridSearchCV:** 24 combinations × 5-fold CV = **120 model trainings**
Best params: `n_estimators=200, max_depth=20, min_samples_split=2`

---

### 2. Gender Classification (Logistic Regression)

| Metric | Value |
|--------|-------|
| **Accuracy** | **40.30%** |
| **F1 Macro** | **0.4036** |
| **F1 Weighted** | **0.4035** |
| Random Baseline | 33.33% |
| **Improvement** | **+6.97% above random** |

**Classes:** female (33.4%) · male (33.7%) · none (32.8%)

**Best Parameters:** `C=10.0, class_weight=balanced, penalty=l2, solver=saga`

> Note: Low accuracy is expected — hypothesis testing confirmed gender has weak statistical signal in travel data. The model performs significantly above random baseline, which is the scientifically honest result.

---

### 3. Hotel Recommendation (Hybrid SVD + Cosine Similarity)

| Metric | Value |
|--------|-------|
| **Hotel Coverage** | **9/9 (100%)** |
| **Eligible Users** | **934 / 1,310 (71.3%)** |
| **Avg Recommended Price** | **$198.06** |
| SVD Latent Factors | 8 |
| User-Hotel Matrix | 1,310 × 9 |

**Methods:** Content-Based (50%) + Collaborative SVD (50%)

---

## ⚡ Quick Start

### Prerequisites

```bash
Python 3.11+
Docker 20+
Git
```

### 1. Clone the Repository

```bash
git clone https://github.com/akshaysom21/voyage-analytics.git
cd voyage-analytics
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate Model Artifacts

Run the notebooks in order:

```bash
# Regression model
jupyter nbconvert --to notebook --execute notebooks/regression_model.ipynb --inplace

# Classification model
jupyter nbconvert --to notebook --execute notebooks/classification_model.ipynb --inplace

# Recommendation model
jupyter nbconvert --to notebook --execute notebooks/recommendation_model.ipynb --inplace
```

### 4. Run the Flask API

```bash
python app/app.py
```

API will be available at `http://localhost:5000`

### 5. Test the API

```bash
python app/test_api.py
```

Expected output: `RESULTS: 11/11 tests passed`

---

## 🌐 API Documentation

Base URL: `http://localhost:5000`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info and all available endpoints |
| `GET` | `/health` | Health check (used by Docker & Kubernetes) |
| `GET` | `/model/info` | Model metadata and performance metrics |
| `POST` | `/predict` | Single flight price prediction |
| `POST` | `/predict/batch` | Batch flight price predictions |
| `POST` | `/predict/gender` | Gender prediction from travel behaviour |

---

### GET `/health`

```bash
curl http://localhost:5000/health
```

```json
{
  "status": "healthy",
  "timestamp": "2026-05-10T09:30:00.123456",
  "service": "flight-price-prediction-api"
}
```

---

### POST `/predict` — Single Flight Price

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 676.53,
    "flightType": "firstClass",
    "agency": "FlyingDrops",
    "month": 10,
    "day_of_week": 2
  }'
```

```json
{
  "success": true,
  "predicted_price": 1333.50,
  "currency": "USD",
  "input_received": {
    "distance": 676.53,
    "flightType": "firstClass",
    "agency": "FlyingDrops",
    "month": 10,
    "day_of_week": 2
  },
  "model_info": {
    "model_type": "Random Forest Regressor",
    "r2_score": 0.9067,
    "mae": 61.8,
    "rmse": 110.9
  }
}
```

**Accepted values:**
- `distance` — float, > 0 (km)
- `flightType` — `"economic"` | `"premium"` | `"firstClass"`
- `agency` — `"CloudFy"` | `"Rainbow"` | `"FlyingDrops"`
- `month` — integer, 1–12
- `day_of_week` — integer, 0 (Monday) – 6 (Sunday)

---

### POST `/predict/batch` — Batch Predictions

```bash
curl -X POST http://localhost:5000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "flights": [
      {"distance": 676.53, "flightType": "firstClass", "agency": "FlyingDrops", "month": 10, "day_of_week": 2},
      {"distance": 300.00, "flightType": "economic",   "agency": "Rainbow",     "month": 8,  "day_of_week": 1},
      {"distance": 500.00, "flightType": "premium",    "agency": "CloudFy",     "month": 6,  "day_of_week": 4}
    ]
  }'
```

```json
{
  "success": true,
  "total_requested": 3,
  "total_predicted": 3,
  "predictions": [...],
  "summary": {
    "min_price": 520.30,
    "max_price": 1333.50,
    "avg_price": 932.10
  }
}
```

---

### POST `/predict/gender` — Gender Prediction

```bash
curl -X POST http://localhost:5000/predict/gender \
  -H "Content-Type: application/json" \
  -d '{
    "age": 25,
    "company": "4You",
    "total_flights": 50,
    "avg_flight_price": 900.0,
    "firstClass_ratio": 0.4,
    "premium_ratio": 0.3,
    "economic_ratio": 0.3,
    "total_hotel_bookings": 10,
    "avg_hotel_price": 200.0
  }'
```

```json
{
  "success": true,
  "predicted_gender": "female",
  "probabilities": {
    "female": 0.4101,
    "male": 0.1947,
    "none": 0.3952
  },
  "model_info": {
    "model_type": "Logistic Regression (Tuned)",
    "accuracy": 0.4030,
    "f1_macro": 0.4036,
    "note": "Gender has weak signal in travel data — +6.97% above random baseline"
  }
}
```

---

### Error Responses

All errors return consistent JSON:

```json
{
  "success": false,
  "error": "flightType must be one of: ['economic', 'premium', 'firstClass']"
}
```

| Status Code | Meaning |
|-------------|---------|
| `200` | Success |
| `400` | Bad Request — invalid or missing input |
| `404` | Endpoint not found |
| `405` | Method not allowed |
| `500` | Internal server error |

---

## 🐳 Docker Deployment

### Production Hardening Features

- ✅ **Non-root user** — runs as `appuser` (UID 1000), not root
- ✅ **Gunicorn WSGI** — 4 workers, 120s timeout (not Flask dev server)
- ✅ **Layer caching** — requirements copied before code for fast rebuilds
- ✅ **HEALTHCHECK** — Docker monitors `/health` every 30 seconds
- ✅ **Read-only volumes** — models mounted as `:ro`
- ✅ **.dockerignore** — excludes notebooks, CSVs, venvs from image

### Build and Run

```bash
# Build the Docker image
docker build -f docker/Dockerfile -t voyage-analytics:1.0.0 .

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up

# OR run directly
docker run -p 5000:5000 voyage-analytics:1.0.0

# Test the running container
curl http://localhost:5000/health

# Stop
docker-compose -f docker/docker-compose.yml down
```

### Verify the Image

```bash
# Check image size
docker images voyage-analytics

# Check container logs
docker logs voyage-flight-api

# Check health status
docker inspect voyage-flight-api | grep Health
```

---

## ☸️ Kubernetes Deployment

### Manifest Overview

| File | Purpose |
|------|---------|
| `deployment.yaml` | 2 replicas, securityContext, resource limits, probes |
| `service.yaml` | LoadBalancer — port 80 → 5000 |
| `configmap.yaml` | FLASK_ENV, WORKERS=4, TIMEOUT=120 |

### Deploy

```bash
# Apply all manifests
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Verify deployment
kubectl get pods
kubectl get services
kubectl get configmap

# Check pod logs
kubectl logs -l app=voyage-analytics

# Check pod health
kubectl describe pod -l app=voyage-analytics
```

### Expected Output

```bash
$ kubectl get pods
NAME                               READY   STATUS    RESTARTS   AGE
voyage-analytics-7d9f8b6c4-abc12   1/1     Running   0          2m
voyage-analytics-7d9f8b6c4-def34   1/1     Running   0          2m

$ kubectl get services
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)
voyage-analytics-service   LoadBalancer   10.96.128.45    34.123.45.67    80:30521/TCP
```

### Production Features

```yaml
# Security hardening
securityContext:
  runAsNonRoot: true          # Cannot run as root
  runAsUser: 1000             # Matches Dockerfile appuser
  allowPrivilegeEscalation: false  # No privilege escalation

# Resource protection
resources:
  requests:
    memory: "256Mi"           # Minimum guaranteed
    cpu: "250m"               # 0.25 CPU core
  limits:
    memory: "512Mi"           # Maximum allowed
    cpu: "500m"               # 0.5 CPU core

# Zero-downtime deployments
livenessProbe:                # Restart dead containers
  initialDelaySeconds: 20     # Wait for model loading
readinessProbe:               # No traffic until ready
  initialDelaySeconds: 15
```

### Scale Up

```bash
# Scale to 5 replicas
kubectl scale deployment voyage-analytics --replicas=5

# Auto-scale based on CPU
kubectl autoscale deployment voyage-analytics --min=2 --max=10 --cpu-percent=70
```

---

## 📊 MLflow Experiment Tracking

### Run Experiments

```bash
cd voyage-analytics
python mlflow_tracking/mlflow_experiments.py
```

### Launch UI

```bash
python -m mlflow ui --port 5001 \
  --backend-store-uri file:///path/to/voyage-analytics/mlflow_tracking/mlruns
```

Open `http://localhost:5001`

### Tracked Experiments

| Experiment | Runs | Best Metric |
|-----------|------|-------------|
| Flight-Price-Regression | 3 | R²=0.9067 |
| Gender-Classification | 4 | Acc=0.4030, F1=0.4036 |

**Per run MLflow logs:**
- ✅ Parameters — n_estimators, max_depth, C, test_size, features
- ✅ Metrics — R², MAE, RMSE / Accuracy, F1 Weighted, F1 Macro
- ✅ Artifacts — trained model + requirements.txt + MLmodel metadata
- ✅ Metadata — run name, timestamp, duration

---

## 🖥️ Streamlit Application

### Run Locally

```bash
python3 -m streamlit run streamlit_app/streamlit_app.py
```

Open `http://localhost:8501`

### Pages

| Page | Features |
|------|----------|
| 🏠 **Dashboard** | KPI cards, flight type distribution, gender chart, hotel bookings, price by class |
| 🏨 **Hotel Recommendations** | User selector (1,340 users), Hybrid/Content/Collaborative method, price comparison chart |
| 💰 **Flight Price Predictor** | Interactive inputs, real-time prediction, delta vs class average, JSON input summary |
| 📊 **Data Insights** | Tabbed analysis — Flights, Hotels, Users |

### Performance Optimization

```python
@st.cache_resource    # Loads 254MB model ONCE — shared across all users
def load_models():
    ...

@st.cache_data        # Caches DataFrames — no CSV reload on every click
def load_data():
    ...
```

---

## 🛠️ Tech Stack

### Machine Learning
| Library | Version | Use |
|---------|---------|-----|
| scikit-learn | 1.3.2 | Random Forest, Logistic Regression, SVD |
| pandas | 2.1.4 | Data manipulation |
| numpy | 1.26.2 | Numerical operations |
| scipy | latest | SVD, statistical tests |
| joblib | 1.3.2 | Model serialization |

### API & Web
| Tool | Version | Use |
|------|---------|-----|
| Flask | 3.0.0 | REST API framework |
| Gunicorn | 21.2.0 | Production WSGI server |
| Streamlit | 1.57.0 | Interactive web application |

### MLOps
| Tool | Version | Use |
|------|---------|-----|
| MLflow | 3.11.1 | Experiment tracking |
| Docker | 29.3.0 | Containerization |
| Kubernetes | — | Container orchestration |
| Git LFS | 3.7.1 | Large model file storage |

---

## 🔑 Key MLOps Concepts Demonstrated

### 1. Training-Serving Consistency
```python
# feature_columns.pkl enforces exact column order at inference time
input_df = pd.DataFrame([features])[feature_columns]
```
Prevents **training-serving skew** — the #1 cause of silent ML failures in production.

### 2. Layer Caching Optimization
```dockerfile
COPY requirements.txt .          # Rarely changes — cached
RUN pip install -r requirements.txt
COPY app/ ./app/                 # Changes often — only this layer rebuilds
```
Code changes rebuild in seconds, not minutes.

### 3. Zero-Downtime Deployments
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 15        # Wait for model loading
```
New pods receive no traffic until healthy. Old pods serve until new ones are ready.

### 4. Defense in Depth Security
```dockerfile
RUN useradd -m -u 1000 appuser  # Docker level
USER appuser
```
```yaml
securityContext:                  # Kubernetes level
  runAsNonRoot: true
  allowPrivilegeEscalation: false
```

### 5. Configuration Decoupled from Code
```yaml
# configmap.yaml — change without rebuilding image
data:
  FLASK_ENV: "production"
  WORKERS: "4"
  TIMEOUT: "120"
```

### 6. Honest Model Reporting
```
Classification Accuracy: 40.30%
Random Baseline:         33.33%
Improvement:            +6.97%
```
Hypothesis testing confirmed weak gender signal before modeling. Reporting accurately above random baseline is better science than inflating metrics.

---

## 📋 Requirements

```txt
flask==3.0.0
gunicorn==21.2.0
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.26.2
joblib==1.3.2
```

---

## 🚀 Live Demo

The Streamlit application is deployed publicly on Streamlit Cloud.

**Live App:** [voyage-analytics.streamlit.app](https://voyage-analytics.streamlit.app)

---

## 👤 Author

**Akshay Som**
Labmentix Final Project — Productionization of ML Systems

---

## 📄 License

This project is for educational and internship demonstration purposes.

---

<div align="center">

**Built with ❤️ — From Raw Data to Production in One Project**

`EDA` → `Hypothesis Testing` → `3 ML Models` → `Flask API` → `Docker` → `Kubernetes` → `MLflow` → `Streamlit`

</div>
