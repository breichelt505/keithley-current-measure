import pyvisa
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import pandas as pd
import argparse
import os


parser = argparse.ArgumentParser(
    prog = "keithley_measure",
    description = "measure current using the keithley electrometer and store as a csv. Terminate program using ctrl+c"
)
parser.add_argument("-l","--listresources", help="print resources to troubleshoot connection error",
                    action = "store_true")
parser.add_argument("-f","--filename", help="name that output file is saved to. Default is timestamp of first reading.",
                    type = str)
parser.add_argument("-k","--keithleytime", 
                    help="use time from keithley (uses system time from computer by default)",
                    action = "store_true")
parser.add_argument("-a","--averagetime", 
                    help="average readings over this time interval in seconds. Default is to save every reading and do no averaging.",
                    type = float)
parser.add_argument("-u","--updateperiod", 
                    help="update plot after this many (averaged if -a is specified) readings. Default is 10.",
                    type = int)
args = parser.parse_args()


fpath = pathlib.Path(__file__)
project_dir = fpath.parents[1]
print(project_dir)


monthdict = {
    "january" : 1,
    "february" : 2,
    "march" : 3,
    "april" : 4,
    "may" : 5,
    "june" : 6, 
    "july" : 7,
    "august" : 8,
    "september" : 9,
    "october" : 10,
    "november" : 11,
    "december" : 12
}

def month_to_number(month):
    for key in monthdict:
        if month.lower() in key:
            number = monthdict[key]
            return int(number)
            break
    raise ValueError(f"month '{month}' not in monthdict")

def get_vals(output):
    reading, time, date, _ = output.split(",")
    datesplit = date.split("-")
    timesplit = time.split(":")
    dt = datetime.datetime(
        int(datesplit[2]),month_to_number(datesplit[1]),int(datesplit[0]),
        int(timesplit[0]),int(timesplit[1]),int(np.floor(float(timesplit[2]))),
        int((float(timesplit[2])-np.floor(float(timesplit[2])))*1e6)
    )
    dt = pd.to_datetime(dt)
    reading = float(reading[:-4])
    return dt, reading

rm = pyvisa.ResourceManager()
if args.listresources:
    print(rm.list_resources()) 

# open keithley resource and reset
keithley = rm.open_resource('GPIB0::27::INSTR')
keithley.write("*rst; status:preset; *cls")

# zchk shunts the input to find zero current, range is set to minimum
keithley.write(":SYSTem:ZCHeck ON")
keithley.write(":conf:curr")
keithley.write(":curr:dc:rang 20e-12")
keithley.query(":read?")
# the zero measurement is made and correction is applied
keithley.write(":SYSTem:ZCORrect:ACQuire")
keithley.write(":SYSTem:ZCORrect ON")
keithley.write(":sens:curr:rang:auto on")
keithley.query(":read?")
keithley.write(":SYSTem:ZCHeck OFF")


i=0
if args.updateperiod:
    update_period = args.updateperiod
else: 
    update_period = 10

times = []
currents = []

plt.figure(figsize=(9,4))

times_avgblock = []
currents_avgblock = []
try:
    while True:
        i+=1

        if args.averagetime:
            times_avgblock = []
            currents_avgblock = []
            then = datetime.datetime.now()
            now = datetime.datetime.now()
            while (now-then) < datetime.timedelta(seconds=args.averagetime):
                keithley.write(":*WAI")
                output = keithley.query(":read?")
                now = datetime.datetime.now()
                t, I = get_vals(output)
                if not(args.keithleytime):
                    t = now
                times_avgblock.append(t)
                currents_avgblock.append(I)
            t = pd.to_datetime(times_avgblock).mean()
            I = np.mean(currents_avgblock)
        else:
            now = datetime.datetime.now()
            keithley.write(":*WAI")
            output = keithley.query(":read?")
            t, I = get_vals(output)
            if not(args.keithleytime):
                t = now

        times.append(t)
        currents.append(I)
        if i%update_period == 0:
            plt.cla()
            plt.plot(times,currents, "r")
            plt.ylabel("current (A)")
            plt.xlabel("time (hh:mm:ss)")
            plt.tight_layout()
            plt.pause(0.05)
except KeyboardInterrupt:
    print("done")
    keithley.close()

data = {"datetime" : times, "current (A)" : currents}
df = pd.DataFrame(data=data)
if args.filename:
    fname = args.filename
else:
    fname = df["datetime"][0].strftime('current_%Y-%m-%d_%H,%M,%S.csv')

if not os.path.isdir(project_dir/"outputs"):
    os.mkdir(project_dir/"outputs")

df.to_csv(project_dir/f"outputs/{fname}")

plt.cla()
plt.plot(times,currents, "r")
plt.ylabel("current (A)")
plt.xlabel("time (hh:mm:ss)")
plt.tight_layout()
plt.show(block=True)