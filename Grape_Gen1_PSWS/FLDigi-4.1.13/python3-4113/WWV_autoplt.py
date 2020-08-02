#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 6 21::37 2020
Full AUTO WWV file processing.
@author dkazdan          mods @jcgibbons N8OBJ
"""


import os
from os import path
import sys
import shutil
import csv
from datetime import date, timedelta
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import filtfilt, butter
from matplotlib.pyplot import plot, legend, show, grid, figure, savefig
import subproces
import webbrowser
from WWV_utility import time_string_to_decimals, graph_Doppler_and_power_data

# ~ points to users home directory - usually /home/pi/
homepath = os.path.expanduser('~')

# imbed the trailing / in the home path
homepath = homepath + "/"

print('Home Path = ' + homepath)

PROCESSDIR = homepath + 'WWVdata/'

#directories for storing processed data files
DATADIR = homepath + 'WWVdata/temp/'

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#This is a MANUAL FORCED find of the file to be graphed

#yesterdaystr='2020-04-25'

# if using above line, comment out 3 lines in next section
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#            - - - - OR - - - -
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

# Find numerical version of today in N8OBJ format
today=date.today()

# And from that, of yesterday
yesterday=today-timedelta(1) #create yesterday's date

# Then turn it into a string of appropriate format
yesterdaystr=yesterday.__str__() #yesterday's date in string form, ISO format

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#convert date format to John's filename format filename
OBJdate=yesterdaystr[2:] #removes first two digits of year
OBJdate=OBJdate.replace('-','') #4emove the hyphens
TEMPFILE='analysis'+OBJdate+'.csv' #John's filename format
timestamped_tempfile=(PROCESSDIR + TEMPFILE) #with full path

# make sure temp path exists - if not, create it with correct permissions
if (path.exists(DATADIR)):
    print('DATADIR exists: ' + DATADIR)
else:
    print('making path ' + DATADIR)
    os.mkdir(DATADIR)			# create tyhe directory
    os.chmod(DATADIR, mode=0o764)	# set the permissions to 764

# Now, from which of the 9 beacon frequencies is this file?
# Create list of beacon name, frequency, count
# May eventually need more categories if audio sidebands are recorded.
WWV2p5 = ['WWV2p5', 2500000., 0] # i.e., 2.5 MHz etc.
WWV5   = ['WWV5',   5000000., 0]
WWV10  = ['WWV10', 10000000., 0]
WWV15  = ['WWV15', 15000000., 0]
WWV20  = ['WWV20', 20000000., 0]
WWV25  = ['WWV25', 25000000., 0]
CHU3   = ['CHU3',   3300000., 0] # CHU actual frequencies are
CHU7   = ['CHU7',   7850000., 0] # 3.33, 7.85, and 14.67 MHz
CHU14  = ['CHU14', 14670000., 0]

# WWV transmitters for 2.5 MHz, 20 MHz, and the experimental 25 MHz put out an ERP of 2.5 kW
# WWV transmitters on 5 MHz, 10 MHz and 15 MHz frequencies use 10 kW of ERP.
# CHU transmits 3 kW signals on 3.33 and 14.67 MHz, and a 10 kW signal on 7.85 MHz
# declare list of these, will be used for finding most likely beacon
frequencies = [WWV2p5, WWV5, WWV10, WWV15, WWV20, WWV25, CHU3, CHU7, CHU14]
# add to that list tolerance ranges in each beacon's line (13 Jan 2019)
for line in frequencies:
    line.append(.99*line[1]) #lower bound for frequency recovery, 1% below nominal
    line.append(1.01*line[1])#upper bound, 1% above nominal.
#-----------------------------------------------------------------
# function to find most likely beacon given "frequencies" vector:
# modified 13 Jan 2019 to use precomputed tolerances
def find_freq(f):
# "Finds the WWV or CHU frequency nearest the given frequency"
# Counts occurances within the tolerance range, line[3] to line[4], of nominal frequencies
    for beacon in frequencies:
        if (beacon[3])<f and f<(beacon[4]): # f between the two tolerances
            beacon[2]+=1
#-----------------------------------------------------------------
# function to find most likely beacon frequency for this data file
def find_most_likely_freq(frequencies):
# each has its frequency and a count for the data points
    #now put the measured frequencies into bins associated witih beacons
    for i in data:
        find_freq(float(i[1]))    #measured frequency
#and check which bin has the most counts
    freq='' #will be the string name of most likely beacon
    maxCount=0
    for i in frequencies:
        if i[2] > maxCount:
            maxCount=i[2]
            freq=i[0]
    return(freq) #returns string of most likely beacon name

timestamped_tempfile=(PROCESSDIR + TEMPFILE) #with full path
#-------------------------------------------------------------------
#%
# Check to see if the file from yesterday exists; if not, exit the program
if (path.exists(timestamped_tempfile)):
    print('File ' + timestamped_tempfile + ' found!\nProcessing...')
else:
    print('File ' + timestamped_tempfile + ' not available.\nExiting disappointed...')
    sys.exit(0)
#-----------------------------------------------
#% #got here, so there's a file to be read.
#read in the .csv file

with open(timestamped_tempfile, 'r') as dataFile:
    dataReader=csv.reader(dataFile)
    data = list(dataReader)
#John's files have two header lines.
#pop them off

data.pop(0)
data.pop(0)

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
# this is the most likely frequency being monitoried in this file

frequency_label=find_most_likely_freq(frequencies)

# Diagnostic settings for forced frequency testing of days data
#frequency_label= 'WWV2p5'
#frequency_label= 'WWV5'
#frequency_label= 'WWV10'
#frequency_label= 'WWV15'
#frequency_label= 'WWV20'
#frequency_label= 'WWV25'
#frequency_label= 'CHU3'
#frequency_label= 'CHU7'
#frequency_label= 'CHU14'

print('Frequency Label Determination: '+frequency_label)
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

#% Check if the appropriate local directory exists; create it if need be
BEACONDIR_lcl=PROCESSDIR+frequency_label + '/'    #e.g., WWV5, CHU7, ...
if (path.exists(BEACONDIR_lcl)):
    print('Path Exists: ' + BEACONDIR_lcl)
else:
    print('Making New Path: ' + BEACONDIR_lcl)
    os.mkdir(BEACONDIR_lcl)			# create the directory
    os.chmod(BEACONDIR_lcl, mode=0o764)		# set permissions to 764

#%
# Copy the file to new directory under timestamped, beacon-stamped name
# File saved by FLDigi (with mods by N8OBJ in the analysis.cxx module) in format analysisYYMMDD.csv
FILENAME=yesterdaystr + '-' + frequency_label + '.csv'

shutil.copyfile(timestamped_tempfile, BEACONDIR_lcl+FILENAME)

#convert date format to John's filename format filename

#2.5MHz WWV
if (frequency_label == 'WWV2p5'):
	print('Decoded 2.5MHz WWV Beacon\n')
	beacon = '-WWV2p5.csv'
	WWV2p5dir = homepath + 'WWVdata/WWV2p5/'
	yesterdayfile=WWV2p5dir + yesterdaystr + beacon

#5MHz WWV
elif (frequency_label == 'WWV5'):
	print('Decoded 5MHz WWV Beacon\n')
	beacon='-WWV5.csv'
	WWV5dir = homepath + 'WWVdata/WWV5/'
	yesterdayfile=WWV5dir + yesterdaystr + beacon

#10MHz WWV
elif (frequency_label == 'WWV10'):
	print('Decoded 10MHz WWV Beacon\n')
	beacon='-WWV10.csv'
	WWV10dir = homepath + 'WWVdata/WWV10/'
	yesterdayfile=WWV10dir + yesterdaystr + beacon

#15MHz WWV
elif (frequency_label == 'WWV15'):
	print('Decoded 15MHz WWV Beacon\n')
	beacon='-WWV15.csv'
	WWV15dir = homepath + 'WWVdata/WWV15/'
	yesterdayfile=WWV15dir + yesterdaystr + beacon

#20MHz WWV
elif (frequency_label == 'WWV20'):
        print('Decoded 20MHz WWV Beacon\n')
        beacon='-WWV20.csv'
        WWV20dir = homepath + 'WWVdata/WWV20/'
        yesterdayfile=WWV20dir + yesterdaystr + beacon

#25MHz WWV
elif (frequency_label == 'WWV25'):
        print('Decoded 25MHz WWV Beacon\n')
        beacon='-WWV25.csv'
        WWV25dir = homepath + 'WWVdata/WWV25/'
        yesterdayfile=WWV25dir + yesterdaystr + beacon

# CHU - 3.33, 7.85, and 14.67 MHz

#3.33MHz CHU
elif (frequency_label == 'CHU3'):
        print('Decoded 3.33MHz CHU Beacon\n')
        beacon='-CHU3.csv'
        CHU3dir = homepath + 'WWVdata/CHU3/'
        yesterdayfile=CHU3dir + yesterdaystr + beacon

#7.85MHz CHU
elif (frequency_label == 'CHU7'):
        print('Decoded 7.85MHz CHU Beacon\n')
        beacon='-CHU7.csv'
        CHU7dir = homepath + 'WWVdata/CHU7/'
        yesterdayfile=CHU7dir + yesterdaystr + beacon

#14.67MHz CHU
elif (frequency_label == 'CHU14'):
        print('Decoded 14.67MHz CHU Beacon\n')
        beacon='-CHU14.csv'
        CHU14dir = homepath + 'WWVdata/CHU14/'
        yesterdayfile=CHU14dir + yesterdaystr + beacon

#%
# Check to see if the file from yesterday exists; if not, exit the program
if (os.path.exists(yesterdayfile)):
    print('File '  + yesterdayfile +   ' found.\nProcessing...')
else:
    print('File ' + yesterdayfile + ' not available.\nExiting VERY Disappointed! ...')
    sys.exit(0)

#% #got here, so there's a file to be read.
#read in the .csv file

with open(yesterdayfile, 'r') as dataFile:
    dataReader=csv.reader(dataFile)
    data = list(dataReader)

#John's files have two header lines.
#Read first header line --- extract PlotDate, OrgName, FreqStd, Lat, Long, Alt data
Header1 = data.pop(0)
#hdr1str = Header1.__str__()

Header2 = data.pop(0)
#hdr2str = Header2.__str__()

#Diagnostic printout
#print('\n' + 'Header1 = ' + hdr1str + '\n')
#print('\n' + 'Header2 = ' + hdr2str + '\n')

PlotDate = Header1[0]
OrgName = Header1[1]
FreqStd = Header1[2]
Lat = Header1[3]
Lon = Header1[4]
Alt = Header1[5]

#Diagnostic printout
#print('PlotDate = ' + PlotDate + '\n')
#print('OrgName =  ' + OrgName + '\n')
#print('FreqStd =  ' + FreqStd + '\n')
#print('Lat =  ' + Lat + '\n')
#print('Long =  ' + Lon + '\n')
#print('Alt =  ' + Alt + '\n')

# Prepare data arrays
hours=[]
Doppler=[]
Power_dB=[] # will be second data set, received power 9I20
LateHour=False # flag for loop going past 23:00 hours
for row in data:
    decHours=time_string_to_decimals(row[0])
    if decHours > 23:
        LateHour=True # went past 23:00 hours
    if (not LateHour) or (LateHour and (decHours>23)): # Otherwise past 23:59:59.  Omit time past midnight.
        hours.append(decHours) # already in float because of conversion to decimal hours.
        Doppler.append(float(row[2])) # frequency offset column as analysis.cxx is writing it
        Power_dB.append (float(row[4])) # 9I20 last column of analysis.csv, log power

# Find max and min of Power_dB for graph preparation:
min_power=np.amin(Power_dB) # will use for graph axis min
max_power=np.amax(Power_dB) # will use for graph axis max
print('dB min: ', min_power, '; dB max: ', max_power)

#%% Create an order 3 lowpass butterworth filter.
# This is a digital filter (analog=False)
# Filtering at .01 to .004 times the Nyquist rate seems "about right."
# The filtering argument (Wn, the second argument to butter()) of.01
# represents filtering at .05 Hz, or 20 second weighted averaging.
# That corresponds with the 20 second symmetric averaging window used in the 1 October 2019
# Excel spreadsheet for the Festival of Frequency Measurement data.
FILTERBREAK=.005 #filter breakpoint in Nyquist rates. N. rate here is 1/sec, so this is in Hz.
FILTERORDER=6
b, a = butter(FILTERORDER, FILTERBREAK, analog=False, btype='low')
#print (b, a)
#%%
# Use the just-created filter coefficients for a noncausal filtering (filtfilt is forward-backward noncausal)

#print ('Filter Doppler shift data')
filtDoppler = filtfilt(b, a, Doppler)

#print ('Filter power data')
filtPower = filtfilt(b, a, Power_dB)

##%% modified from "Double-y axis plot,
## http://kitchingroup.cheme.cmu.edu/blog/2013/09/13/Plotting-two-datasets-with-very-different-scales/
#
fig = plt.figure(figsize=(19,10)) # inches x, y with 72 dots per inch
ax1 = fig.add_subplot(111)
ax1.plot(hours, filtDoppler, 'k') # color k for black
ax1.set_xlabel('UTC Hour')
ax1.set_ylabel('Doppler shift, Hz')
ax1.set_xlim(0,24) # UTC day
ax1.set_ylim([-1, 1]) # -1 to 1 Hz for Doppler shift
#
ax2 = ax1.twinx()
ax2.plot(hours, filtPower, 'r-')  # NOTE: Set for filtered version
ax2.set_ylabel('Power in relative dB', color='r')
ax2.set_ylim(-80, 0) #Try these as defaults to keep graphs similar.
# following lines set ylim for power readings in file
#ax2.set_ylim(min_power, max_power) #as determined above for this data set
for tl in ax2.get_yticklabels():
    tl.set_color('r')
#
#2.5MHz WWv
if (frequency_label == 'WWV2p5'):
	print('Final Plot for Decoded 2.5MHz WWV Beacon\n')
	plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n WWV 2.5 MHz   ' + PlotDate)
	plt.savefig(WWV2p5dir + yesterdaystr + 'WWV2p5_graph.png', dpi=250, orientation='landscape')
	graph_file=WWV2p5dir + yesterdaystr + 'WWV2p5_graph.png'

#5MHz WWV
elif (frequency_label == 'WWV5'):
	print('Final Plot for Decoded 5MHz WWV Beacon\n')
	plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n WWV 5 MHz   ' + PlotDate)
	plt.savefig(WWV5dir + yesterdaystr + 'WWV5_graph.png', dpi=250, orientation='landscape')
	graph_file=WWV5dir + yesterdaystr + 'WWV5_graph.png'
#10MHz WWV
elif (frequency_label == 'WWV10'):
	print('Final Plot for Decoded 10MHz WWV Beacon\n')
	plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n WWV 10 MHz   ' + PlotDate)
	plt.savefig(WWV10dir + yesterdaystr + 'WWV10_graph.png', dpi=250, orientation='landscape')
	graph_file=WWV10dir + yesterdaystr + 'WWV10_graph.png'
#15MHz WWV
elif (frequency_label == 'WWV15'):
	print('Final Plot for Decoded 15MHz WWV Beacon\n')
	plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n WWV 15 MHz   ' + PlotDate)
	plt.savefig(WWV15dir + yesterdaystr + 'WWV15_graph.png', dpi=250, orientation='landscape')
	graph_file=WWV15dir + yesterdaystr + 'WWV15_graph.png'
#20MHz WWV
if (frequency_label == 'WWV20'):
        print('Final Plot for Decoded 20MHz WWV Beacon\n')
        plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n WWV 20 MHz   ' + PlotDate)
        plt.savefig(WWV20dir + yesterdaystr + 'WWV20_graph.png', dpi=250, orientation='landscape')
        graph_file=WWV20dir + yesterdaystr + 'WWV20_graph.png'

#25MHz WWV
elif (frequency_label == 'WWV25'):
        print('Final Plot for Decoded 25MHz WWV Beacon\n')
        plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n WWV 25 MHz   ' + PlotDate)
        plt.savefig(WWV25dir + yesterdaystr + 'WWV25_graph.png', dpi=250, orientation='landscape')
        graph_file=WWV25dir + yesterdaystr + 'WWV25_graph.png'

#3.33MHz CHU
if (frequency_label == 'CHU3'):
        print('Final Plot for Decoded 3.33MHz CHU Beacon\n')
        plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n CHU 3.330 MHz   ' + PlotDate)
        plt.savefig(CHU3dir + yesterdaystr + 'CHU3_graph.png', dpi=250, orientation='landscape')
        graph_file=CHU3dir + yesterdaystr + 'CHU3_graph.png'

#7.85MHz CHU
elif (frequency_label == 'CHU7'):
        print('Final Plot for Decoded 7.85MHz CHU Beacon\n')
        plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n CHU 7.850 MHz   ' + PlotDate)
        plt.savefig(CHU7dir + yesterdaystr + 'CHU7_graph.png', dpi=250, orientation='landscape')
        graph_file=CHU7dir + yesterdaystr + 'CHU7_graph.png'

#14.67MHz CHU
elif (frequency_label == 'CHU14'):
        print('Final Plot for Decoded 14.67MHz CHU Beacon\n')
        plt.title('HF Beacon Doppler Shift Plot for:  ' + OrgName + ' \nLat= ' + Lat + '    Long= ' + Lon + '    Elv= ' + Alt + ' M\n CHU 14.670 MHz   ' + PlotDate)
        plt.savefig(CHU14dir + yesterdaystr + 'CHU14_graph.png', dpi=250, orientation='landscape')
        graph_file=CHU14dir + yesterdaystr + 'CHU14_graph.png'

# =============================================================================

#%%

print('Plot File: ' + graph_file + '\n')

# -F flag in feh is for full-screen
#os.system('feh -F -Z ' + graph_file)

#use std web browser to display day's data
#os.system('chromium-browser ' + graph_file)

#try webbrowser call instead:
#new=2 opens the file in a new tab
#webbrowser.open(graph_file, new=2)

subprocess.call('gpicview ' + graph_file +' &', shell=True)
print('Exiting python combined processing program gracefully')
