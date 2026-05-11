from fastapi import FastAPI
from pydantic import BaseModel

import numpy as np
import pandas as pd
import joblib
import os

from tensorflow.keras.models import load_model

# =========================
# DEBUG FILES
# =========================

print("Current Files:")
print(os.listdir())

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

# =========================
# LOAD MODEL + SCALER
# =========================

try:

    print("Loading model...")

    model = load_model("aqi_lstm_model.h5")

    print("Model loaded successfully")

except Exception as e:

    print("MODEL ERROR:", e)

try:

    print("Loading scaler...")

    scaler = joblib.load("scaler.pkl")

    print("Scaler loaded successfully")

except Exception as e:

    print("SCALER ERROR:", e)

# =========================
# MEMORY BUFFER
# =========================

sequence = []

SEQUENCE_LENGTH = 24

# =========================
# LATEST DATA STORAGE
# =========================

latest_data = {}

# =========================
# INPUT MODEL
# =========================

class SensorData(BaseModel):

    temperature: float
    humidity: float
    dust: float
    mq135: float
    mq2: float

# =========================
# HOME ROUTE
# =========================

@app.get("/")
def home():

    return {
        "message": "AQI Prediction API Running"
    }

# =========================
# LATEST DATA ROUTE
# =========================

@app.get("/latest")
def latest():

    return latest_data

# =========================
# PREDICT ROUTE
# =========================

@app.post("/predict")
def predict(data: SensorData):

    global sequence
    global latest_data

    try:

        # =========================
        # CREATE FEATURE DATAFRAME
        # =========================

        features = pd.DataFrame([{

            "pm": data.dust,

            "MQ135": data.mq135,

            "co": data.mq2,

            "temperature": data.temperature,

            "humidity": data.humidity,

            "aqi": 0
        }])

        # =========================
        # NORMALIZE
        # =========================

        scaled = scaler.transform(features)

        # =========================
        # STORE SEQUENCE
        # =========================

        sequence.append(scaled[0])

        # Keep latest 24 readings only
        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

        # =========================
        # WARM-UP PERIOD
        # =========================

        if len(sequence) < SEQUENCE_LENGTH:

            latest_data = {

                "status": "warming_up",

                "samples_collected": len(sequence),

                "temperature": data.temperature,

                "humidity": data.humidity,

                "dust": data.dust,

                "mq135": data.mq135,

                "mq2": data.mq2,

                "current_aqi": 0,

                "future_aqi": 0
            }

            return latest_data

        # =========================
        # PREPARE LSTM INPUT
        # =========================

        seq = np.array(sequence).reshape(
            1,
            SEQUENCE_LENGTH,
            6
        )

        # =========================
        # PREDICT
        # =========================

        prediction = model.predict(seq)

        # =========================
        # INVERSE SCALING
        # =========================

        dummy = np.zeros((1, 6))

        dummy[0, 5] = prediction[0][0]

        inverse = scaler.inverse_transform(dummy)

        future_aqi = float(inverse[0, 5])

        # =========================
        # CURRENT AQI ESTIMATION
        # =========================

        current_aqi = future_aqi * 0.9

        # =========================
        # STORE LATEST DATA
        # =========================

        latest_data = {

            "status": "success",

            "temperature": data.temperature,

            "humidity": data.humidity,

            "dust": data.dust,

            "mq135": data.mq135,

            "mq2": data.mq2,

            "current_aqi": round(current_aqi, 2),

            "future_aqi": round(future_aqi, 2)
        }

        # =========================
        # RETURN RESPONSE
        # =========================

        return latest_data

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)
        }