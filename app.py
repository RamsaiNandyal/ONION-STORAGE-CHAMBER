from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import joblib

app = Flask(__name__)

# ===== LOAD ML MODELS =====
clf = joblib.load("classifier.pkl")
reg = joblib.load("regressor.pkl")

# ===== CONNECT MONGODB =====
client = MongoClient("mongodb://localhost:27017/")
db = client["onion_storage"]
collection = db["sensor_data"]

# ===== GLOBAL LIVE DATA =====
latest_data = {
    "temp": 25,
    "humidity": 34,
    "gas": 200,
    "status": 0,
    "alert": "NORMAL",
    "shelf": 120
}

# ===== RECEIVE DATA =====
@app.route('/data', methods=['POST'])
def receive_data():
    global latest_data

    data = request.json
    print("DATA RECEIVED:", data)

    temp = data['temp']
    humidity = data['humidity']
    gas = data['gas']

    # ===== ML PREDICTION =====
    status = int(clf.predict([[temp, humidity, gas]])[0])
    shelf = int(reg.predict([[temp, humidity, gas]])[0])

    # ===== ALERT LOGIC =====
    alert_msg = "NORMAL"

    if status == 2:
        alert_msg = "🚨 CRITICAL CONDITION"
    elif status == 1:
        alert_msg = "⚠ WARNING"
    else:
        alert_msg = "✅ SAFE"

    # ===== UPDATE LIVE DATA (IMPORTANT FIX) =====
    latest_data["temp"] = temp
    latest_data["humidity"] = humidity
    latest_data["gas"] = gas
    latest_data["status"] = status
    latest_data["alert"] = alert_msg
    latest_data["shelf"] = shelf

    # ===== STORE IN MONGODB =====
    record = {
        "temp": temp,
        "humidity": humidity,
        "gas": gas,
        "status": status,
        "alert": alert_msg,
        "shelf": shelf,
        "timestamp": datetime.now()
    }

    collection.insert_one(record)

    return jsonify({"status": status})

# ===== LIVE DATA API =====
@app.route('/live')
def live():
    return jsonify(latest_data)

# ===== HISTORY API =====
@app.route('/history')
def history():
    data = list(collection.find().sort("timestamp", -1).limit(10))
    
    result = []
    for d in data:
        result.append({
            "temp": d["temp"],
            "humidity": d["humidity"],
            "gas": d["gas"],
            "shelf": d.get("shelf", 0)
        })
    
    return jsonify(result[::-1])  # reverse for correct order

# ===== DASHBOARD =====
@app.route('/')
def dashboard():
    return render_template("index.html", **latest_data)

# ===== RUN SERVER =====
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)