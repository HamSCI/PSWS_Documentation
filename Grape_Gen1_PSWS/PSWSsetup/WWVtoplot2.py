#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon July 4 2020
File input driven Beacon (WWV / CHU) plotting of multiple input fomats
Reads file ~/PSWS/Srawdata/toplot for files to process

@author jgibbons
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
from WWV_utility import time_string_to_decimals, graph_Doppler_and_power_data
import maidenhead as mh

# ~ points to users home directory - usually /home/pi/
homepath = os.path.expanduser('~')
# imbed the trailing / in the home path
homepath = homepath + "/PSWS/"
#print('Home Path = ' + homepath)

# Procees directory for raw file storage
PROCESSDIR = homepath + 'Srawdata/'

#directories for temp storing processed data files
DATADIR = homepath + 'Stemp/'

#saved data directrory
SAVEDIR = homepath + 'Sdata/'

#saved data directrory
PlotDIR = homepath + 'Splot/'

InfoDir = homepath + 'Sinfo/'
#print('InfoDir = ' + InfoDir)

InFile = homepath + 'Srawdata/toplot'
DoneFile = homepath + 'Srawdata/toplot.done'
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
# see if file containing list of files to process exists
# By default, this file it called "toplot"
# Check to see if the file from yesterday exists; if not, exit the program
if (path.exists(InFile)):
    print('File ' + InFile + ' - List of files found!\n')
else:
    print('File ' + InFile + ' not available.\nExiting disappointed...')
    sys.exit(0)


#sys.exit(0)
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
# Grab saved station info if it exists

#Grab station Node Number
NodePath = InfoDir + "NodeNum.txt"
with open(NodePath, 'r') as NodeFile:
    Snode = NodeFile.readline()
    NodeFile.close()
    Snode = Snode[:-1]
    print('Sinfo Node =', Snode)

#Grab City State
CSPath = InfoDir + "CityState.txt"
with open(CSPath, 'r') as CSFile:
    SCityState = CSFile.readline()
    CSFile.close()
    SCityState = SCityState[:-1]
    print('Sinfo CityState =', SCityState)

#Grab Grid Square
GSPath = InfoDir + "GridSqr"
with open(GSPath, 'r') as GSFile:
    SGridsqr = GSFile.readline()
    GSFile.close()
    SGridsqr = SGridsqr[:-1]
    print('Sinfo Gridsqr =', SGridsqr)

#Grab Lat Long Elv
LLEPath = InfoDir + "LatLonElv.txt"
with open(LLEPath, 'r') as LLEFile:
    SLatLonElv = LLEFile.readline()
    LLEFile.close()
    SLatLonElv = SLatLonElv[:-1]
    print('Sinfo LatLonElv =', SLatLonElv)

#Grab RadioID
RIDPath = InfoDir + "Radio1ID.txt"
with open(RIDPath, 'r') as RIDFile:
    SRID = RIDFile.readline()
    RIDFile.close()
    SRID = SRID[:-1]
    print('Sinfo RadioID =', SRID)

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#Found list of files file, start processing it
#InFile = homepath + 'Srawdata/toplot'
plotlistfile = open(InFile, "r")
for nfile in plotlistfile:
    # next file is in nfile - create  full pathname
    print('File=', nfile)
    # eliminate \n char from end of string for file to open
    filetopen = nfile[:18] # full name with extension
    filetoname = nfile[:14] # clip off .csv extension
    
    #create full path to file to read
    filetoread = PROCESSDIR + filetopen
    
    #update file name
    yesterdaystr = filetoname
    #point to the next file to process with full path
    yesterdayfile = filetoread
   
    # open next file to process
    #f2p = open(ftr, "r")

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

   
    #-------------------------------------------------------------------
    # Check to see if the file from yesterday exists; if not, exit the program
    if (path.exists(yesterdayfile)):
        print('File ' + yesterdayfile + ' found    Processing...')
    else:
        print('File ' + yesterdayfile + ' not available.\nExiting disappointed...')
        plotlistfile.close()
        sys.exit(0)
    #-----------------------------------------------

    #% #got here, so there's a file to be read.
    #read in the .csv file

    with open(yesterdayfile, 'r') as dataFile:
        dataReader=csv.reader(dataFile)
        data = list(dataReader)
        Header = data.pop(0)

        #Figure out which header format reading
        NewHdr = 'unknown'
        #print('Header to check=',Header)
        # Check if First header line is of new format example
        #,2020-05-16T00:00:00Z,N00001,EN91fh,41.3219273, -81.5047731, 284.5,Macedonia Ohio,G1,WWV5
        if (Header[0] == "#"):
            print('New Header String Detected')
            # Have new header format - pull the data fields out
            UTCDTZ = Header[1]
            #UTCDTZ=UTCDTZ.replace(':','') # remove the semicolons
            #print('UTCDTZ =', UTCDTZ)
            node= Header[2]
            #print('Node =', node)
            GridSq = Header[3]
            #print('GridSq =', GridSq)
            Lat = Header[4]
            #print('Lat =', Lat)
            Long = Header[5]
            #print('Long =', Long)
            Elv = Header[6]
            #print('Elev =', Elv)
            citystate = Header[7]
            #print('City State =', citystate)
            radioid = Header[8]
            #print('Radio ID =', radioid)
            beacon = Header[9]
            #print('Beacon =', beacon)
            NewHdr = 'New'
            

        # Try using original FLdigi format w/o info line fake all data
        if (Header[0] == "UTC"):
            print('Detected Original FLDigi Header Format')
            UTCDTZ = "2020-00-00T00:00:00Z"
            node= "N00000"
            Lat = '00.00000'
            Long = '-00.00000'
            Elv = '000'
            GridSq = mh.to_maiden(float(Lat), float(Long))
            print('GridSq =', GridSq)
            citystate = 'NOcity NOstate'
            radioid = 'UU'
            beacon = "unknown"
            NewHdr = 'FLDigi'

        if (NewHdr == 'unknown'):
            ChkDate = Header[0]  # load in first row entry
            Cent = ChkDate[:2] # check first 2 digits  = 20?
            print( ChkDate, 'Yields century of', Cent)  # diag printout

            if  Cent == "20":
                print('Old Header String Detected')
                # Have old header format - pull the data fields out
                #2020-05-15,N8OBJ Macedonia Ohio EN91fh,LB GPSDO,41.3219273, -81.5047731, 284.5
                UTCDTZ = Header[0]
                #UTCDTZ=UTCDTZ.replace(':','') # remove the semicolons
                #print('UTCDTZ =', UTCDTZ)
                #get this stations Node #
                Lat = Header[3]
                #print('Lat =', Lat)
                Long = Header[4]
                #print('Long =', Long)
                Elv = Header[5]
                #print('Elev =', Elv)
                GridSq = mh.to_maiden(float(Lat), float(Long))
                #print('GridSq =', GridSq)
                citystate = Header[1]
                #print('City State =', citystate)
                radioid = 'G1'
                #print('Radio ID =', radioid)
                beacon = "unknown"
                print('Beacon =', beacon)
                NewHdr = 'Old'
            
        #sys.exit(0)   
        # Diagnostic settings for forced frequency testing of days data
        #beacon= 'WWV2p5'
        #beacon= 'WWV5'
        #beacon= 'WWV10'
        #beacon= 'WWV15'
        #beacon= 'WWV20'
        #beacon= 'WWV25'
        #beacon= 'CHU3'
        #beacon= 'CHU7'
        #beacon= 'CHU14'
        print('Header Decode =',NewHdr)
        #print('Scanning for UTC header line')

    if (NewHdr == 'unknown'):
        print('Unknown File header Structure - Aborting!')
        sys.exit(0)

    print('Ready to start processing records')
    #sys.exit(0)
    # Prepare data arrays
    hours=[]
    Doppler=[]
    Vpk=[]
    Power_dB=[] # will be second data set, received power 9I20
    LateHour=False # flag for loop going past 23:00 hours

    # eliminate all metadata saved at start of file - Look for UTC (CSV headers)
    if (NewHdr != 'FLDigi'):
        #find first row of data0
        FindUTC = 0
        for row in data:
            if (FindUTC == 0):
                #print('looking for UTC - row[0] =',row[0])
                if (row[0] == 'UTC'):
                    FindUTC = 1
                    #print('UTC found =', row[0])
            else:
                #print('Processing record')
                decHours=time_string_to_decimals(row[0])
                if decHours > 23:
                    LateHour=True # went past 23:00 hours
                if (not LateHour) or (LateHour and (decHours>23)): # Otherwise past 23:59:59.  Omit time past midnight.
                    hours.append(decHours) # already in float because of conversion to decimal hours.
                    Doppler.append(float(row[2])) # frequency offset from col 2
                    Vpk.append (float(row[3])) # Get Volts peak from col 3
                    Power_dB.append (float(row[4])) # log power from col 4
    if (NewHdr == 'FLDigi'):
        for row in data:
            decHours=time_string_to_decimals(row[0])
            if decHours > 23:
                LateHour=True # went past 23:00 hours
            if (not LateHour) or (LateHour and (decHours>23)): # Otherwise past 23:59:59.  Omit time past midnight.
                hours.append(decHours) # already in float because of conversion to decimal hours.
                Doppler.append(float(row[2])) # frequency offset from col 2
                Vpk.append (float(row[3])) # Get Volts peak from col 3
                Power_dB.append (float(row[4])) # log power from col 4

    # Find max and min of Power_dB for graph preparation:
    min_power=np.amin(Power_dB) # will use for graph axis min
    max_power=np.amax(Power_dB) # will use for graph axis max
    min_Vpk=np.amin(Vpk) # min Vpk
    max_Vpk=np.amax(Vpk) # max Vpk
    min_Doppler=np.amin(Doppler) # min Doppler
    max_Doppler=np.amax(Doppler) # max Doppler

    print('File records all read in - Stats:')
    print('Doppler min: ', min_Doppler, '; Doppler max: ', max_Doppler)
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
    FILTERBREAK=0.99 #filter breakpoint in Nyquist rates. N. rate here is 1/sec, so this is in Hz.
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
    #
    fig = plt.figure(figsize=(19,10)) # inches x, y with 72 dots per inch
    ax1 = fig.add_subplot(111)
    ax1.plot(hours, filtDoppler, 'k') # color k for black
    ax1.set_xlabel('UTC Hour')
    ax1.set_ylabel('Doppler shift, Hz')
    ax1.set_xlim(0,24) # UTC day
    ax1.set_ylim([-.2, .2]) # -1 to 1 Hz for Doppler shift
    #
    ax2 = ax1.twinx()
    ax2.plot(hours, filtPower, 'r-')  # NOTE: Set for filtered version
    ax2.set_ylabel('Power in relative dB', color='r')
    ax2.set_ylim(-80, 0) #Try these as defaults to keep graphs similar.
    # following lines set ylim for power readings in file
    #ax2.set_ylim(min_power, max_power) #as determined above for this data set
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
        
    #PlotDIR = homepath + 'Splot/'
    #2.5MHz WWv
    if (beacon == 'WWV2p5'):
        print('Final Plot for Decoded 2.5MHz WWV Beacon\n')
        plt.title('WWV 2.5 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  ' + GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_WWV2p5_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_WWV2p5_graph.png'

    #5MHz WWV
    elif (beacon == 'WWV5'):
        print('Final Plot for Decoded 5MHz WWV Beacon\n')
        plt.title('WWV 5 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_WWV5_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_WWV5_graph.png'
    #10MHz WWV
    elif (beacon == 'WWV10'):
        print('Final Plot for Decoded 10MHz WWV Beacon\n')
        plt.title('WWV 10 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_WWV10_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_WWV10_graph.png'
    #15MHz WWV
    elif (beacon == 'WWV15'):
        print('Final Plot for Decoded 15MHz WWV Beacon\n')
        plt.title('WWV 15 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_WWV15_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_WWV15_graph.png'
    #20MHz WWV
    if (beacon == 'WWV20'):
        print('Final Plot for Decoded 20MHz WWV Beacon\n')
        plt.title('WWV 20 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_WWV20_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_WWV20_graph.png'

    #25MHz WWV
    elif (beacon == 'WWV25'):
        print('Final Plot for Decoded 25MHz WWV Beacon\n')
        plt.title('WWV 25 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_WWV25_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_WWV25_graph.png'

    #3.33MHz CHU
    if (beacon == 'CHU3'):
        print('Final Plot for Decoded 3.33MHz CHU Beacon\n')
        plt.title('CHU 3.330 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_CHU3_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_CHU3_graph.png'

    #7.85MHz CHU
    elif (beacon == 'CHU7'):
        print('Final Plot for Decoded 7.85MHz CHU Beacon\n')
        plt.title('CHU 7.850 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_CHU7_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_CHU7_graph.png'

    #14.67MHz CHU
    elif (beacon == 'CHU14'):
        print('Final Plot for Decoded 14.67MHz CHU Beacon\n')
        plt.title('CHU 14.670 MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_CHU14_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_CHU14_graph.png'

    elif (beacon == 'unknown'):
        print('Final Plot for Decoded Unknown Beacon\n')
        plt.title('Unknown MHz Doppler Shift Plot\nNode:  ' + node + '     Gridsquare:  '+ GridSq + '\nLat= ' + Lat + '    Long= ' + Long + '    Elv= ' + Elv + ' M\n UTC:    ' + UTCDTZ)
        plt.savefig(PlotDIR + yesterdaystr + '_unknown_graph.png', dpi=250, orientation='landscape')
        graph_file=PlotDIR + yesterdaystr + '_unknown_graph.png'

    # =============================================================================

    print('Plot File: ' + graph_file + '\n')
    
    #close processed file
    dataFile.close()
    
#subprocess.call('gpicview ' + graph_file +' &', shell=True)
# close the plot list input file
plotlistfile.close()

#indicate this file has been processed
#DoneFile = homepath + 'Srawdata/toplot.done'
shutil.move(InFile, DoneFile)

#tell user what just happened
print('\nFinished processing toplot file - adding .done to indicate processing complete\n')
print('File is now ' + OutFile)
print('\n\nParking Python Plotting Program Peacefully\n')
