# Weather-Report
A followup project of https://github.com/Dragon8oy/temp-report using a Rapberry pi and BME280 sensor to monitor temperature, Humidity and barometric pressure, chart it on a flask based website 

Containers for:
- python 3.8.6 flask website using uWSGI on port 8080
- Nginx reverse proxy uWSGI to port 80
- python 3.8.6 reading rpi I2c BME280 sensor and logging it 

**TODO**
 - Remove or use the api blueprint I was developing for something else
 - Report via email if specific conditions are met.
 - Respond automaticaly to email requests for data 

![alt text](https://ihayhurst.github.io/TurgidLemonMeander/graph.png)

![alt_text](https://ihayhurst.github.io/TurgidLemonMeander/BMP280-fritzing.png)
