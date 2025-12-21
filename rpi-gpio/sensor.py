import os
import config
from datetime import datetime
import random

DT_LOG_FORMAT = "%Y-%m-%d %H:%M:%S"

#USE_DUMMY = os.getenv("DUMMY_SENSOR", "false").lower() == "true"
#USE_DUMMY = bool(config.DUMMY_SENSOR)
USE_DUMMY = os.getenv("DUMMY_SENSOR", str(config.DUMMY_SENSOR)).lower() == "true"
DT_LOG_FORMAT = config.log_date_format


if not USE_DUMMY:
    try:
        import bme280
        import smbus2

        port = 1
        address = 0x76
        bus = smbus2.SMBus(port)
        bme280.load_calibration_params(bus, address)

        def read():
            data = bme280.sample(bus, address)
            return {
                "temperature": round(data.temperature, 2),
                "humidity": round(data.humidity, 2),
                "pressure": round(data.pressure, 2),
                "timestamp": datetime.now().strftime(DT_LOG_FORMAT),
            }

    except Exception as e:
        print(f"[WARN] Falling back to dummy sensor: {e}")
        USE_DUMMY = True


if USE_DUMMY:
    # Dummy sensor behaves realistically
    def read():
        return {
            "temperature": round(18 + random.uniform(-1.5, 1.5), 2),
            "humidity": round(50 + random.uniform(-5, 5), 2),
            "pressure": round(1013 + random.uniform(-8, 8), 2),
            "timestamp": datetime.now().strftime(DT_LOG_FORMAT),
        }

