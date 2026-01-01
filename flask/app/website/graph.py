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
from flask import has_app_context

mpl.use("agg")
website = Blueprint("website", __name__)



def get_config(key):
    if has_app_context():
        return app.config[key]
    raise RuntimeError("No Flask app context available")



# import from config
# LOG_DATE_FORMAT  # in config.py to match the format in the log file
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DT_FORMAT = "%Y/%m/%d-%H:%M"  # format used on the cli
APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, "static")
_cached_log = None
_cached_mtime = None
_ALT_CORR = None

def pressure_altitude_offset():
    global _ALT_CORR
    if _ALT_CORR is None:
        altitude = get_config("ALTITUDE")
        _ALT_CORR = round(altitude * 0.12677457, 1)
    return _ALT_CORR


def correct_pressure_for_altitude(p_values):
    offset = pressure_altitude_offset()
    return [round(p + offset, 1) for p in p_values]


def prepareGraphData(reading_count):
    x, y, h, p = readValues(reading_count, tailmode=True)

    p = correct_pressure_for_altitude(p)

    rows = load_log_cached()
    trend = pressure_trend(rows, hours=3)


    return {
        "time": [dt.isoformat() for dt in x],
        "temperature": y,
        "humidity": [round(v, 1) for v in h],
        "pressure": p,
        "pressure_trend": trend,
    }


def pressure_trend(data, hours=3, warn_hpa=3.0):
    """
    data: list of (dt, t, h, p) sorted by dt
    returns (delta, p_now, p_then) or (None, None, None)
    """
    if not data:
        return None, None, None

    end_dt, _, _, end_p = data[-1]
    start_dt = end_dt - datetime.timedelta(hours=hours)

    # Find closest reading at or before start_dt
    start_p = None
    for dt, _, _, p in reversed(data):
        if dt <= start_dt:
            start_p = p
            break

    if start_p is None:
        return None

    delta = round(end_p - start_p, 1)
    return {
        "hours": hours,
        "delta_hpa": delta,
        "direction": "up" if delta > 0 else "down" if delta < 0 else "flat",
        "warning": abs(delta) >= warn_hpa,
    }

def prepareGraphData_range(start_dt, end_dt):
    x, y, h, p = readValues(
        #from_dt=datetime.datetime.fromisoformat(start_dt),
        from_date = start_dt,
        #to_dt=datetime.datetime.fromisoformat(end_dt),
        to_date = end_dt,
        tailmode=False,
    )
    p = correct_pressure_for_altitude(p)
    rows = load_log_cached()
    trend = pressure_trend(rows, hours=3)



    return {
        "time": [dt.isoformat() for dt in x],
        "temperature": y,
        "humidity": [round(v, 1) for v in h],
        "pressure": p,
        "pressure_trend": trend,
    }


def load_log_cached():
    global _cached_log, _cached_mtime
    LOG_FILE = os.path.join(website.root_path, "data-log/hpt.log")
    stat = os.stat(LOG_FILE)

    if _cached_log is None or stat.st_mtime != _cached_mtime:
        data = []
        with open(LOG_FILE) as f:
            for line in f:
                if not line:
                    continue
                line = clean_log_line(line)
                parts = line.split()
                if len(parts) < 5:
                    continue
                try:
                    dt = date_to_dt(f"{parts[0]} {parts[1]}", LOG_DATE_FORMAT)
                    #t, h, p = map(float, parts[2:5])
                    t = round(float(parts[2]), 2)
                    h = round(float(parts[3]), 1)
                    p = round(float(parts[4]), 1)
                except ValueError:
                    continue
                data.append((dt, t, h, p))


        _cached_log = data
        _cached_mtime = stat.st_mtime

    return _cached_log


def clean_log_line(line):
    return line.replace("\x00", "").translate({91: None, 93: None}).strip()

def select_rows_tail(data, count):
    return data[-count:]


def select_rows_range(data, from_dt, to_dt):
    rows = []
    for row in data:
        dt = row[0]
        if dt < from_dt:
            continue
        if dt > to_dt:
            break
        rows.append(row)
    return rows


def parse_and_clamp_range(data, from_date, to_date):
    data_start = data[0][0]
    data_end   = data[-1][0]

    from_dt = date_to_dt(from_date, LOG_DATE_FORMAT)
    to_dt   = date_to_dt(to_date, LOG_DATE_FORMAT)

    if from_dt < data_start:
        from_dt = data_start
    if to_dt > data_end:
        to_dt = data_end

    return from_dt, to_dt


def rows_to_series(rows):
    x, y, h, p = [], [], [], []
    for dt, t, hum, pres in rows:
        x.append(dt)
        y.append(t)
        h.append(hum)
        p.append(pres)
    return x, y, h, p


def readValues(*args, **kwargs):
    data = load_log_cached()
    if not data:
        return [], [], [], []

    tailmode = kwargs.get("tailmode", False)

    if tailmode:
        if args:
            count = args[0]
        elif "lines" in kwargs:
            count = kwargs["lines"]
        else:
            raise ValueError("tailmode requires reading count")

        rows = select_rows_tail(data, count)

    else:
        if "from_date" not in kwargs or "to_date" not in kwargs:
            raise ValueError("range mode requires from_date and to_date")

        from_dt, to_dt = parse_and_clamp_range(
            data,
            kwargs["from_date"],
            kwargs["to_date"],
        )
        rows = select_rows_range(data, from_dt, to_dt)

    return rows_to_series(rows)


def generateGraph(reading_count, area_name):
    """Wrapper for drawgraph called from """

    kwargs = {"tailmode": True, "text": True}
    args = (reading_count,)
    filename = os.path.join(website.root_path, "data-log/hpt.log")
    if len(open(filename, encoding="utf-8").readlines()) < reading_count:
        print("Not enough lines in logfile, aborting\n")
        return
    x, y, h, p = readValues(*args, **kwargs)
    return drawGraph(x, y, h, p, area_name, **kwargs)


def drawGraph(x, y, h, p, area_name, **kwargs):
    if area_name is None:
        area_name = get_config("AREA_NAME")
    temp_max = get_config("TEMP_MAX")
    temp_min = get_config("TEMP_MIN")
    pressure_min = get_config("PRESSURE_MIN")
    pressure_max = get_config("PRESSURE_MAX")
    p = correct_pressure_for_altitude(p)
    x2 = mdates.date2num(x)
    x_sm = np.array(x2)
    x_smooth = np.linspace(x_sm.min(), x_sm.max(), 200)
    spl = UnivariateSpline(x2, y, k=3)
    spl_h = UnivariateSpline(x2, h, k=3)
    spl_p = UnivariateSpline(x2, p, k=3)
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
    ax.set_ylim([temp_min, temp_max])
    ax.axhline(y=0, color="purple", linestyle="--", alpha=0.3)

    pp.set_ylim([pressure_min, pressure_max])
    # plot boundaries of normal pressure
    pp.axhline(y=1010, color="tab:blue", linestyle="--", alpha=0.3)
    # mean pressure pp.axhline(y=1013, color="tab:blue", linestyle="--", alpha=0.3)
    pp.axhline(y=1020, color="tab:blue", linestyle="--", alpha=0.3)
    hh.set_ylim([0, 100])
    plt.title(f"{area_name} Temperature, Humidity and Pressure logged by Pi")

    if kwargs.get("text"):
        pic_IObytes = io.BytesIO()
        plt.savefig(pic_IObytes, format="png")
        pic_IObytes.seek(0)
        pic_hash = base64.b64encode(pic_IObytes.read())
        plt.close(fig)
        print("Graph created in base64 encoding")
        return pic_hash

    else:
        plt.savefig("graph.png", format="png")
        print("Created graph\n")
        plt.clf()
        plt.close("all")
    return


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
