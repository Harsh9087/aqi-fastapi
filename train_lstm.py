import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout

# =========================
# LOAD DATASET
# =========================

file_path = "./Dataset/cleaned_dataset.csv"
df = pd.read_csv(file_path)
   
print(df.head())

# =========================
# CREATE DATETIME
# =========================

df['datetime'] = pd.to_datetime(
    df['date'] + ' ' + df['time']
)

# Sort properly
df = df.sort_values('datetime')

# =========================
# SELECT FEATURES
# =========================

features = [
    'pm',
    'MQ135',
    'co',
    'temperature',
    'humidity',
    'aqi'
]

data = df[features]

# =========================
# NORMALIZE
# =========================

scaler = MinMaxScaler()

scaled_data = scaler.fit_transform(data)

# Save scaler
joblib.dump(scaler, "scaler.pkl")

print("Scaler saved")

# =========================
# CREATE SEQUENCES
# =========================

X = []
y = []

SEQUENCE_LENGTH = 24

for i in range(SEQUENCE_LENGTH, len(scaled_data)):

    X.append(       
        scaled_data[i-SEQUENCE_LENGTH:i]
    )

    # Predict AQI
    y.append(
        scaled_data[i, 5]
    )

X = np.array(X)
y = np.array(y)

print("X Shape:", X.shape)
print("Y Shape:", y.shape)

# =========================
# TRAIN TEST SPLIT
# =========================

split = int(0.8 * len(X))

X_train = X[:split]
X_test = X[split:]

y_train = y[:split]
y_test = y[split:]

# =========================
# BUILD MODEL
# =========================

model = Sequential()

model.add(
    LSTM(
        64,
        return_sequences=True,
        input_shape=(
            X_train.shape[1],
            X_train.shape[2]
        )
    )
)

model.add(Dropout(0.2))

model.add(
    LSTM(64)
)

model.add(Dropout(0.2))

model.add(Dense(1))

# =========================
# COMPILE
# =========================

model.compile(
    optimizer='adam',
    loss='mean_squared_error',
    metrics=['mae']
)

# =========================
# TRAIN
# =========================

history = model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test)
)

# =========================
# SAVE MODEL
# =========================

model.save("aqi_lstm_model.h5")

print("Model Saved")