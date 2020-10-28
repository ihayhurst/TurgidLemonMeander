# rpi-gpio
A Docker container where the i2c device fs mounted and python smbus2 and rpiBME280
run in log.py to read sensor and log data,
Data is logged to a Docker volume mount which is alos mounted into the flask container

Inspired by the docker-rpi gpio container work of Roberto Aguilar
https://github.com/rca/docker-rpi-gpio.git
