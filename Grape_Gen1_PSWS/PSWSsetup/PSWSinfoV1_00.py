#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 13, 2020
List PSWS information
Prints and saves the Station Information in the /PSWS/Sinfo directory
@author jcgibbons N8OBJ
"""

import os
from os import path
import sys
import csv

# ~ points to users home directory - usually /home/pi/
homepath = os.path.expanduser('~')

PSWSDir = homepath + "/PSWS/"
InfoDir = PSWSDir + 'Sinfo/'

################################################################
################################################################

#print('\n\nGrape Personal Space Weather Station (PSWS) List Info Program Ver 1.00\n\n')

################################################################
################################################################

# make sure PSWS path exists - if not, create it with correct permissions
if (path.exists(InfoDir) != 1):
    print(InfoDir + ' NOT there - aborting')
    sys.exit(0)

################################################################
# check for node number
################################################################
NodePath = InfoDir + "NodeNum.txt"

if (path.exists(NodePath)):
    with open(NodePath, 'r') as NodeFile: # file there - open it
        PSWSnode = NodeFile.readline()  # read file contents
        NodeFile.close()   # close file
#        print('Current Node Assignment = '+ PSWSnode)  # display it
else:
#    print('\nNode file not found- creating default\n')
    PSWSnode = 'N0000000\n' # create default Node Number

################################################################
#Check for CallSign info
################################################################
CallSgnPath = InfoDir + "CallSign.txt"

if (path.exists(CallSgnPath)):
    with open(CallSgnPath, 'r') as CallSgnFile: # file there - open it
        CallSign = CallSgnFile.readline()  # read file contents
        CallSgnFile.close()   # close file
#        print('CallSign = '+ CallSign)  # display it

else:
#    print('CallSign file not found- creating default')
    CallSign = 'NoCall\n' # create default Lat Long Elv Numbers

################################################################
# check for Lat Long Elev
################################################################

LLEPath = InfoDir + "LatLonElv.txt"

if (path.exists(LLEPath)):
    with open(LLEPath, 'r') as LLEFile: # file there - open it
        LatLonElv = LLEFile.readline()  # read file contents
        LLEFile.close()   # close file
#        print('\nLatLonElV = ' + LatLonElv)
else:
#    print('\nLatLonElV file not found- creating default')
    LatLonElv = '00.000000,-00.000000,000\n' # create default Lat Long Elv Numbers

################################################################
#Check for City State info
################################################################
CSPath = InfoDir + "CityState.txt"

if (path.exists(CSPath)):
    with open(CSPath, 'r') as CSFile: # file there - open it
        CityState = CSFile.readline()  # read file contents
        CSFile.close()   # close file
#        print('Current Saved City State = '+ CityState)  # display it

else:
#    print('CityState file not found- creating default')
    CityState = 'NOCity NOState\n' # create default Lat Long Elv Numbers

################################################################
#Check for FreqRef info
################################################################
FreqStdPath = InfoDir + "FreqStd.txt"

if (path.exists(FreqStdPath)):
    with open(FreqStdPath, 'r') as FrqStdFile: # file there - open it
        FreqStd = FrqStdFile.readline()  # read file contents
        FrqStdFile.close()   # close file
#        print('Current Saved Frequency Standard = '+ FreqStd)  # display it

else:
        FreqStd = 'Unknown\n' # create default Lat Long Elv Numbers

################################################################
#Get Radio1 info
################################################################
RadioPath = InfoDir + "Radio1.txt"

if (path.exists(RadioPath)):
    with open(RadioPath, 'r') as RadioFile: # file there - open it
        Radio1 = RadioFile.readline()  # read file contents
        RadioFile.close()   # close file
#        print('Current Saved Radio1 = '+ Radio1)  # display it

else:
        Radio1 = 'Mystery Radio1\n' # create default Lat Long Elv Numbers

################################################################
#Get Radio1 ID info
################################################################
RIDPath = InfoDir + "Radio1ID.txt"
if (path.exists(RIDPath)):
    with open(RIDPath, 'r') as RadioIDFile: # file there - open it
        RadioID = RadioIDFile.readline()  # read file contents
        RadioIDFile.close()   # close file
#        print('Current Saved Radio1 ID = '+ RadioID)  # display it

else:
    RadioID = 'No Radio1 ID\n' # create default Lat Long Elv Numbers

################################################################
#Get Antenna info
################################################################
AntPath = InfoDir + "Antenna.txt"
if (path.exists(AntPath)):
    with open(AntPath, 'r') as AntFile: # file there - open it
        ANT = AntFile.readline()  # read file contents
        AntFile.close()   # close file
#        print('Current Saved Antenna = '+ ANT)  # display it

else:
    ANT = '50 Ohm Dummy Load\n' # create default Lat Long Elv Numbers

################################################################
#Get System info
################################################################
SysInfoPath = InfoDir + "System.txt"
if (path.exists(SysInfoPath)):
    with open(SysInfoPath, 'r') as SysInfoFile: # file there - open it
        SysInf = SysInfoFile.readline()  # read file contents
        SysInfoFile.close()   # close file
#        print('Current System Info = '+ SysInf)  # display it

else:
    SysInf = 'A Computer Running Linux\n' # create default Lat Long Elv Numbers

################################################################
#Get remaining autogenerated info for final listing of station info
################################################################
# Get autogenerated GridSquare
################################################################
GSPath = InfoDir + "GridSqr"
if (path.exists(AntPath)):
    with open(GSPath, 'r') as GSFile: # file there - open it
        GridSqr = GSFile.readline()  # read file contents
        GSFile.close()   # close file
else:
    GridSqr = "Unknown\n"

################################################################
# Get autogenerated Beacon
################################################################
BcnPath = InfoDir + "Beacon1"
Beacon1 = 'Unknown\n'
if (path.exists(BcnPath)):
    with open(BcnPath, 'r') as BcnFile: # file there - open it
        Beacon1 = BcnFile.readline()  # read file contents
        BcnFile.close()   # close file
else:
    Beacon1 = "Unknown\n"

################################################################
################################################################

#sys.exit(0)

#print('\n Final Metadata for this station:\n')

print('#######################################');
print('# MetaData for Grape Gen 1 Station');
print('#')
print('# Station Node Number      ' + PSWSnode[:-1] )
print('# Callsign                 ' + CallSign[:-1])
print('# Grid Square              ' + GridSqr[:-1])
print('# Lat, Long, Elv           ' + LatLonElv[:-1])
print('# City State               ' + CityState[:-1])
print('# Radio1                   ' + Radio1[:-1])
print('# Radio1ID                 ' + RadioID[:-1])
print('# Antenna                  ' + ANT[:-1])
print('# Frequency Standard       ' + FreqStd[:-1])
print('# System Info              ' + SysInf[:-1])
print('#')
print('# Beacon Now Decoded       ' + Beacon1[:-1])
print('#')
print('#######################################')
################################################################
################################################################
#Look for optional Metadat file
MetaPath = InfoDir + "Metadata.txt"
if (path.exists(MetaPath)):
#    print('# --- Extra Metadata File ---')
    with open(MetaPath, 'r') as MetaFile: # file there - open it
        MetadataLine = MetaFile.readline()  # read file contents
        print('# ' + MetadataLine + '\n')

    MetaFile.close()   # close file 
    print('# ')
    print('#######################################')


################################################################
################################################################
# create file with above info imbedding Node Number in filename
################################################################
################################################################
PSWSInfoPath = InfoDir + 'PSWSinfo' + PSWSnode[:-1] + '.txt'
print('\n\nSaved file = '  + PSWSInfoPath)

with open(PSWSInfoPath, 'w') as PSWSInfoFile:
    PSWSInfoFile.write('#######################################\n') #write data line
    PSWSInfoFile.write('# MetaData for Grape Gen 1 Station\n') #write data line
    PSWSInfoFile.write('#\n') #write data line
    PSWSInfoFile.write('# Station Node Number      ' + PSWSnode) #write data line
    PSWSInfoFile.write('# Callsign                 ' + CallSign) #write data line
    PSWSInfoFile.write('# Grid Square              ' + GridSqr) #write data line
    PSWSInfoFile.write('# Lat, Long, Elv           ' + LatLonElv) #write data line
    PSWSInfoFile.write('# City State               ' + CityState) #write data line
    PSWSInfoFile.write('# Radio1                   ' + Radio1) #write data line
    PSWSInfoFile.write('# Radio1ID                 ' + RadioID) #write data line
    PSWSInfoFile.write('# Antenna                  ' + ANT) #write data line
    PSWSInfoFile.write('# Frequency Standard       ' + FreqStd) #write data line
    PSWSInfoFile.write('# System Info              ' + SysInf) #write data line
    PSWSInfoFile.write('#\n') #write data line
    PSWSInfoFile.write('# Beacon Now Decoded       ' + Beacon1) #write data line
    PSWSInfoFile.write('#\n') #write data line
    PSWSInfoFile.write('#######################################\n') #write data line

################################################################
# check for metadata file and print if exists
################################################################
    MetaDataPath = InfoDir + "Metadata.txt"
    if (path.exists(MetaDataPath)):
        with open(MetaPath, 'r') as MetaDataFile: # file there - open it
            MetadataLine = MetaDataFile.readline()  # read file contents
            PSWSInfoFile.write('# ' + MetadataLine + '\n') #print contents to file

        MetaDataFile.close()   # close metadata file
        PSWSInfoFile.write('#\n')
        PSWSInfoFile.write('#######################################\n')

        PSWSInfoFile.close()
        os.chmod(PSWSInfoPath, mode=0o764)   # set the permissions to 764

################################################################
################################################################
################################################################

