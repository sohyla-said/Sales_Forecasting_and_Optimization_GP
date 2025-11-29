import mlflow.pyfunc 
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
from Model_Monitoring.monitor import detect_data_drift, monitor_prediction_error, check_api_health

MODEL_PATH = os.getenv("MODEL_PATH", "exported_model/model") 

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Sales Forecasting API", "status": "running", "docs": "/docs"}

class PredictionInput(BaseModel):
    store_nbr: float
    item_nbr: float
    unit_sales: float
    onpromotion: float
    day: int
    month: int
    dayofweek: int
    week: int
    family_encoded: int
    city_encoded: int
    state_encoded: int
    type_encoded: int
    is_outlier: int
    is_return: int
    holiday: int
    year: int
    is_weekend: int
    
try:
    forecasting_model = mlflow.pyfunc.load_model(MODEL_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    forecasting_model = None

@app.post("/predict")
def predict_sales(data: PredictionInput):
    if forecasting_model is None:
        return {"predicted_sales": None, "status": "error", "message": "Model is not loaded."}
    
    input_df = pd.DataFrame([data.model_dump()])

    log_sales_pred = forecasting_model.predict(input_df)

    original_sales_pred = np.expm1(log_sales_pred)[0]

   
    drift_alerts = detect_data_drift(input_df.iloc[0].to_dict())

    actual_value = None   # replace when true data available
    if actual_value is not None:
        monitor_prediction_error(actual_value, original_sales_pred)

    return {
        "predicted_sales": float(original_sales_pred),
        "status": "success"
    }

    