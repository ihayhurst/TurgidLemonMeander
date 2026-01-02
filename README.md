# Weather-Report
A follow-up project of [temp-report](https://github.com/stuarthayhurst/temp-report),using a Raspberry Pi and BME280 sensor to monitor temperature, humidity and barometric pressure. Data is logged continuously and visualised via a Flask-based website, with interactive navigation of historical readings.

Containers:
 - flask: python 3.11 flask website using uWSGI on port 8080
 - nginx: Nginx reverse proxy uWSGI 8080 to port 80
 - log: python  reading rpi I2c BME280 sensor and logging it

Fritzing circut diag image credit: Matt Hawkins (probably)

## Web interface

The Flask application now serves an interactive chart backed by a JSON data endpoint.  
This allows browsing historical data ranges using day navigation buttons and a time slider, rather than relying solely on static matplotlib output.

To improve performance on low-powered hardware (e.g. Raspberry Pi), log data is cached in memory and only reloaded when the underlying log file changes.

### About graphing

Matplotlib is still used for legacy and CLI-driven graph generation, but the primary web interface renders charts dynamically in the browser using JSON data served by Flask.

## Notes

- This is intended as a lightweight, single-device project rather than a general-purpose time-series system.
- Log files grow continuously unless rotated externally.
- Performance is tuned for Raspberry Pi–class hardware and low request volumes.


## Getting started
 ### Connecting the sensor:
 - Connect the sensor and enable the I2C bus
 - As well as the fritzing diagram, Matt Hawkins' [article](https://www.raspberrypi-spy.co.uk/2016/07/using-bme280-i2c-temperature-pressure-sensor-in-python) has useful instructions about enabling the i2c system and connecting the sensor to i2c bus
 - Although, we're using the BME280 python module from Richard Hull who also has some fine [instructions](https://pypi.org/project/RPi.bme280/).

 ### Setting up docker:
 - Install docker and docker-compose on you pi: [straightforward guide](https://withblue.ink/2019/07/13/yes-you-can-run-docker-on-raspbian.html)
 - Essentially, the following can be used:
```
  sudo su -
  curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -
  echo "deb [arch=armhf] https://download.docker.com/linux/raspbian bookworm stable" >>/etc/apt/sources.list.d/docker.list
  apt update
  apt install -y --no-install-recommends docker-ce cgroupfs-mount
  systemctl enable docker.service --now
```
 - Additionaly I added the pi user to the docker group to enable a non-root user to run docker: `sudo usermod -aG docker pi`
 - Restart the session, or do: `newgrp docker` (Remember this or you will still get 'permission denied')

 ### Setting up the project:
 - Clone this repo: `git clone https://github.com/ihayhurst/TurgidLemonMeander.git`
 - `cd TurgidLemonMeander`
 - Fetch the containers: `docker-compose pull` (The Pi 3 can take 4 hours to build it otherwise)
 - Start the containers: `docker-compose up -d` 
 - Also note, if the sensor isn't working, the stack won't start (/dev/i2c is required)
   - set the environment variable DUMMY_SENSOR=True or in the config pi-gpio/config.py DUMMY_SENSOR = True

## To-Do:
 - See project [plans](https://github.com/ihayhurst/TurgidLemonMeander/projects/1)

## Diagrams:

![Example output](https://github.com/ihayhurst/TurgidLemonMeander/blob/master/docs/graph.png?raw=true)
![Example output (historical range view)](https://github.com/ihayhurst/TurgidLemonMeander/blob/master/docs/screenshot-2026-01-02.png?raw=true))


![Circuit diagram](https://github.com/ihayhurst/TurgidLemonMeander/blob/master/docs/BMP280-fritzing.png?raw=true)
