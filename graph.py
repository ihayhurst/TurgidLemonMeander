# -*- coding: utf-8 -*-
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np
import sys, argparse, re, datetime
import config

DT_FORMAT       = '%Y/%m/%d-%H:%M'
LOG_DT_FORMAT = config.log_date_format
area_name = config.area_name 

def generateGraph(reading_count, area_name):
    '''Wrapper for drawgraph called from '''
    kwargs = {'tailmode' : True}
    args   = {reading_count}
    if len(open('hpt.log', encoding="utf-8").readlines(  )) < reading_count:
      print('Not enough lines in logfile, aborting\n')
      plt.figure()
      plt.savefig('hpt.png')
      plt.clf()
      plt.close('all')
      return
    x, y, h, p   = readValues(*args, **kwargs)
    drawGraph(x,y,h,p, area_name)

def drawGraph(x,y,h,p, area_name):
    x2 = mdates.date2num(x)
    x_sm = np.array(x2)
    x_smooth = np.linspace(x_sm.min(), x_sm.max(), 200)
    spl = make_interp_spline(x2, y, k=3)
    spl_h = make_interp_spline(x2, h, k=3)
    spl_p = make_interp_spline(x2, p, k=3)
    y_smooth = spl(x_smooth)
    h_smooth = spl_h(x_smooth)
    p_smooth = spl_p(x_smooth)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(right=0.75)
    fig.autofmt_xdate()
    hh = ax.twinx()
    pp = ax.twinx()

    ax.grid(which='major', axis='x', color='grey')
    hh.spines["right"].set_position(("axes", 1.2))

    plt.plot([],[])
    x_smooth_dt = mdates.num2date(x_smooth)
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %H:%M'))
    maFmt = mdates.DateFormatter('%b-d')
    miFmt = mdates.DateFormatter('%H-%M')
    ax.xaxis.set_major_formatter(maFmt)
    ax.xaxis.set_minor_formatter(miFmt)
    for label in ax.xaxis.get_minorticklabels()[::2]: # show every other minor label
        label.set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=10)

    plt.xlabel('Time (Month-Day - Hour: Minutes)')
    temperature_color = 'tab:red'
    humidity_color    = 'tab:green'
    pressure_color    = 'tab:blue'
    ax.set_ylabel('Temperature \u2103', color=temperature_color)
    hh.set_ylabel('Humidity %',         color=humidity_color)
    pp.set_ylabel('Pressure mBar',      color=pressure_color)
    ax.plot(x_smooth_dt, y_smooth, color=temperature_color, linewidth=1)
    hh.plot(x_smooth_dt, h_smooth, color=humidity_color, linewidth=1)
    pp.plot(x_smooth_dt, p_smooth, color=pressure_color, linewidth=1)
    plt.title(str(area_name) + ' Temperature, Humidity and Pressure logged by Pi')
    plt.savefig('graph.png')
    print('Created graph\n')
    plt.clf()
    plt.close('all')

def readValues(*args, **kwargs):
    '''for key, value in kwargs.items():     #Debug
        print ("%s == %s" %(key, value)) #Debug
    '''
    print("From: ",kwargs.get('from_date'))
    print("To: ",kwargs.get('to_date')) 

    if kwargs.get('lines') != None:
        reading_count = kwargs.get('lines')
    else:
        reading_count = args[0]

    log_dt_format = LOG_DT_FORMAT

    x=[] #Datetime
    y=[] #Temperature
    h=[] #Humidity 
    p=[] #Presure
    x.clear()
    y.clear()
    h.clear()
    p.clear()

    try:
        tailmode = kwargs.get('tailmode')
    except:
        tailmode = True
    if not tailmode:
        from_dt = date_to_dt(kwargs.get('from_date'),DT_FORMAT)
        to_dt = date_to_dt(kwargs.get('to_date'),DT_FORMAT)

    with open('hpt.log', 'r', encoding="utf-8") as f:
        if tailmode:
            taildata = f.readlines() [-reading_count:]
        else:
            taildata = f.readlines()
        for line in taildata:
            line = line.translate({ord(i): None for i in '[]'})
            data = re.split(" ", line)
            temp, humidity, pressure =  float(data[2]), float(data[3]), float(data[4])
            #print(f'Temp: {temp} Humidity:{humidity} Pressure:{pressure}\n')
            dt = str(data[0])+" "+str(data[1])
            dt = date_to_dt(dt, LOG_DT_FORMAT)
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
        return x,y,h,p

def cmd_args(args=None):
    parser = argparse.ArgumentParser("Graph.py charts range of times from a temperature log")

    parser.add_argument('-l', '--lines',  type=int, dest='lines',
                    help='Number of tailing log lines to plot')
    parser.add_argument('-s', '--start',  dest='start',
                    help='Start date YYYY/MM/DD-HH:MM')
    parser.add_argument('-e', '--end',  dest='end',
                    help='End   date YYYY/MM/DD-HH:MM')
    parser.add_argument('-d', '--dur',  dest='dur',
                    help='Duration: Hours, Days, Weeks,  e.g. 2W for 2 weeks')

    opt = parser.parse_args(args)

    return opt

def parse_duration(duration):
    #print("Duration == ",duration)
    hours = datetime.timedelta(hours = 1)
    days = datetime.timedelta(days = 1)
    weeks = datetime.timedelta(weeks = 1)
    fields = re.split('(\d+)',duration)
    #print(fields[1],"--",fields[2])
    duration = int(fields[1])
    if fields[2][:1].upper() == 'H':
        duration_td = duration * hours
    elif fields[2][:1].upper() == 'D':
        duration_td = duration * days
    elif fields[2][:1].upper() == 'W':
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

    if opt.dur and opt.start and opt.end: #Assume start and range ignore end
        print("All three madness") #Debug
        print("Duration",opt.dur)
        duration = parse_duration(opt.dur)
        opt.end_dt = date_to_dt(opt.start, DT_FORMAT)+duration
        opt.end = opt.end_dt.strftime(DT_FORMAT)

    if opt.dur and opt.start and not opt.end: #Start and range 
        print("Start date and duration") #Debug
        print("Duration",opt.dur)
        duration = parse_duration(opt.dur)
        opt.end_dt = date_to_dt(opt.start, DT_FORMAT)+duration
        opt.end = opt.end_dt.strftime(DT_FORMAT)

    if opt.dur and not opt.start and opt.end: #Range before enddate
        print("End date and duration") #Debug
        duration = parse_duration(opt.dur)
        opt.start_dt = date_to_dt(opt.end, DT_FORMAT)-duration
        opt.start = opt.start_dt.strftime(DT_FORMAT)
        
    if opt.dur and not opt.start and not opt.end: #tailmode with range
        print("End of log back by duratiion") #Debug
        duration = parse_duration(opt.dur)
        opt.end_dt = datetime.datetime.now()
        opt.end = dt_to_date (opt.end_dt, DT_FORMAT)
        opt.start_dt = date_to_dt(opt.end, DT_FORMAT)-duration
        opt.start = opt.start_dt.strftime(DT_FORMAT)

    if not opt.dur and opt.start and opt.end: #Date range
        print("Start date and end date") #Debug
        if date_to_dt(opt.start, DT_FORMAT) >date_to_dt(opt.end, DT_FORMAT): # End before start so swap
            opt.start, opt.end = opt.end, opt.start

    if not opt.dur and opt.start and not opt.end: #Start Date only - from start date to end
        print("Start Date to end of log ") #Debug
        opt.end_dt = datetime.datetime.now()
        opt.end = opt.end_dt.strftime(DT_FORMAT)

    if not opt.dur and not opt.start and opt.end: #End Date only - from end date to start
        print("End date back to the dawn of time (or the log at least) ") #Debug
        opt.start_dt = datetime.date(1970, 1, 1)
        opt.start = opt.start_dt.strftime(DT_FORMAT)

    if opt.lines != None: #tailmode with lines
        print("tail back number of lines") #Debug
        kwargs={'tailmode': True, 'lines': opt.lines, **kwargs}

    if not opt.lines and not opt.dur and not opt.start and not opt.end: #tailmode with lines (none set so using 12)
        kwargs={'tailmode': True, 'lines': 12}

    if not opt.lines:
        print("Not Tailmode")
        kwargs={'tailmode': False, 'from_date': opt.start, 'to_date': opt.end, **kwargs}


    x, y, h, p  = readValues(*args, **kwargs)
    drawGraph(x,y,h,p, area_name)
    sys.exit(1)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except ValueError:
        print("Give me something to do")
        sys.exit(1)
