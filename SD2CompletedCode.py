#!/usr/bin/python3
import serial
import sqlite3
import matplotlib.pyplot as plt
import math
import os

import pandas as pd
from scipy.stats import linregress
import numpy as np



desktop_path = '/home/sulfur101/Desktop'
base_filename = 'ATC_DB.db'
filename = os.path.join(desktop_path, base_filename)
count = 0
while os.path.exists(filename):
        count +=1
        filename = os.path.join(desktop_path, f'{base_filename}({count})')



# Connect to the database or create it if it doesn't exist
conn = sqlite3.connect(filename)
c = conn.cursor()
ser = serial.Serial('/dev/ttyACM0', 9600)
totaldatapoints = 0

# Determine whether it's NMOS or PMOS
device_type = ser.readline().decode('utf-8').strip()
if device_type == "1":
    device_type = "PMOS"
else:
    device_type = "NMOS"

vgs = []
current = []

# Create tables if they don't exist
c.execute(f'''
    CREATE TABLE IF NOT EXISTS {device_type}_Voltage (
        GVoltage REAL,
        SVoltage REAL,
        DVoltage REAL
    )
''')
c.execute(f'''
    CREATE TABLE IF NOT EXISTS {device_type}_VGS (
        Value REAL
    )
''')
c.execute(f'''
    CREATE TABLE IF NOT EXISTS {device_type}_Current (
        Value REAL
    )
''')
c.execute(f'''
    CREATE TABLE IF NOT EXISTS {device_type}_VGS_Current(
        VGS REAL,
        Current REAL
    )
''')

try:
    while True:
        data = ser.readline().decode('utf-8').strip()

        # Debugging line to print raw Arduino data
        print(f"Raw Arduino Data: {data}")

        # Split the data based on spaces
        values = data.split()

        # Extract numerical values
        gvoltage_value = float(values[0].split(":")[1])
        svoltage_value = float(values[1].split(":")[1])
        dvoltage_value = float(values[2].split(":")[1])
        vgs_value = float(values[3].split(":")[1])
        current_value = float(values[4].split(":")[1])

        # Store data in the database
        c.execute(f"INSERT INTO {device_type}_Voltage (GVoltage, SVoltage, DVoltage) VALUES (?,?,?)", (gvoltage_value, svoltage_value, dvoltage_value))
        c.execute(f"INSERT INTO {device_type}_VGS (Value) VALUES (?)", (vgs_value,))
        c.execute(f"INSERT INTO {device_type}_Current (Value) VALUES (?)", (current_value,))
        c.execute(f"INSERT INTO {device_type}_VGS_Current (VGS, Current) VALUES (?,?)", (vgs_value, current_value,))
        conn.commit()

        # Append values for plotting
        vgs.append(vgs_value)
        current.append(current_value)
        if device_type == "PMOS":
                ID = [math.sqrt(abs(value)) for value in current if abs(value) >= 0.005]
        else:
                ID = [math.sqrt(value) for value in current if value >= 0.005]
                
        #generate the VGS vs Current graph once all datapoints have been collected
        totaldatapoints += 1
        if totaldatapoints == 26:
                plt.figure()
                plt.plot(vgs, current, 'o-')
                plt.xlabel('VGS')
                plt.ylabel('CURRENT')
                plt.title('VGS vs. Current')
                plt.grid(True)
                plt.show(block=False)
                
                
        #generate the VGS vs sqrt(ID):
                
                slope, intercept, r_value, p_value, std_err = linregress(vgs[len(vgs)-len(ID):len(vgs)], ID)
        
                kn = 2*(slope)**2
                vt = abs(intercept)/slope
                
                value1 = round(kn, 4)
                value2 = round(vt, 4)
                print(value1)
                print(value2)
                
                plt.figure()
                plt.plot(vgs[len(vgs)-len(ID):len(vgs)], ID, 'o-')
                
                
                xmin, xmax = min(vgs[len(vgs)-len(ID):len(vgs)]), max(vgs[len(vgs)-len(ID):len(vgs)])
                ymin, ymax = min(ID), max(ID)

                
                text_x = xmax - 0.2 * (xmax - xmin)
                text_y = ymax - 0.1 * (ymax - ymin)
                
                textThing = 'Kn: ' + str(value1) + '\n' + 'Vt: ' + str(value2) 
                plt.text(text_x, text_y, textThing, fontsize = 10, verticalalignment = 'top', ha='right')
                plt.xlabel('VGS')
                plt.ylabel('SQRT(ID)')
                plt.title('VGS vs sqrt(ID)')
                plt.grid(True)
                plt.show(block=True)
                
                
                
                break
                
        

                
except KeyboardInterrupt:
    print("Data collection stopped by user")

finally:
    # Close the serial port and database connection
    ser.close()
    conn.close()
