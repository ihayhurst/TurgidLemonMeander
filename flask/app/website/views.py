import os
from flask import render_template, Blueprint, request
from flask import __version__ as __flask_version__
from flask import current_app
from app.website import graph

website = Blueprint(
    "website",
    __name__,
    static_folder="static",
    static_url_path="/website/static",
    template_folder="templates",
)


@website.route("/", methods=["POST", "GET"])
def website_home():

    if request.method == "POST":
        result = request.form
        for key, value in result.items():
            print("received", key, "with value", value)
        # 3600 sec in hour / delay interval 600
        interval = int(result["region"])
        region = interval * 6
        lookup = "wibble"
    else:
        interval = 24
        region = interval * 6
        lookup = "wibble"
        

    graphImageData = graph.generateGraph(region, "Conservatory")
    graphImageData = graphImageData.decode("utf-8")
    title = f"Pi weather report for {interval} Hours"
    return render_template(
        "index.html",
        title=title,
        result="wibble",
        lookup=lookup,
        graphImageData=graphImageData,
    )


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
