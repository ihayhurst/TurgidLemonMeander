import os
import requests
from flask import render_template, Blueprint, request, jsonify
from flask import __version__ as __flask_version__
from flask import current_app
from app.website import graph
import datetime

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
website = Blueprint(
    "website",
    __name__,
    static_folder="static",
    static_url_path="/website/static",
    template_folder="templates",
)

@website.route("/")
def website_home():
    area_name = current_app.config['AREA_NAME']
    templateData = {
        'title': f"sensor reports for {area_name}",
        'currentPiTemp': get_pi_temp(),
        'currentReadings': get_current_bme280_reading()
    }
    return render_template("index.html", **templateData)

@website.route("/mpl", methods=["POST", "GET"])
def website_mpl():
    DEFAULT_INTERVAL = 24
    if request.method == "POST":
        raw = request.form.get("region", DEFAULT_INTERVAL)
        try:
            interval = int(raw)
        except (TypeError, ValueError):
            interval = DEFAULT_INTERVAL
        region = interval * 6
        lookup = "wibble"
    else:
        interval = DEFAULT_INTERVAL

    region = interval * 6
    lookup = "wibble"

    area_name = current_app.config['AREA_NAME']
    graphImageData = graph.generateGraph(region, area_name)
    graphImageData = graphImageData.decode("utf-8")
    templateData = {
        'title':  f"Pi weather report for {interval} Hours",
        'lookup': lookup,
        'graphImageData': graphImageData,
        'currentPiTemp': get_pi_temp(),
        'currentReadings': get_current_bme280_reading()

    }
    return render_template( "mpl.html", **templateData)


@website.route("/graph-data")
def graph_data():
    if "start" in request.args and "end" in request.args:
        start_iso = request.args["start"].replace("Z", "")
        end_iso   = request.args["end"].replace("Z", "")
        print(f'{request.args["start"]}')

        start_dt = datetime.datetime.fromisoformat(start_iso)
        end_dt   = datetime.datetime.fromisoformat(end_iso)
        start_str =graph.dt_to_date(start_dt, LOG_DATE_FORMAT)
        end_str   =graph.dt_to_date(end_dt, LOG_DATE_FORMAT)

        print(f"{start_str=},{end_str=}")
        return jsonify(graph.prepareGraphData_range(start_str, end_str))

    # fallback tailing that last logged data
    hours = int(request.args.get("hours", 48))
    reading_count = hours * 6  # or whatever your cadence is
    return jsonify(graph.prepareGraphData(reading_count))


@website.route("/about")
def website_about():

    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")
    envprint = {k: v for k, v in current_app.config.items()}
    flaskVer = __flask_version__
    if app_name:
        message = f"""Hello from {app_name}, a flask ver {flaskVer}
                    app running in a Docker container
                    behind Nginx! with redis and hot code load"""
        return render_template("about.html", message=message, envprint=envprint)

    return render_template("about.html", message="Hello from flask")


def get_pi_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp_c = int(f.read()) / 1000
            return f"{temp_c:.1f}°C"
    except FileNotFoundError:
        return "Unavailable"

def get_current_air_temp():
    return "hot"

def get_current_bme280_reading():
    try:
        resp = requests.get("http://rpi-gpio:5000/current", timeout=1)
        #resp = requests.get("http://juniper.local:5000/current", timeout=1)
        resp.raise_for_status()
        print(resp.json())
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
