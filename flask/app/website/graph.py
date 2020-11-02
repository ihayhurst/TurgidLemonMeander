# -*- coding: utf-8 -*-
import sys
import os
import argparse
import datetime
import base64
import io
from re import split

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.interpolate import UnivariateSpline

from flask import Blueprint
from flask import current_app as app


website = Blueprint("website", __name__)
# TODO: write a proper function to get what we need from the config


def getGlobals():
    with app.app_context():
        area_name = app.config["AREA_NAME"]
    return area_name


mpl.use("agg")
DT_FORMAT = "%Y/%m/%d-%H:%M"  # format used on the cli

# import from config
# LOG_DATE_FORMAT  # in config.py to match the format in the log file
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, "static")


def generateGraph(reading_count, area_name):
    """Wrapper for drawgraph called from """
    kwargs = {"tailmode": True, "text": True}
    args = {reading_count}
    filename = os.path.join(website.root_path, "data-log/hpt.log")
    if len(open(filename, encoding="utf-8").readlines()) < reading_count:
        print("Not enough lines in logfile, aborting\n")
        plt.figure()
        plt.savefig("hpt.png")
        plt.clf()
        plt.close("all")
        return
    x, y, h, p = readValues(*args, **kwargs)
    return drawGraph(x, y, h, p, area_name, **kwargs)


def drawGraph(x, y, h, p, area_name, **kwargs):
    x2 = mdates.date2num(x)
    x_sm = np.array(x2)
    x_smooth = np.linspace(x_sm.min(), x_sm.max(), 200)
    spl = UnivariateSpline(x2, y, k=3)
    spl_h = UnivariateSpline(x2, h, k=3)
    spl_p = UnivariateSpline(x2, p, k=3)
    # If you want to see more wibble in your lines
    # spl.set_smoothing_factor(0.5)
    # spl_h.set_smoothing_factor(0.5)
    # spl_p.set_smoothing_factor(0.5)
    y_smooth = spl(x_smooth)
    h_smooth = spl_h(x_smooth)
    p_smooth = spl_p(x_smooth)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(right=0.75)
    fig.autofmt_xdate()
    hh = ax.twinx()
    pp = ax.twinx()

    ax.grid(which="major", axis="x", color="grey")
    hh.spines["right"].set_position(("axes", 1.2))

    plt.plot([], [])
    x_smooth_dt = mdates.num2date(x_smooth)
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %H:%M'))
    maFmt = mdates.DateFormatter("%b-%d")
    miFmt = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(maFmt)
    ax.xaxis.set_minor_formatter(miFmt)
    for label in ax.xaxis.get_minorticklabels()[::2]:  # show every other minor label
        label.set_visible(True)
    ax.tick_params(axis="both", which="major", labelsize=10)

    plt.xlabel("Time (Month-Day - Hour: Minutes)")
    temperature_color = "tab:red"
    humidity_color = "tab:green"
    pressure_color = "tab:blue"
    ax.set_ylabel("Temperature \u2103", color=temperature_color)
    hh.set_ylabel("Humidity %", color=humidity_color)
    pp.set_ylabel("Pressure mBar", color=pressure_color)
    ax.plot(x_smooth_dt, y_smooth, color=temperature_color, linewidth=1)
    hh.plot(x_smooth_dt, h_smooth, color=humidity_color, linewidth=1)
    pp.plot(x_smooth_dt, p_smooth, color=pressure_color, linewidth=1)
    ax.set_ylim([-10, 35])
    ax.axhline(y=0, color="purple", linestyle="--", alpha=0.3)
    pp.set_ylim([940, 1053])
    pp.axhline(y=1009.144, color="tab:blue", linestyle="--", alpha=0.3)
    pp.axhline(y=1022.689, color="tab:blue", linestyle="--", alpha=0.3)
    hh.set_ylim([0, 100])
    # TODO: blergh just a test of a get config app_context
    gareaName = getGlobals()
    plt.title(f"{gareaName} Temperature, Humidity and Pressure logged by Pi")

    if kwargs.get("text"):
        pic_IObytes = io.BytesIO()
        plt.savefig(pic_IObytes, format="png")
        pic_IObytes.seek(0)
        pic_hash = base64.b64encode(pic_IObytes.read())
        print("Graph created in base64 encoding")
        return pic_hash

    else:
        plt.savefig("graph.png", format="png")
        print("Created graph\n")
        plt.clf()
        plt.close("all")
    return


def readValues(*args, **kwargs):
    """for key, value in kwargs.items():     #Debug
    print ("%s == %s" %(key, value)) #Debug
    """
    print("From: ", kwargs.get("from_date"))
    print("To: ", kwargs.get("to_date"))

    if kwargs.get("lines") is not None:
        reading_count = kwargs.get("lines")
    else:
        reading_count = args[0]

    x = []  # Datetime
    y = []  # Temperature
    h = []  # Humidity
    p = []  # Presure
    x.clear()
    y.clear()
    h.clear()
    p.clear()

    tailmode = kwargs.get("tailmode", False)
    if not tailmode:
        from_dt = date_to_dt(kwargs.get("from_date"), DT_FORMAT)
        to_dt = date_to_dt(kwargs.get("to_date"), DT_FORMAT)

    filename = os.path.join(APP_ROOT, "data-log/hpt.log")
    with open(filename, "r", encoding="utf-8") as f:
        if tailmode:
            taildata = f.readlines()[-reading_count:]
        else:
            taildata = f.readlines()
        for line in taildata:
            line = line.translate({ord(i): None for i in "[]"})
            data = split(" ", line)
            temp, humidity, pressure = float(data[2]), float(data[3]), float(data[4])
            dt = f"{data[0]} {data[1]}"
            dt = date_to_dt(dt, LOG_DATE_FORMAT)
            if tailmode:
                x.append(dt)
                y.append(temp)
                h.append(humidity)
                p.append(pressure)
            else:
                if (dt >= from_dt) and (dt <= to_dt):
                    x.append(dt)
                    y.append(temp)
                    h.append(humidity)
                    p.append(pressure)
        return x, y, h, p


def cmd_args(args=None):
    parser = argparse.ArgumentParser(
        "Graph.py charts range of times from a temperature log"
    )

    parser.add_argument(
        "-l",
        "--lines",
        type=int,
        dest="lines",
        help="Number of tailing log lines to plot",
    )
    parser.add_argument(
        "-s", "--start", dest="start", help="Start date YYYY/MM/DD-HH:MM"
    )
    parser.add_argument("-e", "--end", dest="end", help="End   date YYYY/MM/DD-HH:MM")
    parser.add_argument(
        "-d",
        "--dur",
        dest="dur",
        help="Duration: Hours, Days, Weeks,  e.g. 2W for 2 weeks",
    )
    parser.add_argument(
        "-t", "--text", dest="text", help="Output graphic as base64 encoded text"
    )

    opt = parser.parse_args(args)

    return opt


def parse_duration(duration):
    hours = datetime.timedelta(hours=1)
    days = datetime.timedelta(days=1)
    weeks = datetime.timedelta(weeks=1)
    fields = split(r"(\d+)", duration)
    duration = int(fields[1])
    if fields[2][:1].upper() == "H":
        duration_td = duration * hours
    elif fields[2][:1].upper() == "D":
        duration_td = duration * days
    elif fields[2][:1].upper() == "W":
        duration_td = duration * weeks
    else:
        raise ValueError

    return duration_td


def date_to_dt(datestring, FORMAT):
    dateasdt = datetime.datetime.strptime(datestring, FORMAT)
    return dateasdt


def dt_to_date(dateasdt, FORMAT):
    datestring = datetime.datetime.strftime(dateasdt, FORMAT)
    return datestring


def main(args=None):
    opt = cmd_args(args)
    kwargs = {}
    area_name = ""

    if opt.dur and opt.start and opt.end:  # Assume start and range ignore end
        print("Duration", opt.dur)
        duration = parse_duration(opt.dur)
        opt.end_dt = date_to_dt(opt.start, DT_FORMAT) + duration
        opt.end = opt.end_dt.strftime(DT_FORMAT)

    if opt.dur and opt.start and not opt.end:  # Start and range
        print("Duration", opt.dur)
        duration = parse_duration(opt.dur)
        opt.end_dt = date_to_dt(opt.start, DT_FORMAT) + duration
        opt.end = opt.end_dt.strftime(DT_FORMAT)

    if opt.dur and not opt.start and opt.end:  # Range before enddate
        duration = parse_duration(opt.dur)
        opt.start_dt = date_to_dt(opt.end, DT_FORMAT) - duration
        opt.start = opt.start_dt.strftime(DT_FORMAT)

    if opt.dur and not opt.start and not opt.end:  # tailmode with range
        duration = parse_duration(opt.dur)
        opt.end_dt = datetime.datetime.now()
        opt.end = dt_to_date(opt.end_dt, DT_FORMAT)
        opt.start_dt = date_to_dt(opt.end, DT_FORMAT) - duration
        opt.start = opt.start_dt.strftime(DT_FORMAT)

    if not opt.dur and opt.start and opt.end:  # Date range
        if date_to_dt(opt.start, DT_FORMAT) > date_to_dt(
            opt.end, DT_FORMAT
        ):  # End before start so swap
            opt.start, opt.end = opt.end, opt.start

    if (
        not opt.dur and opt.start and not opt.end
    ):  # Start Date only - from start date to end
        opt.end_dt = datetime.datetime.now()
        opt.end = opt.end_dt.strftime(DT_FORMAT)

    if (
        not opt.dur and not opt.start and opt.end
    ):  # End Date only - from end date to start
        opt.start_dt = datetime.date(1970, 1, 1)
        opt.start = opt.start_dt.strftime(DT_FORMAT)

    if opt.lines is not None:  # tailmode with lines
        kwargs = {"tailmode": True, "lines": opt.lines, **kwargs}

    if (
        not opt.lines and not opt.dur and not opt.start and not opt.end
    ):  # tailmode with lines (none set so using 12)
        kwargs = {"tailmode": True, "lines": 12}

    if not opt.lines:
        print("Not Tailmode")
        kwargs = {
            "tailmode": False,
            "from_date": opt.start,
            "to_date": opt.end,
            **kwargs,
        }

    if opt.text is not None:
        print("Base64 encoded png output")
        kwargs = {"text": True, **kwargs}

    if not opt.text:
        print("png output file")
        kwargs = {"text": False, **kwargs}

    x, y, h, p = readValues(*args, **kwargs)
    drawGraph(x, y, h, p, area_name, **kwargs)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except ValueError:
        print("Give me something to do")
