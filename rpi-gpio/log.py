import threading
from time import sleep
from datetime import datetime

import bme280
import smbus2
import config
from flask import Flask, jsonify

port = 1
address = 0x76
bus = smbus2.SMBus(port)
bme280.load_calibration_params(bus, address)

delay = config.delay
DT_LOG_FORMAT = config.log_date_format

app = Flask(__name__)

# Global shared sample
latest_sample = {
    "temperature": None,
    "humidity": None,
    "pressure": None,
    "timestamp": None,
}

def log_loop():
    while True:
        sample = bme280.sample(bus, address)
        humidity = round(float(sample.humidity), 2)
        pressure = round(float(sample.pressure), 2)
        temp = round(float(sample.temperature), 2)
        date = datetime.now().strftime(DT_LOG_FORMAT)

        # Update shared latest_sample
        latest_sample.update({
            "temperature": temp,
            "humidity": humidity,
            "pressure": pressure,
            "timestamp": date,
        })

        # Write to file
        print(f"[{date}] {temp} {humidity} {pressure}")
        with open("/data-log/hpt.log", "+a") as f:
            f.write(f"[{date}] {temp} {humidity} {pressure}\n")
        sleep(delay)

@app.route("/current", methods=["GET"])
def get_current():
    if latest_sample["temperature"] is None:
        return jsonify({"error": "Sensor data not yet available"}), 503
    return jsonify(latest_sample)

if __name__ == "__main__":
    t = threading.Thread(target=log_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)

