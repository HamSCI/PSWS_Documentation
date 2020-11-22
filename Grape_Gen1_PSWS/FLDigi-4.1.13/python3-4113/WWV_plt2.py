#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon July 1 2020
Full Beacon (WWV / CHU) plotting of 2 input fomats
added hours ticks, removed time from UTC dat in header, added zero ref line for doppler freq shift, Elv now Elev  7-31=20 JCG
added autoplot capability 11/21/20 jgibbons
@authors dkazdan jgibbons
"""


import os
from os import path
import sys
import csv
from datetime import date, timedelta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import legend, show, grid, figure, savefig
from scipy.signal import filtfilt, butter
import subprocess
from WWV_utility2 import time_string_to_decimals, graph_Doppler_and_power_data
import maidenhead as mh

# ~ points to users home directory - usually /home/pi/
homepath = os.path.expanduser('~')
# imbed the trailing / in the home path
homepath = homepath + "/PSWS/"
print('Home Path = ' + homepath)

PROCESSDIR = homepath + 'Srawdata/'

#directories for temp storing processed data files
DATADIR = homepath + 'Stemp/'

#saved data directrory
SAVEDIR = homepath + 'Sdata/'

#saved data directrory
PlotDIR = homepath + 'Splot/'

InfoDir = homepath + 'Sinfo/'
#print('InfoDir = ' + InfoDir)

autoplotfile = homepath + 'Scmd/autoplot'
#print('AutoPlot file path = ' + autoplotfile)


#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
# Normal date creation for file to be processed
#
# Find numerical version of today in N8OBJ format
today=date.today()

# And from that, of yesterday
yesterday=today-timedelta(1) #create yesterday's date

# Then turn it into a string of appropriate format
yesterdaystr=yesterday.__str__() #yesterday's date in string form, ISO format

#convert date format filename
Olddate=yesterdaystr[2:] #removes first two digits of year
Olddate=Olddate.replace('-','') #4emove the hyphens

# Hard force of date to plot - for debug purposes
#Olddate ='200729'  # fake the date - force this date

#create filename in correct format
TEMPFILE='analysis' + Olddate + '.csv' #filename format

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------


#            - - - - OR - - - -

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
# This is a MANUAL FORCED OVERRIDE find of the file to be graphed
#TEMPFILE='analysis200729.csv'  # newest format with full ISO timestamp - force file

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

yesterdayfile=(PROCESSDIR + TEMPFILE) #with full path

#-------------------------------------------------------------------
# Check to see if the file from yesterday exists; if not, exit the program
if (path.exists(yesterdayfile)):
    print('File ' + yesterdayfile + ' found!\nProcessing...')
else:
    print('File ' + yesterdayfile + ' not available.\nExiting disappointed...')
    sys.exit(0)
#-----------------------------------------------

#% #got here, so there's a file to be read.
#read in the .csv file

# make sure Sinfo file exists - if not, create obvious fake data
#if (path.exists(SaveDataDirBeacon)):
#    print('Target Dir exists as', SaveDataDirBeacon)
#else:
#    print('Target Dir NOT there - making path ' + SaveDataDirBeacon)
#    os.mkdir(SaveDataDirBeacon)           # create tyhe directory
#    os.chmod(SaveDataDirBeacon, mode=0o764)   # set the permissions to 764

#Grab station Node Number
NodePath = InfoDir + "NodeNum.txt"
with open(NodePath, 'r') as NodeFile:
    Snode = NodeFile.readline() # read first line of file
    NodeFile.close()
    Snode = Snode[:-1] # remove <lf>
    #print('Sinfo Node =', Snode)

#Grab City State
CSPath = InfoDir + "CityState.txt"
with open(CSPath, 'r') as CSFile:
    SCityState = CSFile.readline() # read first line of file
    CSFile.close()
    SCityState = SCityState[:-1] # remove <lf>
    #print('Sinfo CityState =', SCityState)

#Grab Grid Square
GSPath = InfoDir + "GridSqr"
with open(GSPath, 'r') as GSFile:
    SGridsqr = GSFile.readline() # read first line of file
    GSFile.close()
    SGridsqr = SGridsqr[:-1] # remove <lf>
    #print('Sinfo Gridsqr =', SGridsqr)

#Grab Lat Long Elev
LLEPath = InfoDir + "LatLonElv.txt"
with open(LLEPath, 'r') as LLEFile:
    SLatLonElv = LLEFile.readline() # read first line of file
    LLEFile.close()
    SLatLonElv = SLatLonElv[:-1] # remove <lf>
    #print('Sinfo LatLonElv =', SLatLonElv)

#Grab RadioID
RIDPath = InfoDir + "Radio1ID.txt"
with open(RIDPath, 'r') as RIDFile:
    SRID = RIDFile.readline() # read first line of file
    RIDFile.close()
    SRID = SRID[:-1] # remove <lf>
    #print('Sinfo RadioID =', SRID)


with open(yesterdayfile, 'r') as dataFile:
    dataReader=csv.reader(dataFile)
    data = list(dataReader)
    Header = data.pop(0)

    #Figure out which header format reading
    NewHdr = 'Unknown'
    print('Header to check=',Header)
    # Check if First header line is of new format example
    #,2020-05-16T00:00:00Z,N00001,EN91fh,41.3219273, -81.5047731, 284.5,Macedonia Ohio,G1,WWV5
    if (Header[0] == "#"):
        print('New Header String Detected')
        # Have new header format - pull the data fields out
        NewHdr = 'New'
         
        UTCDTZ = Header[1]
        #print('UTCDTZ Header from file read = ' + UTCDTZ)
        
        UTC_DT = UTCDTZ[:10] # Strip off time and ONLY keep UTC Date
        #print('UTC_DT = ' + UTC_DT)
        
        #UTCDTZ=UTCDTZ.replace(':','') # remove the semicolons
#        print('UTCDTZ =', UTCDTZ)
        node= Header[2]
#        print('Node =', node)
        GridSqr = Header[3]
#        print('GridSqr =', GridSqr)
        Lat = Header[4]
#        print('Lat =', Lat)
        Long = Header[5]
#        print('Long =', Long)
        Elev = Header[6]
#        print('Elev =', Elev)
        citystate = Header[7]
#        print('City State =', citystate)
        RadioID = Header[8]
#        print('Radio ID =', RadioID)
        beacon = Header[9]
#        print('Beacon =', beacon)
       

    # Try using original FLdigi format w/o info line fake all data
#    if (Header[0] == "UTC"):
#        print('Detected Original FLDigi Header Format')
#        UTCDTZ = "2020-00-00T00:00:00Z"
#        node= "N00000"
#        Lat = '00.00000'
#        Long = '-00.00000'
#        Elev = '000'
#        print('GridSqr =', GridSqr)
#        citystate = 'NOcity NOstate'
#        RadioID = SRID
#        beacon = "Unknown"
#        NewHdr = 'FLDigi'

    if (NewHdr == 'Unknown'):
        ChkDate = Header[0]  # load in first row entry
        Cent = ChkDate[:2] # check first 2 digits  = 20?
        print( ChkDate, 'Header Yields Century of', Cent)  # diag printout

        if  Cent == "20":
            print('Old Header String Detected')
            # Have old header format - pull the data fields out
            #2020-05-15,N8OBJ Macedonia Ohio EN91fh,LB GPSDO,41.3219273, -81.5047731, 284.5
            UTCDTZ = Header[0]
            UTC_DT = UTCDTZ[:10] # Strip off time and ONLY keep UTC Date
            UTCDTZ=UTCDTZ.replace(':','') # remove the semicolons
            print('UTCDTZ =', UTCDTZ)
            #get this stations Node #
            Lat = Header[3]
            #print('Lat =', Lat)
            Long = Header[4]
            #print('Long =', Long)
            Elev = Header[5]
            #print('Elev =', Elev)
            GridSqr = mh.to_maiden(float(Lat), float(Long))
            print('GridSqr =', GridSqr)
            citystate = Header[1]
            #print('City State =', citystate)
            RadioID = 'G1'
            #print('Radio ID =', RadioID)
#            beacon = "Unknown"
#            print('Beacon =', beacon)
            NewHdr = 'Old'
        
    #sys.exit(0)   
    # Diagnostic settings for forced frequency testing of days data
    #beacon = 'Unknown'
    #beacon = 'WWV2p5'
    #beacon = 'WWV5'
    #beacon = 'WWV10'
    #beacon = 'WWV15'
    #beacon = 'WWV20'
    #beacon = 'WWV25'
    #beacon = 'CHU3'
    #beacon = 'CHU7'
    #beacon = 'CHU14'
    
    print('Header Decode =',NewHdr)
    #print('Scanning for UTC header line')

if (NewHdr == 'Unknown'):
    print('Unknown File header Structure - Aborting!')
    sys.exit(0)
#sys.exit(0)
print('Ready to start processing records')
#sys.exit(0)
# Prepare data arrays
hours=[]
Doppler=[]
Vpk=[]
Power_dB=[] # will be second data set, received power 9I20
LateHour=False # flag for loop going past 23:00 hours

# eliminate all metadata saved at start of file - Look for UTC (CSV headers)
#find first row of data0
FindUTC = 0
recordcnt  = 0
freqcalc = 0
calccnt = 0

for row in data:
    if (FindUTC == 0):
        #print('looking for UTC - row[0] =',row[0])
        if (row[0] == 'UTC'):
            FindUTC = 1
#            print('UTC found =', row[0])
    else:
        #print('Processing record')
        decHours=time_string_to_decimals(row[0])
        if (NewHdr != 'New'):
            if (calccnt  < 101):
                calcnt = calcnt+1
                freqcalc = freqcalc + (float(row[1])/100)
        if decHours > 23:
            LateHour=True # went past 23:00 hours
        if (not LateHour) or (LateHour and (decHours>23)): # Otherwise past 23:59:59.  Omit time past midnight.
            hours.append(decHours) # already in float because of conversion to decimal hours.
            Doppler.append(float(row[2])) # frequency offset from col 2
            Vpk.append (float(row[3])) # Get Volts peak from col 3
            Power_dB.append (float(row[4])) # log power from col 4


if (NewHdr != 'New'):

#    CalcFreq = freqcalc / 10   ding /10 i=n calculation now
#    print("Average of 1st 10 measured frequencies = ", CalcFreq)

    #Create integer rep for analysis (add offset to get correct rounding)
    CalcFrqNum = int((CalcFreq+100)/10000)
    print('CalcFreqNum =',CalcFrqNum)

    #Figure out the beacon ID from 1st 10 lines of data in file

    # have it default to Unknown
    beacon = "Unknown";
    
    if (CalcFrqNum == 250):
        beacon = "WWV2p5"
       
    if (CalcFrqNum == 500):
        beacon = "WWV5"
        
    if (CalcFrqNum == 1000):
        beacon = "WWV10"
        
    if (CalcFrqNum == 1500):
        beacon = "WWV15"
        
    if (CalcFrqNum == 2000):
        beacon = "WWV20"
        
    if (CalcFrqNum == 2500):
        beacon = "WWV25"
        
    if (CalcFrqNum == 333):
        beacon = "CHU3"
        
    if (CalcFrqNum == 785):
        beacon = "CHU7"
        
    if (CalcFrqNum == 1467):
        beacon = "CHU14"
        
    print('Calc Beacon ID =',beacon)

# Find max and min of Power_dB for graph preparation:
min_power=np.amin(Power_dB) # will use for graph axis min
max_power=np.amax(Power_dB) # will use for graph axis max
min_Vpk=np.amin(Vpk) # min Vpk
max_Vpk=np.amax(Vpk) # max Vpk
min_Doppler=np.amin(Doppler) # min Doppler
max_Doppler=np.amax(Doppler) # max Doppler

print('\nDoppler min: ', min_Doppler, '; Doppler max: ', max_Doppler)
print('Vpk min: ', min_Vpk, '; Vpk max: ', max_Vpk)
print('dB min: ', min_power, '; dB max: ', max_power)
#sys.exit(0) 
 
#%% Create an order 3 lowpass butterworth filter.
# This is a digital filter (analog=False)
# Filtering at .01 to .004 times the Nyquist rate seems "about right."
# The filtering argument (Wn, the second argument to butter()) of.01
# represents filtering at .05 Hz, or 20 second weighted averaging.
# That corresponds with the 20 second symmetric averaging window used in the 1 October 2019
# Excel spreadsheet for the Festival of Frequency Measurement data.
#FILTERBREAK=.005 #filter breakpoint in Nyquist rates. N. rate here is 1/sec, so this is in Hz.
FILTERBREAK=0.005 #filter breakpoint in Nyquist rates. N. rate here is 1/sec, so this is in Hz.
FILTERORDER=6
b, a = butter(FILTERORDER, FILTERBREAK, analog=False, btype='low')
#print (b, a)
#%%
# Use the just-created filter coefficients for a noncausal filtering (filtfilt is forward-backward noncausal)

#print ('Filter Doppler shift data')
filtDoppler = filtfilt(b, a, Doppler)

#print ('Filter power data')
filtPower = filtfilt(b, a, Power_dB)
#sys.exit(0)
##%% modified from "Double-y axis plot,
## http://kitchingroup.cheme.cmu.edu/blog/2013/09/13/Plotting-two-datasets-with-very-different-scales/

# set up x-axis with time
fig = plt.figure(figsize=(19,10)) # inches x, y with 72 dots per inch
ax1 = fig.add_subplot(111)
ax1.plot(hours, filtDoppler, 'k') # color k for black
ax1.set_xlabel('UTC Hour')
ax1.set_ylabel('Doppler shift, Hz')
ax1.set_xlim(0,24) # UTC day
ax1.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24], minor=False)
ax1.set_ylim([-1.0, 1.0]) # -1 to 1 Hz for Doppler shift
# plot a zero freq reference line for 0.000 Hz Doppler shift
plt.axhline(y=0, color="gray", lw=1)
# set up axis 2 in red
ax2 = ax1.twinx()
ax2.plot(hours, filtPower, 'r-')  # NOTE: Set for filtered version
ax2.set_ylabel('Power in relative dB', color='r')
ax2.set_ylim(-90, 0) #Try these as defaults to keep graphs similar.
# following lines set ylim for power readings in file
#ax2.set_ylim(min_power, max_power) #as determined above for this data set
for tl in ax2.get_yticklabels():
    tl.set_color('r')

#2.5MHz WWv
if (beacon == 'WWV2p5'):
    print('Final Plot for Decoded 2.5MHz WWV Beacon\n')
    beaconlabel = 'WWV 2.5 MHz'

#5MHz WWV
elif (beacon == 'WWV5'):
    print('Final Plot for Decoded 5MHz WWV Beacon\n')
    beaconlabel = 'WWV 5 MHz'

#10MHz WWV
elif (beacon == 'WWV10'):
    print('Final Plot for Decoded 10MHz WWV Beacon\n')
    beaconlabel = 'WWV 10 MHz'
        
#15MHz WWV
elif (beacon == 'WWV15'):
    print('Final Plot for Decoded 15MHz WWV Beacon\n')
    beaconlabel = 'WWV 15 MHz'
        
#20MHz WWV
if (beacon == 'WWV20'):
    print('Final Plot for Decoded 20MHz WWV Beacon\n')
    beaconlabel = 'WWV 20 MHz'
        
#25MHz WWV
elif (beacon == 'WWV25'):
    print('Final Plot for Decoded 25MHz WWV Beacon\n')
    beaconlabel = 'WWV 25 MHz'
    
#3.33MHz CHU
if (beacon == 'CHU3'):
    print('Final Plot for Decoded 3.33MHz CHU Beacon\n')
    beaconlabel = 'CHU 3.330 MHz'
        
#7.85MHz CHU
elif (beacon == 'CHU7'):
    print('Final Plot for Decoded 7.85MHz CHU Beacon\n')
    beaconlabel = 'CHU 7.850'
        
#14.67MHz CHU
elif (beacon == 'CHU14'):
    print('Final Plot for Decoded 14.67MHz CHU Beacon\n')
    beaconlabel = 'CHU 14.670 MHz'
        
elif (beacon == 'Unknown'):
    print('Final Plot for Decoded Unknown Beacon\n')
    beaconlabel = 'Unknown Beacon'
    
#PlotDIR = homepath + 'Splot/'
# Create Plot Title
plt.title(beaconlabel + ' Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSqr + '\nLat= ' + Lat + '    Long= ' + Long + '    Elev= ' + Elev + ' M\n' + UTC_DT + '  UTC')

# Create Plot File Nam
graph_file = PlotDIR + yesterdaystr + '_' + node + '_' +  GridSqr + '_' +  RadioID + '_' +  beacon + '_graph.png'

# create plot
plt.savefig(PlotDIR + yesterdaystr + '_' + node + '_' +  GridSqr + '_' +  RadioID + '_' +  beacon + '_graph.png', dpi=250, orientation='landscape')
# =============================================================================

print('Plot File: ' + graph_file + '\n')  # indicate plot file name for crontab printout

#-------------------------------------------------------------------
# Check to see if the autoplot file exists; if not, skip the plot
if (path.exists(autoplotfile)):
    print('autoplot enable File found - Processing Plot...\n')
    subprocess.call('gpicview ' + graph_file +' &', shell=True)   #create shell and plot the data from graph file
else:
    print('No autoplot enable File found - exiting')
#-----------------------------------------------

#subprocess.call('gpicview ' + graph_file +' &', shell=True)   #create shell and plot the data from graph file

print('Exiting python combined processing program gracefully')
