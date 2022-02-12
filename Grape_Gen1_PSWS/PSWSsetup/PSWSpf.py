#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30, 2021
07-05-2020 Ver 0.10 - First working copy finished
08-08-2021 Ver 0.20 - using todo file for input
08-21-2021 Ver 0.21 - working on todo file reading and basic function
08-21-2021 Ver 0.22 - create new metadata header info
08-24-2021 Ver 0.23 - adding final output format w/multiple file input
09-13-2021 Ver 0.24 - Finished first pass and all is working
09-14-2021 Ver 0.25 - Added plotting processing as well
09-15-2021 Ver 0.26 - Saved original raw file and created new raw file with updates
02-11-2022 Ver 0.27 - optimized / fixed extraction of Lat Long Elev from Metadata File

WWV full file processing for (not old) and new format files
Null detection and removal / resequencing of time stamps
Old format fill-in of header info for data files being created

@author jcgibbons N8OBJ
"""

import os
from os import path
import sys
import shutil
import csv
from csv import reader
from datetime import date, timedelta
import maidenhead as mh
import fix_timestamps_after_crash
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import legend, show, grid, figure, savefig
from scipy.signal import filtfilt, butter
#import subprocess
from WWV_utility2 import time_string_to_decimals, graph_Doppler_and_power_data

#-------------------------------------------------
#-------------------------------------------------
print('WWV Beacon File Re-Processing Program - Ver 0.26')
print('************************************************\n')

#create and check paths
# Define users home directory path
HomePath = os.path.expanduser('~')
#print('Home Path = ' + HomePath)

ProcessDir = HomePath + '/PSWS/Srawdata/'
#print('ProcessDir = ' + ProcessDir)

# path to the todo file list
ToDoPath = HomePath + '/PSWS/Srawdata/todo'
#print('todo File path = ' + ToDoPath)

#directories for storing processed data files
TempDir = HomePath + '/PSWS/Stemp/'
#$print('TempDir = ' + TempDir)

InfoDir = HomePath + '/PSWS/Sinfo/'
#print('InfoDir = ' + InfoDir)

#directory for storing processed data files
SDataDir = HomePath + '/PSWS/Sdata/'
#print('SDataDir = ' + SDataDir)

#directory for storing processed plot files
PlotDir = HomePath + '/PSWS/Splot/'
#print('PlotDir = ' + PlotDir)

#directory for storing processed data files to be transferred
XferDataDir = HomePath + '/PSWS/Sxfer/'
#print('XferDataDir = ' + XferDataDir)

# flag file for auto transfer on / off
autoxferfile = HomePath + '/PSWS/Scmd/autoxfer'
#print('AutoXfer file path = ' + autoxferfile)

# flag file for auto plot transfer on / off
#autoplotfile = HomePath + '/PSWS/Scmd/autoplot'
#print('AutoXfer file path = ' + autoplotfile)

#-------------------------------------------------
#-------------------------------------------------
# VERIFY PATHS
# make sure both data path exists - if not, abort
if (path.exists(ProcessDir)):
    print('ProcessDir exists: ' + ProcessDir)
else:
    print('Exiting - No directory ', ProcessDir)
    sys.exit(0)

# make sure temp path exists - if not, abort
if (path.exists(TempDir)):
    print('TempDir exists: ' + TempDir)
else:
    print('Exiting - No directory ', TempDir)
    sys.exit(0)

# look for existance of todo file
# make sure temp path exists - if not, abort
if (path.exists(ToDoPath)):
    print('todo file exists: ' + ToDoPath)
else:
    print('No todo file - exiting mad! ', ToDoPath)
    sys.exit(0)

#-------------------------------------------------
#-------------------------------------------------
# Grab sys info from node database files
print("\nThis System's New Node Info:\n")

# THis section reads in all the Sinfo data that represents
# all of the current data that for this node

#Grab station Node Number - save in variable SNode
NodePath = InfoDir + "NodeNum.txt"
with open(NodePath, 'r') as NodeFile:
    SNode = NodeFile.readline()
    NodeFile.close()
    SNode = SNode[:-1] # remove <CR>
    print('Sinfo Node =', SNode)

#Grab Callsign - save in variable SCallsign
CallSPath = InfoDir + "CallSign.txt"
with open(CallSPath, 'r') as CSFile:
    SCallsign = CSFile.readline()
    CSFile.close()
    SCallsign = SCallsign[:-1] # remove <CR>
    print('Sinfo Callsign =', SCallsign)

#Grab City State - save in variable SCityState
CSPath = InfoDir + "CityState.txt"
with open(CSPath, 'r') as CSFile:
    SCityState = CSFile.readline()
    CSFile.close()
    SCityState = SCityState[:-1] # remove <CR>
    print('Sinfo CityState =', SCityState)

#Grab Grid Square - save in variable SGridsqr
GSqPath = InfoDir + "GridSqr"
with open(GSqPath, 'r') as GSqFile:
    SGridsqr = GSqFile.readline()
    GSqFile.close()
    SGridsqr = SGridsqr[:-1] # remove <CR>
    print('Sinfo Gridsqr =', SGridsqr)

#Grab Lat Long Elv - save in variable Slatlonelv
LLEPath = InfoDir + "LatLonElv.txt"
with open(LLEPath, 'r') as LLEFile:
    SLatLonElv = LLEFile.readline()
    LLEFile.close()
    SLatLonElv = SLatLonElv[:-1] # remove <CR>
    print('LatLongElev =',SLatLonElv)
with open(LLEPath, 'r') as LLEFile:
    LLEdata = csv.reader(LLEFile)
    for LLEline in LLEdata:
        Lat = LLEline[0]
        Long = LLEline[1]
        Elev = LLEline[2]
    LLEFile.close()
    print('Lat=',Lat,' Long=',Long,' Elev=',Elev)

#Grab Frequency Standard - save in variable SFreqStd
FSPath = InfoDir + "FreqStd.txt"
with open(FSPath, 'r') as FSFile:
    SFreqStd = FSFile.readline()
    FSFile.close()
    SFreqStd = SFreqStd[:-1] # remove <CR>
    print('Sinfo Freq Standard =', SFreqStd)

#Grab Radio - save in variable SRadio
RadioPath = InfoDir + "Radio1.txt"
with open(RadioPath, 'r') as RadioFile:
    SRadio = RadioFile.readline()
    RadioFile.close()
    SRadio = SRadio[:-1] # remove <CR>
    print('Sinfo Radio =', SRadio)

#Grab RadioID - save in variable SRadioID
RadioIDPath = InfoDir + "Radio1ID.txt"
with open(RadioIDPath, 'r') as RadioIDFile:
    SRadioID = RadioIDFile.readline()
    RadioIDFile.close()
    SRadioID = SRadioID[:-1] # remove <CR>
    print('Sinfo RadioID =', SRadioID)

#Get Antenna - save in variable SAnt
AntPath = InfoDir + "Antenna.txt"
with open(AntPath, 'r') as AntFile:
    SAnt = AntFile.readline()
    AntFile.close()
    SAnt = SAnt[:-1] # remove <CR>
    print('Sinfo Antenna =', SAnt)

#Get System Data - save in variable SSystm
SystmPath = InfoDir + "System.txt"
with open(SystmPath, 'r') as SystmFile:
    SSystm = SystmFile.readline()
    SystmFile.close()
    SSystm = SSystm[:-1] # remove <CR>
    print('Sinfo System =', SSystm)


#sys.exit(0)

#Get Metadata - and save to newly created file if it exists
# Metadat file will be copied from original file - not metdata.txt file
#-------------------------------------------------
#-------------------------------------------------

# File processing starts and loops from here

#-------------------------------------------------
#-------------------------------------------------

# open file of list of files to process  (todo)
with open(ToDoPath, 'r') as ToDoFile:
    print('\n\n**************************************************')
    print('**************************************************')
    FiletoChk = ToDoFile.readline() # read first line of file
    while FiletoChk != '':  # keep looping until done
        # remove <lf> char after filename 
        # file name format is analysisYYMMDD.csv --- 18 Chars total
        while (len(FiletoChk) > 18):
            #print('Filename Length as read in from file =',len(FiletoChk))

            FiletoChk = FiletoChk[:-1]
        #print('Next file listed in todo to process is:',FiletoChk)
        # Create full path name of file to process
        ChkFile = ProcessDir + FiletoChk

        #-------------------------------------------------------------------
        # Check to see if the file to check exists; if not, exit the program
        if (path.exists(ChkFile)):
            print('File to Process ' + ChkFile + ' found!')
        else:
            print('\nFile ' + ChkFile + ' not available.\nExiting very disappointed...\n')
            sys.exit(0)

        # intermediate file for no nulls by screwed up time stamps
        FileBadTime = 'BadTimStmp.csv'

        # create full path to file to check
        ChkFile=(ProcessDir + FiletoChk) # File to check with full path

        # create path to temp image file location if needed
        TempFile=(TempDir + FileBadTime) #with fixed with full path

        # create path to final image file location in /Stemp
        FinalFile=(TempDir + FiletoChk)

        # create path to final image file location in /Stemp of new raw file to save
        NewRawFile=(TempDir + FiletoChk + '.new')

        # got here, so there's a file to be read.
        ###################################################################################
        ###################################################################################
        print('Doing Corrupt File Check. Parsing for the dreaded null chars...')

        null = b'\0'.hex()  # null char - damn screwy way to define it....
        #sys.exit(0)
        #query os for file size
        ChkFileInfo = os.stat(ChkFile)
        numbyt = ChkFileInfo.st_size
        print('File ',ChkFile, '\nOS length (bytes) = ', numbyt)

        # init counters
        numchar = 0
        numnull = 0

        # look for any null char in the file and count it
        with open(ChkFile, 'br') as fileOrg:  #open file in binary data mode - parse it for null (0x00) chars
            for bytnum in range(numbyt):
                nxtchr = fileOrg.read(1)
                if nxtchr.hex() == null :
                    #found one - count it
                    numnull = numnull + 1
                else:
                    #count normaol char
                    numchar = numchar+1
            fileOrg.close()
        print('Original File Size = ',numbyt,'  Number valid chars = ', numchar, '  Number nulls = ', numnull)

        #Any null chars?
        if (numnull == 0) :
            print('No null chars found - Using this file -----> AS IS <-----\n')
            # keep same source file - no null chars found - switch to point to original file
            TempFile = ChkFile
            ReplaceOrigFile = 0
            badfile = 0
        else:
            print(numnull,' Null Chars Found - Repairing Corrupted File...')
            badfile = 1
            ReplaceOrigFile = 1

        # found a null char in the file - must remove all of them....
        if (badfile == 1) :
            # File is corrupt - fix it
            remnull = 0  # init counters
            wnumchar = 0
            fixtempfile = open(TempFile, 'bw')  #open temp file for writes
            with open(ChkFile, 'br') as fileOrg:  #open original file in binary data mode - parse and remove null (0x00) chars
                for bytnum in range(numbyt): # set up loop for reading whole file
                    nxtchr = fileOrg.read(1) # read next binary char
                    if nxtchr.hex() == null :
                        #char is a null - count & omit it
                        remnull = remnull + 1
                    else:
                        #char is valid - count & save it
                        wnumchar = wnumchar+1
                        fixtempfile.write(nxtchr) #save real char in new file
                #Print out final file char counts
                print('Removed ',remnull,'null chars  ---  wrote ',wnumchar, 'chars back to temp repaired file')

                # What has been done is that this file was created with the null chars rremoved  but still has bad time stamps

            fixtempfile.close()  # close temp file
        #    sys.exit(0)
        ###################################################################################
        ###################################################################################

        ### resequencing time stamp code goes here
            print("Adjusting timestamps - parsing for space/time continuum flaws")
            # Aidan's magical timestamp sequence fix code
            fix_timestamps_after_crash.fix_and_write_back(TempFile)
        ###################################################################################
        ###################################################################################

        #See if need to Move the fixed file to the original directory

        if (ReplaceOrigFile == 1):
            print('Replacing original corrupted file with fixed version', TempFile)
            #overwrite original corrupted file
            #Keep original bad file for future reference (in case we screw up...)
            SaveBadSrcFile = ChkFile + '.bad'

            print('TempFile=',TempFile, '  ChkFile=',ChkFile, '  SavedBadSrcFile=',SaveBadSrcFile)
            #sys.exit(0)
            # move original raw data corrupted source file to have a .bad file extension added
            print('Saving Original file as .bad for future reference')
            shutil.move(ChkFile, SaveBadSrcFile)  # saves the original source file with a .bad file extension
            os.chmod(SaveBadSrcFile, mode=0o664)   # set the permissions to 664

            shutil.move(TempFile, ChkFile)  # replace the original source file with the fixed one
            os.chmod(ChkFile, mode=0o664)   # set the permissions to 664
        ###################################################################################
        ###################################################################################
        # create new header info in new file and copy the Metadata header to new file
        # copy the Metadata header to new file
        #open the original input file that has been null corrected for final processing
        with open(ChkFile, "r") as tmpfile:
            print('File ', FiletoChk, ' Opened')
            linecnt=0
            #open new final output file (to be initially saved in tmp dir)
            FinalOutFile = open(FinalFile, 'w', newline='')
            # temp storage of new raw data file to save
            NewRawFileTemp = open(NewRawFile, 'w', newline='')
            #use csv processing modules for both
            tmpreader = csv.reader(tmpfile)
            writeff = csv.writer(FinalOutFile)
            writenewraw = csv.writer(NewRawFileTemp)
            # index starts at 0 and goes thru 9 on 1st metadata header info line
            # need to extract original date (index=1) and Beacon (index=9) from 1st line of file

            # the only 2 pieces of info we need from the original file is the date/timestamp and Beacon
            # These are extracted here
            for line in tmpreader:
                #print('date=',line[1])
                #print('Beacon=',line[9])
                UTCDTZ = line[1]
                UTCDTZnc=UTCDTZ.replace(':','') # remove the semicolons for use in filename
                SBeacon = line[9]
                #print('Extracted SDate =',UTCDTZ)
                UTC_DT = UTCDTZ[:10]  # Just want date with no - -
                UTCshort = UTCDTZ[2:10]
                UTCsnc=UTCshort.replace('-','') # remove the semicolons for use in filename
                #print('UTC YYMMDD=', UTCsnc)
                print('Extracted DateOnly=',UTC_DT)
                print('Extracted SBeacon =',SBeacon)
                break  # seems kinda crude way to exit on 1st pass....

            # take care of metadata lines first
            # Write first line of newly created header
            # write new info header line
            #print('New Metatdata Header:')
            #print('#,',UTCDTZ,',',SNode,',',SGridsqr,',',SLatLonElv,',',SCityState,',',SRadioID,',',SBeacon)
            FirstLine='#,'+UTCDTZ+','+SNode+','+SGridsqr+','+SLatLonElv+','+SCityState+','+SRadioID+','+SBeacon+'\n'
            FinalOutFile.write(FirstLine) #write data to final format file
            NewRawFileTemp.write(FirstLine) #write data to new raw format file

            #print('#######################################')
            FinalOutFile.write('#######################################\n') #write data line
            NewRawFileTemp.write('#######################################\n') #write data line
            #print('# MetaData for Grape Gen 1 Station')
            FinalOutFile.write('# MetaData for Grape Gen 1 Station\n') #write data line
            NewRawFileTemp.write('# MetaData for Grape Gen 1 Station\n') #write data line
            #print('#')
            FinalOutFile.write('#\n') #write data line
            NewRawFileTemp.write('#\n') #write data line
            #print('# Station Node Number      ' + SNode)
            FinalOutFile.write('# Station Node Number      ' + SNode + '\n') #write data line
            NewRawFileTemp.write('# Station Node Number      ' + SNode + '\n') #write data line
            #print('# Callsign                 ' + SCallsign )
            FinalOutFile.write('# Callsign                 ' + SCallsign + '\n') #write data line
            NewRawFileTemp.write('# Callsign                 ' + SCallsign + '\n') #write data line
            #print('# Grid Square              ' + SGridsqr)
            FinalOutFile.write('# Grid Square              ' + SGridsqr + '\n') #write data line
            NewRawFileTemp.write('# Grid Square              ' + SGridsqr + '\n') #write data line
            #print('# Lat, Long, Elv           ' + SLatLonElv)
            FinalOutFile.write('# Lat, Long, Elv           ' + SLatLonElv + '\n') #write data line
            NewRawFileTemp.write('# Lat, Long, Elv           ' + SLatLonElv + '\n') #write data line
            #print('# City State               ' + SCityState)
            FinalOutFile.write('# City State               ' + SCityState + '\n') #write data line
            NewRawFileTemp.write('# City State               ' + SCityState + '\n') #write data line
            #print('# Radio1                   ' + SRadio)
            FinalOutFile.write('# Radio1                   ' + SRadio + '\n') #write data line
            NewRawFileTemp.write('# Radio1                   ' + SRadio + '\n') #write data line
            #print('# Radio1ID                 ' + SRadioID)
            FinalOutFile.write('# Radio1ID                 ' + SRadioID + '\n') #write data line
            NewRawFileTemp.write('# Radio1ID                 ' + SRadioID + '\n') #write data line
            #print('# Antenna                  ' + SAnt)
            FinalOutFile.write('# Antenna                  ' + SAnt + '\n') #write data line
            NewRawFileTemp.write('# Antenna                  ' + SAnt + '\n') #write data line
            #print('# Frequency Standard       ' + SFreqStd)
            FinalOutFile.write('# Frequency Standard       ' + SFreqStd + '\n') #write data line
            NewRawFileTemp.write('# Frequency Standard       ' + SFreqStd + '\n') #write data line
            #print('# System Info              ' + SSystm)
            FinalOutFile.write('# System Info              ' + SSystm + '\n') #write data line
            NewRawFileTemp.write('# System Info              ' + SSystm + '\n') #write data line
            #print('#')
            FinalOutFile.write('#\n') #write data line
            NewRawFileTemp.write('#\n') #write data line
            #print('#')
            FinalOutFile.write('# Beacon Now Decoded       ' + SBeacon + '\n') #write data line
            NewRawFileTemp.write('# Beacon Now Decoded       ' + SBeacon + '\n') #write data line
            #print('# Beacon Now Decoded       ' + SBeacon)
            FinalOutFile.write('#\n') #write data line
            NewRawFileTemp.write('#\n') #write data line
            #print('#')
            FinalOutFile.write('#######################################\n') #write data line
            NewRawFileTemp.write('#######################################\n') #write data line
            #print('#######################################')
            # in old file scan for the header line that starts the actual data following it
            for nxtline in tmpfile:
            # look for header line of file data -
                if (nxtline[:3] != "UTC"):
                    linecnt = linecnt + 1
                    # this will remove the original header info
                else:
                    # this is the CSV header already in buffer - rewrite what we want from it
                    NewRawFileTemp.write("UTC,Freq,Freq Err,Vpk,dBV(Vpk)\n") # write original format in new analysisYYMMDD.csv file
                    FinalOutFile.write("UTC,Freq,Vpk\n") #processed header file write
                    #print("Found it [UTC]! - writing Header out as: UTC,Freq,Vpk\n")
                    linecnt = linecnt + 1
                    break
            print('Total number of lines for metadata (including Header line) = ', linecnt)

            # This just blindly copies all the data lines to the new file
            rowcnt = 0
            for line in tmpreader:
                # use this line if you want to recreate the original raw data file named analysisYYMMDD.csv
                writenewraw.writerow([line[0], line[1], line[2], line[3], line[4]]) #original saved data

                # use this line if you want to create the processed data file with the huge filename
                writeff.writerow([line[0], line[1], line[3]]) #processed data

                # KEep track of total data lines collected for day (should be 86,400)
                rowcnt = rowcnt + 1

            #Indicate total lines read and what was expected
            MissSecData = 86400 - rowcnt
            print('   --->>> Processed ',rowcnt,' rows of data - should be 86400 - missing ',MissSecData  ,' Seconds of data <<<---', '\n')

            # close all open files
            tmpfile.close()
            FinalOutFile.close()
            NewRawFileTemp.close()

        #print('File ',FinalOutFile , ' Closed')

        #print('Temp exit')
        #sys.exit(0)

        ###################################################################################
        ###################################################################################
        # Use format corrected date from header of file for processed filename
        NewFinalFileName = UTCDTZnc + '_' + SNode + '_' + SRadioID + '_' + SGridsqr + '_FRQ_' + SBeacon + '.csv'

        # Create filename and correct position in filesystem tree
        SDataFile = SDataDir + NewFinalFileName   # Save final file directly in /Sdata/ directory
        #print('New Finished Final Format File = ', SDataFile)

        # move new processed data file to final destination
        #print('Coping Output File to final destination ',SDataFile)
        shutil.move(FinalFile, SDataFile)
        os.chmod(SDataFile, mode=0o664)   # set the permissions to 664

        # save original raw data file with .orig appended to filename
        #print('Saving original analysisYYMMDD.csv file')
        OldChkFile = ChkFile + '.orig'
        shutil.move(ChkFile, OldChkFile)
        os.chmod(OldChkFile, mode=0o664)   # set the permissions to 664

        # move new raw data file to final destination
        #print('Moving new raw data File to final destination ',ChkFile)
        shutil.move(NewRawFile, ChkFile)
        os.chmod(ChkFile, mode=0o664)   # set the permissions to 664

        ###############################################################
        # Create the plotfile for this file as well
        beacon = SBeacon
        print('Processing new plot file')

        # Start Plot Processing
        with open(ChkFile, "r") as DataFile:
            dataReader=csv.reader(DataFile)
            data = list(dataReader)
            Header = data.pop(0)

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

            print('Doppler min: ', min_Doppler, '; Doppler max: ', max_Doppler)
            print('Vpk min: ', min_Vpk, '; Vpk max: ', max_Vpk)
            print('dB min: ', min_power, '; dB max: ', max_power)

            # Create an order 3 lowpass butterworth filter.
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
            filtDoppler = filtfilt(b, a, Doppler)  # something changed in python3 that gives error/warning
                                                   # use arr[tuple(seq)]` instead of `arr[seq]`

            #print ('Filter power data')
            filtPower = filtfilt(b, a, Power_dB)
            #sys.exit(0)
            ##%% modified from "Double-y axis plot,
            ## http://kitchingroup.cheme.cmu.edu/blog/2013/09/13/Plotting-two-datasets-with-very-different-scales/
            #print('set up axes for plot')

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

            # Create Plot Title
            #print('create Plot TItle')
            plt.title(SBeacon + ' Doppler Shift Plot\nNode:  ' + SNode + '     Gridsquare:  '+ SGridsqr + '\nLat= ' + Lat + '    Long= ' + Long + '    Elev= ' + Elev + ' M\n' + UTC_DT + '  UTC')

            # Create Plot File Nam
            #GraphFile = yesterdaystr + '_' + node + '_' + RadioID + '_' + GridSqr + '_' + beacon + '_graph.png'
            GraphFile = UTCDTZnc + '_' + SNode + '_' + SRadioID + '_' + SGridsqr + '_' + SBeacon + '_graph.png'
            PlotGraphFile = PlotDir + GraphFile
            XferGraphFile = XferDataDir + GraphFile

            # create plot
            #plt.savefig(PlotDir + yesterdaystr + '_' + node + '_' +  GridSqr + '_' +  RadioID + '_' +  beacon + '_graph.png', dpi=250, orientation='landscape')
            plt.savefig(PlotGraphFile, dpi=250, orientation='landscape')
            # =============================================================================

            print('Plot File: ' + GraphFile + '\n')  # indicate plot file name for crontab printout


        # Check to see if the autoxfer file exists; if not, skip copying the plot
        if (path.exists(autoxferfile)):
            print('autoxfer enable File found')
            # copy processed data file to transfer directory
            XferDataFile = XferDataDir + NewFinalFileName   # Copy final processed data file also to /Sxfer/ directory for transfer
            print('Copying data file to Sxfer directory for upload '+ XferDataFile)
            shutil.copy(SDataFile, XferDataFile)
            os.chmod(XferDataFile, mode=0o664)   # set the permissions to 664
            # Copy final plot file also to /Sxfer/ directory for transfer
            print('Copying plot file to Sxfer directory for upload '+ XferGraphFile)
            shutil.copy(PlotGraphFile, XferGraphFile)
            os.chmod(XferGraphFile, mode=0o664)   # set the permissions to 664
        else:
            print('No autoxfer enable File found - no copy made')


        # indicate done with this file
        print('**************************************************')
        print('**************************************************\n\n')

        # check for next file to process
        FiletoChk = ToDoFile.readline() # read next line of file list to update 

####################################################################################### 
# finished processing all file in todo file - finish and exit

# close the todo file just processed
ToDoFile.close()

# rename it with .done so you know it has been processed
ToDoPathDone = ToDoPath + '.done'
shutil.move(ToDoPath, ToDoPathDone)

# exit gracefully
print('\n\nFinished processing all files in todo file - exiting gracefully!') 
sys.exit(0)
