import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib

# ===== GENERATE TRAINING DATA =====
np.random.seed(42)

data = []
for _ in range(1000):
    temp = np.random.randint(20, 40)
    humidity = np.random.randint(50, 90)
    gas = np.random.randint(100, 600)

    # STATUS LABEL
    if gas > 400 or temp > 32:
        status = 2   # DANGER
    elif gas > 250 or humidity > 75:
        status = 1   # WARNING
    else:
        status = 0   # SAFE

    # SHELF LIFE (REGRESSION TARGET)
    shelf = max(10, 120 - (gas * 0.15) - (temp * 0.5))

    data.append([temp, humidity, gas, status, shelf])

df = pd.DataFrame(data, columns=["temp","humidity","gas","status","shelf"])

X = df[["temp","humidity","gas"]]
y_class = df["status"]
y_reg = df["shelf"]

# ===== MODELS =====
clf = RandomForestClassifier(n_estimators=100)
reg = RandomForestRegressor(n_estimators=100)

clf.fit(X, y_class)
reg.fit(X, y_reg)

# ===== SAVE =====
joblib.dump(clf, "classifier.pkl")
joblib.dump(reg, "regressor.pkl")

print("✅ Models trained and saved")