import bme280
import smbus2
from time import sleep
from datetime import datetime
import config

port = 1
address = 0x76 #BME280 address.
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)
delay = config.delay
DT_LOG_FORMAT = config.log_date_format

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = round(float(bme280_data.humidity), 2)
    pressure  = round(float(bme280_data.pressure), 2)
    temp =round(float(bme280_data.temperature), 2)
    date = datetime.now().strftime(DT_LOG_FORMAT)
    print(f'[{date}] {temp} {humidity} {pressure}')
    with open('hpt.log', '+a') as f:
        f.write(f'[{date}] {temp} {humidity} {pressure}\n')
    sleep(delay)
