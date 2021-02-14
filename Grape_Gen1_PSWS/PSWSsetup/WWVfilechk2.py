#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29, 2020
First working copy finished July 5, 2020
WWVfilechk2.py   Finished for usage 7-16-20

WWV file corruption processing.
Faliure mode is power gets cut off to RasPi and the last buffer write to disk has 
padded the file with null chars.  Then on restart FLDigi starts before the clock 
gets set (usually backwards in time) and then when the system clock sets, its jumps 
forward to the correct time.  This is the fingerprint of the corruption.  Both are fixed.
Jan 29, 2021 added copy of files to be transferred each day to the /Sxfer directory
             added auto transfer on/off  capability, autoplot on/off capability
@author jcgibbons N8OBJ
"""

import os
from os import path
import sys
import shutil
import csv
from datetime import date, timedelta
import maidenhead as mh
import fix_timestamps_after_crash

# Define users home directory path
HomePath = os.path.expanduser('~')
print('Home Path = ' + HomePath)

ProcessDir = HomePath + '/PSWS/Srawdata/'
#print('ProcessDir = ' + ProcessDir)

#directories for storing processed data files
TempDir = HomePath + '/PSWS/Stemp/'
#print('TempDir = ' + TempDir)

InfoDir = HomePath + '/PSWS/Sinfo/'
#print('InfoDir = ' + InfoDir)

#directory for storing processed data files
SaveDataDir = HomePath + '/PSWS/Sdata/'
#print('SaveDataDir = ' + SaveDataDir)

#directory for storing processed data files to be transferred
XferDataDir = HomePath + '/PSWS/Sxfer/'
#print('XferDataDir = ' + XferDataDir)

# flag file for auto transfer on / off
autoxferfile = HomePath + '/PSWS/Scmd/autoxfer'
#print('AutoXfer file path = ' + autoxferfile)

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

# Find numerical version of today in N8OBJ format
today = date.today()

# And from that, of yesterday
yesterday = today-timedelta(1) #create yesterday's date

# Then turn it into a string of appropriate format
yesterdaystr = yesterday.__str__() #yesterday's date in string form, ISO format
yesterdaydate = yesterdaystr # save for use if we need to resequence any strings
print('Yesterdays Date = ', yesterdaydate)

#convert date format to filename format
yestrdate = yesterdaystr[2:] #removes first two digits of year
yestrdate = yestrdate.replace('-','') #remove the hyphens

#create file name to check
FileChk = 'analysis' + yestrdate + '.csv' #filename format
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

# ----- OR ------

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
#This is a MANUAL FORCED find of the file to be graphed

# Force a file for debug

#FileChk='analysis210110.csv'  # newest format

# if using above line, comment out 3 lines in next section
#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

# intermediate file for no nulls by screwed up time stamps
FileBadTime = 'BadTimStmp.csv'

# create full path to file to check
ChkFile=(ProcessDir + FileChk) # File to check with full path

# create path to temp image file location if needed
TempFile=(TempDir + FileBadTime) #with fixed with full path

# create path to final image file location if needed
FinalFile=(TempDir + FileChk) #with fixed with full path

# make sure both data path exists - if not, abort
if (path.exists(ProcessDir)):
    print('ProcessDir exists: ' + ProcessDir)
else:
    print('No directory ', ProcessDir)
    sys.exit(0)

# make sure temp path exists - if not, abort
if (path.exists(TempDir)):
    print('TempDir exists: ' + TempDir)
else:
    print('No directory ', TempDir)
    sys.exit(0)
#-------------------------------------------------------------------
#%
# Check to see if the file to check exists; if not, exit the program
if (path.exists(ChkFile)):
    print('\nFile to Analyze ' + ChkFile + ' found\n')
else:
    print('\nFile ' + ChkFile + ' not available.\nExiting disappointed...\n')
    sys.exit(0)
#-----------------------------------------------
#% #got here, so there's a file to be read.
print('Doing Corrupt File Check. Parsing for the dreaded null chars...')

null = b'\0'.hex()  # null char - damn screwy way to define it....

#query os for  file size
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
if numnull == 0 :
    print('No null chars found - Using file --- AS IS ---\n')
    # keep same source file - no null chars found - switch to point to original file
    TempFile = ChkFile
    ReplaceOrigFile = 0
    badfile = 0
else:
    print(numnull,' Null Chars Found - Repairing Corrupted File...')
    badfile = 1
    ReplaceOrigFile = 1

# found a null char in the file - must remove all of them....
if badfile == 1 :
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

# File pointers created as follows:
# intermediate file for no nulls but screwed up time stamps
#      is FileBadTime = 'BadTimeStampFile.csv'

# create path to temp image file location if needed
#      TempFile=(TempDir + FileBadTime) #with fixed with full path

### resequencing time stamp code goes here
    print("Adjusting timestamps - parsing for space/time continuum flaws")
    # Aidan's magical timestamp sequence fix code
    fix_timestamps_after_crash.fix_and_write_back(TempFile)

#See if need to Move the fixed file to the original directory

if ReplaceOrigFile == 1:
    print('Replacing original corrupted file with fixed version', TempFile)
    #overwrite original corrupted file
    #Keep original bad file for future reference (in case we screw up...)
    SaveBadSrcFile = ChkFile + '.bad'

    print('TempFile=',TempFile, '  ChkFile=',ChkFile, '  SavedBadSrcFile=',SaveBadSrcFile)
    #sys.exit(0)
    # move original raw data corrupted source file to have a .bad file extension added
    print('Saving Original file as .bad for future reference')
    shutil.move(ChkFile, SaveBadSrcFile)  # saves the original source file with a .bad file extension
    #os.chmod(SaveBadSrcFile, mode=0o664)   # set the permissions to 664

    shutil.move(TempFile, ChkFile)  # replace the original source file with the fixed one
    #os.chmod(ChkFile, mode=0o664)   # set the permissions to 664


# now have fixed file (if not replaced - TempFile = ChkFile)
#print()
print('Final File= ',FinalFile)
print ('Temp FixFile= ',TempFile)
print('Original File= ', ChkFile)
print()
#sys.exit(0)
#print('Open source from ', ChkFile)

#Create final saved file format for xfer
with open(ChkFile, "r") as tmpfile:
    linecnt=0
    FinalOutFile = open(FinalFile, 'w', newline='')
    #print('Create Final File format for upload')
    # take care of metadata lines first
    for nxtline in tmpfile:
        if (nxtline[:3] != "UTC"):
            linecnt = linecnt + 1
            #print('HDR:',nxtline[:3])
            FinalOutFile.write(nxtline)
        else:
            # this is the CSV header already in buffer - fake what we want from it
            FinalOutFile.write("UTC,Freq,Vpk\n")
            #print("Found it [UTC]! - writing Header out as: UTC,Freq,Vpk\n")
            linecnt = linecnt + 1
            break

    print('Total lines for metadata (including Header line) = ', linecnt)

    # now grab correct lines of each row to save in final file
    # change file handling to .csv format for both files
    tmpreader = csv.reader(tmpfile)
    writeff = csv.writer(FinalOutFile)

# metadata already written to new file, start with data
    recordcnt  = 0
    freqcalc = 0
    calccnt = 0
    for line in tmpreader:
        #print(",".join([line[0], line[1], line[3]]))
        writeff.writerow([line[0], line[1], line[3]])
        recordcnt = recordcnt + 1
        calccnt = calccnt + 1
        if (calccnt  < 11):
            freqcalc = freqcalc + float(line[1])
   #print('Total Data Records = ', recordcnt)
    CalcFreq = freqcalc / 10
   # print("Average of 1st 10 measured frequencies = ", CalcFreq)

    #Create integer rep for analysis (add offset to get correct rounding)
    CalcFrqNum = int((CalcFreq+100)/10000)
    #print('CalcFreqNum =',CalcFrqNum)

    #Figure out the beacon ID from 1st 10 lines of data in file

    # have it default to Unknown
    cbeacon = "Unknown";

    if (CalcFrqNum == 250):
        cbeacon = "WWV2p5"

    if (CalcFrqNum == 500):
        cbeacon = "WWV5"

    if (CalcFrqNum == 1000):
        cbeacon = "WWV10"

    if (CalcFrqNum == 1500):
        cbeacon = "WWV15"

    if (CalcFrqNum == 2000):
        cbeacon = "WWV20"

    if (CalcFrqNum == 2500):
        beacon = "WWV25"

    if (CalcFrqNum == 333):
        cbeacon = "CHU3"

    if (CalcFrqNum == 785):
        cbeacon = "CHU7"

    if (CalcFrqNum == 1467):
        cbeacon = "CHU14"

    print('Calc Beacon ID =',cbeacon)

    tmpfile.close()
    FinalOutFile.close()

# Grab System info dir data as default

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#Grab station Node Number
NodePath = InfoDir + "NodeNum.txt"
with open(NodePath, 'r') as NodeFile:
    Snode = NodeFile.readline()
    NodeFile.close()
    Snode = Snode[:-1]
#    print('Sinfo Node =', Snode)

#Grab City State
CSPath = InfoDir + "CityState.txt"
with open(CSPath, 'r') as CSFile:
    SCityState = CSFile.readline()
    CSFile.close()
    SCityState = SCityState[:-1]
#    print('Sinfo CityState =', SCityState)

#Grab Grid Square
GSPath = InfoDir + "GridSqr"
with open(GSPath, 'r') as GSFile:
    SGridsqr = GSFile.readline()
    GSFile.close()
    SGridsqr = SGridsqr[:-1]
#    print('Sinfo Gridsqr =', SGridsqr)

#Grab Lat Long Elv
LLEPath = InfoDir + "LatLonElv.txt"
with open(LLEPath, 'r') as LLEFile:
    SLatLonElv = LLEFile.readline()
    LLEFile.close()
    SLatLonElv = SLatLonElv[:-1]
#    print('Sinfo LatLonElv =', SLatLonElv)

#Grab RadioID
RIDPath = InfoDir + "Radio1ID.txt"
with open(RIDPath, 'r') as RIDFile:
    SRID = RIDFile.readline()
    RIDFile.close()
    SRID = SRID[:-1]
#    print('Sinfo RadioID =', SRID)

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#sys.exit(0)
# first, see what it's supposed to be
# Extract file header info

with open(FinalFile, 'r') as dataFile:
    dataReader=csv.reader(dataFile)
    data = list(dataReader)
    #print('Header Data:',data)
    Header = data.pop(0)

    #Figure out which header format reading
    NewHdr = 0
    print('Header to check=', Header)
    # Check if First header line is of new format example
    #,2020-05-16T00:00:00Z,N00001,EN91fh,41.3219273, -81.5047731, 284.5,Macedonia Ohio,G1,WWV5
    if Header[0] == "#":
        print('New Header String Detected')
        NewHdr = 1        # Have new header format
        #pull the data fields out
        UTCDTZ = Header[1]
        UTCDTZnc=UTCDTZ.replace(':','') # remove the semicolons for use in filename
        print('Original Read UTCDTZ =', UTCDTZ, '   corrected UTCDTZnc = ',UTCDTZnc)
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
    else:
        print("Unknown Header Format - Exiting Program...")
        dataFile.close()
        sys.exit(0)

    dataFile.close()

    print('Final Format Intermediate Output File =', FinalFile)
    # Use format corrected date from header of file for filename
    NewFinalFileName = UTCDTZnc + '_' + node + '_' + radioid + '_' + GridSq + '_FRQ_' + beacon + '.csv'

    print('New Final File Name =',NewFinalFileName)


#### NO NEED TO DO THIS  ####
# Taken care of by filenaming structure so they all can exist in one directory.

# check for existance of final correct beacon sub-directory
#SaveDataDirBeacon = SaveDataDir + beacon
# make sure Sdata path exists - if not, create it with correct permissions
#if (path.exists(SaveDataDirBeacon)):
#    print('Target Dir exists as', SaveDataDirBeacon)
#else:
#    print('Target Dir NOT there - making path ' + SaveDataDirBeacon)
#    os.mkdir(SaveDataDirBeacon)           # create tyhe directory
#    os.chmod(SaveDataDirBeacon, mode=0o664)   # set the permissions to 664

#SaveDataFile = SaveDataDir + beacon +'/' + NewFinalFileName   # save final file in /Sdata/Beacon/ subdirctory

# Create filename and correct position in filesystem tree
SaveDataFile = SaveDataDir + NewFinalFileName   # Save final file directly in /Sdata/ directory
print('Finished Final Format File = ', NewFinalFileName)
print('Final file saved to ', SaveDataFile)

# move file to final destination
print('\nMoving Output File to final destination ',SaveDataFile)
#shutil.move(FinalFile, SaveDataFile)
shutil.move(FinalFile, SaveDataFile)
#os.chmod(SaveDataFileFile, mode=0o664)   # set the permissions to 664

#-------------------------------------------------------------------
# Check to see if the autoxfer file exists; if not, skip copying the plot
if (path.exists(autoxferfile)):
    print('autoxfer enable File found\n')
    # copy file to transfer directory
    XferDataFile = XferDataDir + NewFinalFileName   # Copy final processed data file also to /Sxfer/ directory for transfer
    print('Copying file to Sxfer directory for upload '+ XferDataFile)
    shutil.copy(SaveDataFile, XferDataFile)
    #os.chmod(XferDataFile, mode=0o664)   # set the permissions to 664
else:
    print('No autoxfer enable File found - exiting')

print('\nExiting New Gen 1 Grape python processing program gracefully')
