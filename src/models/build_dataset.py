# build_dataset.py
# Combines flights.csv, hotels.csv, and users.csv into one processed_data.csv

import os
import pandas as pd


# ==============================
# PATH SETUP
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

FLIGHTS_PATH = os.path.join(DATA_DIR, "flights.csv")
HOTELS_PATH = os.path.join(DATA_DIR, "hotels.csv")
USERS_PATH = os.path.join(DATA_DIR, "users.csv")

OUTPUT_PATH = os.path.join(PROCESSED_DIR, "processed_data.csv")


# ==============================
# LOAD CSV FILES
# ==============================

flights = pd.read_csv(FLIGHTS_PATH)
hotels = pd.read_csv(HOTELS_PATH)
users = pd.read_csv(USERS_PATH)


# ==============================
# RENAME USER KEY FOR MERGING
# ==============================

# users.csv has column: code
# flights.csv and hotels.csv have column: userCode
# So we rename code -> userCode
users = users.rename(columns={"code": "userCode"})


# ==============================
# PREFIX COLUMNS TO AVOID DUPLICATES
# ==============================

flights = flights.rename(
    columns={
        "travelCode": "travelCode",
        "userCode": "userCode",
        "from": "flight_from",
        "to": "flight_to",
        "flightType": "flight_type",
        "price": "flight_price",
        "time": "flight_time",
        "distance": "flight_distance",
        "agency": "flight_agency",
        "date": "flight_date"
    }
)

hotels = hotels.rename(
    columns={
        "travelCode": "travelCode",
        "userCode": "userCode",
        "name": "hotel_name",
        "place": "hotel_place",
        "days": "hotel_days",
        "price": "hotel_price",
        "total": "hotel_total",
        "date": "hotel_date"
    }
)

users = users.rename(
    columns={
        "company": "user_company",
        "name": "user_name",
        "gender": "user_gender",
        "age": "user_age"
    }
)


# ==============================
# MERGE FLIGHTS AND HOTELS
# ==============================

# flights and hotels share:
# travelCode
# userCode
# date is not always same, so we merge mainly on travelCode and userCode

travel_data = pd.merge(
    flights,
    hotels,
    on=["travelCode", "userCode"],
    how="outer"
)


# ==============================
# MERGE WITH USERS
# ==============================

processed_data = pd.merge(
    travel_data,
    users,
    on="userCode",
    how="left"
)


# ==============================
# FEATURE ENGINEERING
# ==============================

# Total trip cost = flight price + hotel total
processed_data["total_trip_cost"] = (
    pd.to_numeric(processed_data["flight_price"], errors="coerce").fillna(0)
    + pd.to_numeric(processed_data["hotel_total"], errors="coerce").fillna(0)
)

# Classification target example:
# classify customer trip type based on total trip cost
processed_data["trip_cost_category"] = pd.cut(
    processed_data["total_trip_cost"],
    bins=[-1, 1000, 2500, float("inf")],
    labels=["low_cost", "medium_cost", "high_cost"]
)

# Regression target example:
# total_trip_cost can be used as regression target


# ==============================
# CLEAN FINAL DATA
# ==============================

processed_data = processed_data.drop_duplicates()

# Fill numeric columns with 0
numeric_cols = processed_data.select_dtypes(include=["int64", "float64"]).columns
processed_data[numeric_cols] = processed_data[numeric_cols].fillna(0)

# Fill object columns with 'unknown'
object_cols = processed_data.select_dtypes(include=["object"]).columns
processed_data[object_cols] = processed_data[object_cols].fillna("unknown")

# Fix categorical column separately
if "trip_cost_category" in processed_data.columns:
    processed_data["trip_cost_category"] = processed_data["trip_cost_category"].astype(str)
    processed_data["trip_cost_category"] = processed_data["trip_cost_category"].fillna("unknown")


# ==============================
# SAVE FINAL CSV
# ==============================

processed_data.to_csv(OUTPUT_PATH, index=False)

print("Processed dataset created successfully.")
print("Saved at:", OUTPUT_PATH)
print("Final shape:", processed_data.shape)
print("Columns:")
print(processed_data.columns.tolist())