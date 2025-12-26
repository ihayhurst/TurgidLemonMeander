from time import sleep
from sensor import read
import threading
from flask import Flask, jasonify
import config


delay = config.delay
DT_LOG_FORMAT = config.log_date_format
app = Flask(__name__)

latest_sample = {
        "temperature": None,
        "humidity": None,
        "pressure": None,
        "timestamp": None.
        }

while True:
    sample = read()
    print(f"[{sample['timestamp']}] "
          f"{sample['temperature']} "
          f"{sample['humidity']} "
          f"{sample['pressure']}")

    lastest_sample.update({
        "temperature": sample['temperature'],
        "humidity": sample['humidity'],
        "pressure": sample['pressure'],
        "timestamp': sample['timestamp'],
        })
    
    with open("/data-log/hpt.log", "+a") as f:
        f.write(f"[{sample['timestamp']}] "
                f"{sample['temperature']} "
                f"{sample['humidity']} "
                f"{sample['pressure']}\n")

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
