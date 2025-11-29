import requests
import csv
import time
import pandas as pd
import os
from datetime import datetime
import numpy as np
import json

API_URL = 'http://localhost:8000/predict'

LATENCY_LOG = 'Logs/latency_log.csv'
ERROR_LOG = 'Logs/error_log.csv'
DRIFT_LOG = 'Logs/drift_log.csv'
TRAINING_STATS_PATH = "processed_data.csv"

def initialize_log_files():
    # Create logs directory if it doesn't exist
    os.makedirs('Logs', exist_ok=True)
    
    for log_file in [LATENCY_LOG, ERROR_LOG, DRIFT_LOG]:
        # Check if file doesn't exist OR if it exists but is empty
        if not os.path.exists(log_file) or (os.path.exists(log_file) and os.path.getsize(log_file) == 0):
            if log_file == LATENCY_LOG:
                log_to_csv(log_file, ['Date', 'Latency_ms', 'Status_Code'])
            elif log_file == ERROR_LOG:
                log_to_csv(log_file, ['Date', 'Actual', 'Predicted', 'MAPE'])
            else:  # DRIFT_LOG
                log_to_csv(log_file, ['Date', 'Drift_Results'])
            print(f"Initialized {log_file}")
        else:
            print(f"{log_file} already exists and has data")
def load_training_stats():
    """Load training statistics only once."""
    if not os.path.exists(TRAINING_STATS_PATH):
        print("Training stats file not found:", TRAINING_STATS_PATH)
        return None
    
    df = pd.read_csv(TRAINING_STATS_PATH)

    stats = {
        "unit_sales_mean": df["unit_sales"].mean(),
        "unit_sales_std": df["unit_sales"].std(),
        "onpromotion_mean": df["onpromotion"].mean(),
        "onpromotion_std": df["onpromotion"].std(),
    }
    return stats

TRAIN_STATS = load_training_stats()

LATENCY_THRESHOLD_MS = 1000
ERROR_THRESHOLD_PERCENT = 5   # example: MAPE > 5% triggers alert
DRIFT_THRESHOLD = 0.5       # mean difference tolerance

def log_to_csv(filename, row):
    initialize_log_files()
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def alert(msg):
    print(f"[Alert] {msg}")
    log_to_csv("Logs/alerts.log", [datetime.now(), msg])


# API health check
def check_api_health(payload):
    start = time.time()
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        latency_ms = (time.time() - start) * 1000

        log_to_csv(LATENCY_LOG, [datetime.now(), latency_ms, response.status_code])

        if latency_ms > LATENCY_THRESHOLD_MS:
            alert(f"High API latency detected: {latency_ms:.2f} ms")

        return response.json(), latency_ms
    except Exception as e:
        alert(f"API health check failed: {e}")
        return None, None
    
# Prediction Error Monitoring
def monitor_prediction_error(actual, predicted):
    if actual == 0:
        return 0
    # calculate MAPE (mean absolute percentage error)
    mape = abs((actual - predicted) / actual) * 100
    log_to_csv(ERROR_LOG, [datetime.now(), actual, predicted, mape])

    if mape > ERROR_THRESHOLD_PERCENT:
        print(f"[ALERT] High MAPE detected: {mape:.2f}%")
        alert(f"High prediction error detected: MAPE = {mape:.2f}%")

    return mape

# Data drift Monitoring
def detect_data_drift(input_row):
    """Check input features drift using training stats."""
    drift_results = {}
    drift_alerts = []

    for feature in ["unit_sales", "onpromotion"]:
        if feature not in TRAIN_STATS:
            continue
        
        train_mean = TRAIN_STATS[f"{feature}_mean"]
        new_value = input_row.get(feature)

        if new_value is None:
            continue

        diff = abs(new_value - train_mean)
        drift_results[feature] = diff

        if diff > DRIFT_THRESHOLD:
            drift_alerts.append(f"Drift in {feature}: diff={diff:.3f}")
            alert(f"Drift detected in {feature} — diff: {diff:.3f}")

    log_to_csv(DRIFT_LOG, [datetime.now(), json.dumps(drift_results)])

    return drift_alerts


if __name__ == "__main__":

    initialize_log_files()

    sample_payload = {
        "store_nbr": 1.0,
        "item_nbr": 103665.0,
        "unit_sales": 7.0,
        "onpromotion": 0.0,
        "day": 16,
        "month": 8,
        "dayofweek": 1,
        "week": 33,
        "family_encoded": 13,
        "city_encoded": 5,
        "state_encoded": 11,
        "type_encoded": 0,
        "is_outlier": 0,
        "is_return": 0,
        "holiday": 0,
        "year": 2013,
        "is_weekend": 0
    }

    result, latency = check_api_health(sample_payload)

    if result:
        print(f"API OK — Latency {latency:.2f} ms")
        print(f"Prediction: {result}")

        predicted_value = result.get("predicted_sales", None)

        actual_value = None  # Replace with real values when available

        if actual_value is not None:
            mape = monitor_prediction_error(actual_value, predicted_value)
            print("MAPE:", mape)
        
        new_data_stats = {
            "unit_sales_log": np.random.uniform(2, 4),  
            "onpromotion": np.random.uniform(0, 1)
        }

        drift_detected, drift_details = detect_data_drift(new_data_stats)
        print("Drift:", drift_details)

    else:
        print("API not reachable. Check backend service.")


    print("✔ Monitoring cycle complete.")
