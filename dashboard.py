import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Live AQI Dashboard",
    layout="wide"
)

st.title("🌍 Smart AQI Monitoring Dashboard")

# =========================
# FASTAPI URL
# =========================

API_URL = "http://127.0.0.1:8000/latest"

# =========================
# SESSION STORAGE
# =========================

if "history" not in st.session_state:

    st.session_state.history = []

# =========================
# FETCH DATA
# =========================

try:

    response = requests.get(API_URL)

    data = response.json()

except Exception as e:

    st.error(f"Server Error: {e}")

    st.stop()

# =========================
# STORE HISTORY
# =========================

if data:

    st.session_state.history.append({

        "time": datetime.now().strftime("%H:%M:%S"),

        "temperature": data.get("temperature", 0),

        "humidity": data.get("humidity", 0),

        "dust": data.get("dust", 0),

        "mq135": data.get("mq135", 0),

        "mq2": data.get("mq2", 0),

        "current_aqi": data.get("current_aqi", 0),

        "future_aqi": data.get("future_aqi", 0)
    })

# =========================
# AQI CATEGORY
# =========================

current_aqi = data.get("current_aqi", 0)

if current_aqi <= 50:
    category = "Good"

elif current_aqi <= 100:
    category = "Satisfactory"

elif current_aqi <= 200:
    category = "Moderate"

elif current_aqi <= 300:
    category = "Poor"

elif current_aqi <= 400:
    category = "Very Poor"

else:
    category = "Severe"

# =========================
# TOP METRICS
# =========================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Current AQI",
    round(current_aqi, 2)
)

col2.metric(
    "Future AQI (1H)",
    round(data.get("future_aqi", 0), 2)
)

col3.metric(
    "AQI Category",
    category
)

# =========================
# SENSOR CARDS
# =========================

st.subheader("📡 Live Sensor Readings")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Temperature",
    f'{data.get("temperature", 0)} °C'
)

c2.metric(
    "Humidity",
    f'{data.get("humidity", 0)} %'
)

c3.metric(
    "Dust",
    round(data.get("dust", 0), 2)
)

c4.metric(
    "MQ135",
    round(data.get("mq135", 0), 2)
)

c5.metric(
    "MQ2",
    round(data.get("mq2", 0), 2)
)

# =========================
# DATAFRAME
# =========================

history_df = pd.DataFrame(
    st.session_state.history
)

# =========================
# AQI CHART
# =========================

st.subheader("📈 AQI Trend")

fig = px.line(

    history_df,

    x="time",

    y=["current_aqi", "future_aqi"],

    markers=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# SENSOR TREND
# =========================

st.subheader("📊 Sensor Trends")

sensor_fig = px.line(

    history_df,

    x="time",

    y=[
        "temperature",
        "humidity",
        "dust",
        "mq135",
        "mq2"
    ],

    markers=True
)

st.plotly_chart(
    sensor_fig,
    use_container_width=True
)

# =========================
# LIVE TABLE
# =========================

st.subheader("🧾 Recent Readings")

st.dataframe(
    history_df.tail(10),
    use_container_width=True
)

# =========================
# AUTO REFRESH
# =========================

st.caption("Refreshing every 2 seconds...")

time.sleep(2)

st.rerun()