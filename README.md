# Weather-Report
A followup project of https://github.com/Dragon8oy/temp-report using a Rapberry pi and BME280 sensor to monitor temperature, Humidity and barometric pressure, chart it on a flask based website. Using Docker enables us to scrap the messy install script with numerous tmux sessions (sorry Dragon8oy) and start the logging in a container that starts with the system

Containers:
- flask: python 3.8.6 flask website using uWSGI on port 8080
- nginx: Nginx reverse proxy uWSGI 8080 to port 80
- log: python 3.8.6 reading rpi I2c BME280 sensor and logging it

Fritzing circut diag image credit: Matt Hawkins (probably)

## Getting started
 - Connect the sensor and enable the I2C bus.
As well as the fritzing diagram Matt Hawkins' article has useful instructions about enabling the i2c system 
and connecting the sensor to I2c bus https://www.raspberrypi-spy.co.uk/2016/07/using-bme280-i2c-temperature-pressure-sensor-in-python
Although we're using the BME280 python module from Richard Hull https://pypi.org/project/RPi.bme280/ who also has some fine instructions.

 - Install docker and docker-compose on you pi. Here is a straghtforward guide: https://withblue.ink/2019/07/13/yes-you-can-run-docker-on-raspbian.html
but essentially I did:
```
sudo su -
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -
echo "deb [arch=armhf] https://download.docker.com/linux/raspbian buster stable" >>/etc/apt/sources.list.d/docker.list
apt update
apt install -y --no-install-recommends docker-ce cgroupfs-mount
systemctl enable docker.service
systemctl start docker.service
```
Additionaly I added the pi user to the docker group to enable a non-root user to run docker
```sudo usermod -aG docker pi```
restart the session or do ```newgrp docker``` (Remember this or you will still get 'permission denied')

 - Clone this repo.
cd into it,
if you were to just ```docker-compose up -d``` (it will ignore the image tag and pull the source images for the individual docker containers)
Now my pi3 took 4 hours to build the flask (python container with matplotlib, numpy and scipy)
so.. you can pull this from dockerhub built for arm
by starting with 
``` docker-compose pull```
will fetch my built flask image,

the other containers build in minutes so ```docker compose up -d `` will build them bfore starting

the rpi-gpio image mounts the /dev/ic2 system into the container so if you havent got the sensor working the stack won't start 
(I aim to fix this and at least let the stack start if the device isn't there and work on the code using the frozen copy of an old log)


## To-Do:
 - See project [plans](https://github.com/ihayhurst/TurgidLemonMeander/projects/1)

![alt text](https://ihayhurst.github.io/TurgidLemonMeander/graph.png)

![alt_text](https://ihayhurst.github.io/TurgidLemonMeander/BMP280-fritzing.png)
