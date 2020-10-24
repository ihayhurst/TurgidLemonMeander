import os
from flask import render_template, Blueprint, current_app, request
from flask import __version__ as __flask_version__
import base64
import . graph
website = Blueprint('website', __name__)


@website.route("/", methods = ['POST', 'GET'])
def index():

    if request.method == 'POST':
        result = request.form
        region = int(result['region'])*6 #3600 sec in hour / delay interval 600
        lookup = "wibble"
    else:
        region = (6*24)

    graphImageData = graph.generateGraph(region, 'Conservatory')
    graphImageData = graphImageData.decode('utf-8')
    title = "Pi weather report"
    return render_template('index.html',title=title, result=result, lookup=lookup, graphImageData=graphImageData)


@website.route("/about")
def website_home():

    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")
    envprint = {k:v for k,v in current_app.config.items()}
    flaskVer = __flask_version__
    if app_name:
        message = f'Hello from {app_name}, a flask ver {flaskVer} app running in a Docker container behind Nginx! with redis and hot code load'
        return render_template('about.html', message=message, envprint=envprint)

    return render_template('about.html', message="Hello from flask")
