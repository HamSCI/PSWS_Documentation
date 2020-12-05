#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jul 21, 2020
Create PSWS directory Structure
Populate the Station Information in the /PSWS/Sinfo directory

@author jcgibbons N8OBJ
"""

import os
from os import path
#import sys
import csv
import maidenhead as mh

# ~ points to users home directory - usually /home/pi/
homepath = os.path.expanduser('~')

PSWSDir = homepath + "/PSWS/"
#PSWSDir = homepath + "/pswstest/" #Fake test directory
RawdataDir = PSWSDir + 'Srawdata/'
InfoDir = PSWSDir + 'Sinfo/'
CmdDir = PSWSDir + "Scmd/"
TempDir = PSWSDir + "Stemp/"
StatDir = PSWSDir + "Sstat/"
CodeDir = PSWSDir + "Scode/"
PlotDir = PSWSDir + "Splot/"
DataDir = PSWSDir + "Sdata/"

################################################################
################################################################
################################################################
#Antenna.txt - done
#CallSign.txt - done
#CityState.txt - done
#FreqStd.txt - done
#GridSqr - done
#LatLonElv.txt - done
#Metadata.ttt - not done
#NodeNum.txt  - done
#Radio1ID.txt - done
#Radio1.txt - done
#System.txt - done
################################################################
################################################################
print('\n\nGrape Personal Space Weather Station (PSWS) Setup Program Ver 1.01\n\n')
################################################################
#Check for main base Directory
print('Checking / Creating PSWS Directory Structure\n')
print('Home Path = ' + homepath)

################################################################
# make sure PSWS path exists - if not, create it with correct permissions
if (path.exists(PSWSDir)):
    print('Base Dir PSWS exists ' + PSWSDir)
else:
    print('PSWS Not there - Creating path ' + PSWSDir)
    os.mkdir(PSWSDir)           # create the directory
    os.chmod(PSWSDir, mode=0o774)   # set the permissions to 764

#Check for the subdirectories
################################################################
# make sure Rawdata path exists - if not, create it with correct permissions
if (path.exists(RawdataDir)):
    print('Srawdata exists ' + RawdataDir)
else:
    print('Not there - making path ' + RawdataDir)
    os.mkdir(RawdataDir)           # create the directory
    os.chmod(RawdataDir, mode=0o764)   # set the permissions to 764

################################################################
# make sure Sinfo path exists - if not, create it with correct permissions
if (path.exists(InfoDir)):
    print('Sinfo exists ' + InfoDir)
else:
    print('Not there - making path ' + InfoDir)
    os.mkdir(InfoDir)           # create the directory
    os.chmod(InfoDir, mode=0o764)   # set the permissions to 764

################################################################
# make sure Scmd path exists - if not, create it with correct permissions
if (path.exists(CmdDir)):
    print('Scmd exists ' + CmdDir)
else:
    print('Not there - making path ' + CmdDir)
    os.mkdir(CmdDir)           # create the directory
    os.chmod(CmdDir, mode=0o774)   # set the permissions to 764

################################################################
# make sure Stemp path exists - if not, create it with correct permissions
if (path.exists(TempDir)):
    print('Stemp exists ' + TempDir)
else:
    print('Not there - making path ' + TempDir)
    os.mkdir(TempDir)           # create the directory
    os.chmod(TempDir, mode=0o764)   # set the permissions to 764

################################################################
# make sure Sstat path exists - if not, create it with correct permissions
if (path.exists(StatDir)):
    print('Sstat exists ' + StatDir)
else:
    print('Not there - making path ' + StatDir)
    os.mkdir(StatDir)           # create the directory
    os.chmod(StatDir, mode=0o764)   # set the permissions to 764

################################################################
# make sure Scode path exists - if not, create it with correct permissions
if (path.exists(CodeDir)):
    print('Scode exists ' + CodeDir)
else:
    print('Not there - making path ' + CodeDir)
    os.mkdir(CodeDir)           # create the directory
    os.chmod(CodeDir, mode=0o774)   # set the permissions to 764
    
################################################################
# make sure Splot path exists - if not, create it with correct permissions
if (path.exists(PlotDir)):
    print('Splot exists ' + PlotDir)
else:
    print('Not there - making path ' + PlotDir)
    os.mkdir(PlotDir)           # create the directory
    os.chmod(PlotDir, mode=0o764)   # set the permissions to 764

################################################################
# make sure Sdata path exists - if not, create it with correct permissions
if (path.exists(DataDir)):
    print('Sdata exists ' + DataDir)
else:
    print('Not there - making path ' + DataDir)
    os.mkdir(DataDir)           # create the directory
    os.chmod(DataDir, mode=0o764)   # set the permissions to 764

################################################################
# All dirctories exist or were created -now populate the station information
print('\nNow checking all system Metadata Information')

################################################################
# check for existance of node number
################################################################
NodePath = InfoDir + "NodeNum.txt"

if (path.exists(NodePath)):
    with open(NodePath, 'r') as NodeFile: # file there - open it
        Snode = NodeFile.readline()  # read file contents
        NodeFile.close()   # close file
        if len(Snode) >8:  #look for <lf> char
            Snode = Snode[:-1] # Strip of <LF>
        print('\nCurrent Node Assignment = '+ Snode + '\n')  # display it
        Nfound = 1 #indicate file exist and displey contents
else:
    print('\nNode file not found- creating default\n')
    with open(NodePath, 'w') as NodeFile:
        Snode = 'N0000000\n' # create default Node Number
        NodeFile.write(Snode) #write default node
        NodeFile.close()
    os.chmod(NodePath, mode=0o764)   # set the permissions to 764
    Snode = Snode[:-1] # Strip of <LF>
    print('Created Node Number = ', Snode)
    Nfound = 0
Done = 0
while Done == 0:
    print('Enter New Node Number [format N1234567]')
    NewNN = input('or <enter> to keep this one > ')
    changeNN = 0
    nochng = 0
    if NewNN == '':
        print('Keeping existing Node Number as ' + Snode)
        NewNN = Snode
        Done = 1
        nochng = 1
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        nnlth = len(NewNN)
        if  nnlth == 8:
            print('Correct Length of '+ str(nnlth) + ' for ' + NewNN)
            changeNN = changeNN + 1
        else:
            print('Wrong Length of ' + str(nnlth) + ' for '+ NewNN)
        #print('Node Number Entered as ' + NewNN)

    #Check for leading N
        if NewNN[:1] == 'N':
            print('Correct header letter - ' + NewNN[:1])
            changeNN = changeNN + 1
        else:
            print('Incorrect header letter - ' + NewNN[:1])

    # check if number is an integer
    #    nnval = int( NewNN[1:8])
    #    except ValueError as e:  # >>> this does not work as expected <<<
            # do something with the error
    #        print('Invalid Number ' + NewNN[1:8] )
    #    else:
    #         if nnval <= 9999999:
    #            print('Number of ' + NewNN[1:8] + ' is valid integer')
    #            changeNN = changeNN + 1

    changeNN = changeNN + 1  # allow any char sequence in node number 7 digit field 

    if(changeNN == 3 ): # 0 for keep old number or failed test, 1 or 2 for failed tests, 3 for valid entry
        with open(NodePath, 'w') as NodeFile:
            NodeFile.write(NewNN + '\n') #write new node number with <lf>
            NodeFile.close()
        os.chmod(NodePath, mode=0o764)   # set the permissions to 764
        Done = 1
        print('New Node of '+ NewNN + ' saved\n')
        NewNN = NewNN + '\n'  # for final printout formatting
    else:
        print('Node Number - no change made\n')

################################################################
#Check for CallSign info
################################################################
CallSgnPath = InfoDir + "CallSign.txt"

if (path.exists(CallSgnPath)):
    with open(CallSgnPath, 'r') as CallSgnFile: # file there - open it
        CallSign = CallSgnFile.readline()  # read file contents
        CallSgnFile.close()   # close file
        print('Current CallSign = '+ CallSign)  # display it

else:
    print('CallSign file not found- creating default')
    with open(CallSgnPath, 'w') as CallSgnFile:
        CallSign = 'NoCall\n' # create default Lat Long Elv Numbers
        CallSgnFile.write(CallSign) #write default LAt Long Elev
        CallSgnFile.close()
    os.chmod(CallSgnPath, mode=0o764)   # set the permissions to 764
    print('Created default CallSign =', CallSign)
CSchng = 0
Done = 0
while Done == 0:
    print('Enter New CallSign')
    NewCallS = input('or <enter> to keep this one > ')
    if NewCallS == '':
        print('Keeping existing CallSign as ' + CallSign[:-1])
        NewCallS = CallSign
        Done = 1
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        cslth = len(NewCallS)
        if  cslth >= 3:
            print('Correct min Length of '+ str(cslth) + ' for ' + NewCallS)
            Done =  1
            CSchng = 1
        else:
            print('Wrong min Length of ' + str(cslth) + ' for '+ NewCallS)

if(CSchng == 1 ): # 0 for keep old number or failed test, 1 for valid entry
    with open(CallSgnPath, 'w') as CallSgnFile:
        CallSgnFile.write(NewCallS + '\n') #write new node number with <lf>
        CallSgnFile.close()
    os.chmod(CallSgnPath, mode=0o764)   # set the permissions to 764
    print('New CallSign '+ NewCallS + ' saved\n')
    NewCallS = NewCallS + '\n'  # for final printout formatting
else:
    print('CallSign - no change made\n')


################################################################
# check for existance of Lat Long Elev
################################################################
LLEPath = InfoDir + "LatLonElv.txt"

if (path.exists(LLEPath)):
    with open(LLEPath, 'r') as LLEFile: # file there - open it
        LatLonElv = LLEFile.readline()  # read file contents
        LLEFile.close()   # close file
        #print('\nCurrent Saved Lat, Long, Elev Assignment = '+ LatLonElv + '\n')  # display it
        Nfound = 1 #indicate file exist and displey contents
else:
    print('\nLatLonElV file not found- creating default')
    with open(LLEPath, 'w') as LLEFile:
        LatLonElv = '00.000000, -00.000000, 000\n' # create default Lat Long Elv Numbers
        LLEFile.write(LatLonElv) #write default LAt Long Elev
        LLEFile.close()
    os.chmod(LLEPath, mode=0o764)   # set the permissions to 764
    print('Created default Lat, Long, Elv =', LatLonElv)
    LatLonElv = LatLonElv + '\n'  # for final printout formatting
    Nfound = 0




################################################################
# read in the LatLonElv.txt file as .csv format
with open(LLEPath, 'r') as LLEcsvFile:
    LatLonElv=csv.reader(LLEcsvFile)
    LLEcsv = list(LatLonElv)
    LLEdat = LLEcsv.pop(0)
    #print('File - Lat:' + LLEdat[0] + ' Long:' + LLEdat[1] + ' Elev:' + LLEdat[2])
    LLEcsvFile.close()   
  
# Get the new Latitude info   
Done = 0
while Done == 0:
    print('Existing Latitude = ' + LLEdat[0])
    print('\nEnter New Latitude [format 00.000000]')
    Lat = input('or <enter> to keep this one > ')
    changeLLE = 0
    if Lat == '':
        Done = 1
        Lat = LLEdat[0]
        print('Keeping existing Latitude as ' + Lat)
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        latlth = len(Lat)
        if  latlth >= 7:  #look for 2.4 char format (allow for - sign
            print('Correct min Length of '+ str(latlth) + ' for ' + Lat)
            changeLLE = changeLLE + 1
            Done = 1
            LLEdat[0] = Lat  # assign new value to array
            print('Latitude Saved as ' + Lat)
        else:
            print('Wrong min Latitude Length of ' + str(latlth) + ' for '+ Lat)
            Done = 0
    
################################################################
# Get the new Longitude info   
Done = 0
while Done == 0:
    print('\nExisting Longitude = ' + LLEdat[1])
    print('\nEnter New Longitude [format -000.000000]')
    Long = input('or <enter> to keep this one > ')
    if Long == '':
        Done = 1
        Long = LLEdat[1]
        print('Keeping existing Longitude as ' + Long)
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        lonlth = len(Long)
        if  lonlth >= 8:  #look for 4.4 char format (allow for - sign
            print('Correct min Length of '+ str(lonlth) + ' for ' + Long)
            changeLLE = changeLLE + 1
            Done = 1
            LLEdat[1] = Long  # assign new value to array
            print('Longitude Saved as ' + Long)
        else:
            print('Wrong min Longitude Length of ' + str(lonlth) + ' for '+ Long)
            Done = 0

################################################################
# Get the new Elevation info   
Done = 0
while Done == 0:
    print('\nExisting Elevation = ' + LLEdat[2])
    print('\nEnter New Elevation in Meters [format 000]')
    Elev = input('or <enter> to keep this one > ')
    if Elev == '':
        Done = 1
        Elev = LLEdat[2]
        print('Keeping existing Elevation as ' + Elev)
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        elvlth = len(Elev)
        if  elvlth >= 2:  #look for 000 char format (allow for - sign
            print('Correct min Length of '+ str(elvlth) + ' for ' + Elev)
            changeLLE = changeLLE + 1
            Done = 1
            LLEdat[2] = Elev  # assign new value to array
            print('Elevation Saved as ' + Elev)
        else:
            print('Wrong min Elevation Length of ' + str(elvlth) + ' for '+ Elev)
            Done = 0

################################################################
# Check if need to update Lat, Long, Elev and Gridsquare
if changeLLE > 0:
    # there was a change made - save it
    nlat = float(Lat)
    nlong = float(Long)
    #print(nlat, nlong, nelev)
    GridSqr =  mh.to_maiden(nlat, nlong) # create gridsquare from Lat /Long info
    print('\nSaving New Coordinate Info')
    print('Latitude: ' + Lat)
    print('Longitude: ' + Long)
    print('Elevation: ' + Elev)
    with open(LLEPath, 'w') as LLEFile:
        LatLonElv = Lat + ',' + Long + ',' + Elev + '\n' # create default Lat Long Elv Numbers
        LLEFile.write(LatLonElv) #write default LAt Long Elev
        LLEFile.close()
    os.chmod(LLEPath, mode=0o764)   # set the permissions to 764

################################################################
    #write new Grid Square
    GSPath = InfoDir + "GridSqr"
    with open(GSPath, 'w') as GSFile:
        GSFile.write(GridSqr  + '\n')
        GSFile.close()
        os.chmod(GSPath, mode=0o764)   # set the permissions to 664 
        print('\nCalculated GridSquare: ' + GridSqr)
  
################################################################
#Check for City State info
################################################################
CSPath = InfoDir + "CityState.txt"

if (path.exists(CSPath)):
    with open(CSPath, 'r') as CSFile: # file there - open it
        CityState = CSFile.readline()  # read file contents
        CSFile.close()   # close file
        print('\nCurrent Saved City State = '+ CityState)  # display it

else:
    print('\nCityState file not found- creating default')
    with open(CSPath, 'w') as CSFile:
        CityState = 'NOCity NOState\n' # create default Lat Long Elv Numbers
        CSFile.write(CityState) #write default LAt Long Elev
        CSFile.close()
    os.chmod(CSPath, mode=0o764)   # set the permissions to 764
    print('Created default City State = ', CityState)
CSchng = 0
Done = 0
while Done == 0:
    print('Enter New City State [format City State - NO commas]')
    NewCS = input('or <enter> to keep this one > ')
    if NewCS == '':
        print('Keeping existing City State as ' + CityState[:-1])
        NewCS = CityState
        Done = 1
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        cslth = len(NewCS)
        if  cslth >= 6:
            print('Correct min Length of '+ str(cslth) + ' for ' + NewCS)
            Done =  1
            CSchng = 1
        else:
            print('Wrong min Length of ' + str(cslth) + ' for '+ NewCS)

if(CSchng == 1 ): # 0 for keep old number or failed test, 1 for valid entry
    with open(CSPath, 'w') as CSFile:
        CSFile.write(NewCS + '\n') #write new node number with <lf>
        CSFile.close()
    os.chmod(CSPath, mode=0o764)   # set the permissions to 764
    print('New City State of '+ NewCS + ' saved\n')
    NewCS = NewCS + '\n'  # for final printout formatting
else:
    print('City State - no change made')

################################################################
#Check for FreqRef info
################################################################
FreqStdPath = InfoDir + "FreqStd.txt"

if (path.exists(FreqStdPath)):
    with open(FreqStdPath, 'r') as FrqStdFile: # file there - open it
        FreqStd = FrqStdFile.readline()  # read file contents
        FrqStdFile.close()   # close file
        print('\nCurrent Saved Frequency Standard = '+ FreqStd)  # display it

else:
    print('\nFrequency Standard file not found - creating default')
    with open(FreqStdPath, 'w') as FrqStdFile:
        FreqStd = 'Unknown FreqStd\n' # create default Lat Long Elv Numbers
        FrqStdFile.write(FreqStd) #write default LAt Long Elev
        FrqStdFile.close()
    os.chmod(FreqStdPath, mode=0o764)   # set the permissions to 764
    print('Created default Frequency Standard =', FreqStd)
CSchng = 0
Done = 0
while Done == 0:
    print('Enter New Frequency Standard [XTAL, TCXO, OCXO, GPSDO, LB GPSDO, Rubidium, Cesium, Custom]')
    NewFrqStd = input('or <enter> to keep this one > ')
    if NewFrqStd == '':
        print('Keeping existing Frequency Standard as ' + FreqStd[:-1])
        NewFrqStd = FreqStd
        Done = 1
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        fslth = len(NewFrqStd)
        if  fslth >= 4:
            print('Correct min Length of '+ str(fslth) + ' for ' + NewFrqStd)
            Done =  1
            CSchng = 1
        else:
            print('Wrong min Length of ' + str(fslth) + ' for '+ NewFrqStd)

if(CSchng == 1 ): # 0 for keep old number or failed test, 1 for valid entry
    with open(FreqStdPath, 'w') as FrqStdFile:
        FrqStdFile.write(NewFrqStd + '\n') #write new node number with <lf>
        FrqStdFile.close()
    os.chmod(FreqStdPath, mode=0o764)   # set the permissions to 764
    print('New Frequency Standard '+ NewFrqStd + ' saved\n')
    NewFrqStd = NewFrqStd + '\n'  # for final printout formatting
else:
    print('Frequency Standard - no change made')

################################################################
#Get Radio1 info
################################################################
RadioPath = InfoDir + "Radio1.txt"

if (path.exists(RadioPath)):
    with open(RadioPath, 'r') as RadioFile: # file there - open it
        Radio1 = RadioFile.readline()  # read file contents
        RadioFile.close()   # close file
        print('\nCurrent Saved Radio1 = '+ Radio1)  # display it

else:
    print('\nRadio1 file not found- creating default')
    with open(RadioPath, 'w') as RadioFile:
        Radio1 = 'Mystery Radio1\n' # create default Lat Long Elv Numbers
        RadioFile.write(Radio1) #write default LAt Long Elev
        RadioFile.close()
    os.chmod(RadioPath, mode=0o764)   # set the permissions to 764
    print('Created default Radio1 =', Radio1)
CSchng = 0
Done = 0
while Done == 0:
    print('Enter New Radio1')
    NewRadio = input('or <enter> to keep this one > ')
    if NewRadio == '':
        print('Keeping existing Radio1 as ' + Radio1[:-1])
        NewRadio = Radio1
        Done = 1
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        radlth = len(NewRadio)
        if  radlth >= 6:
            print('Correct min Length of '+ str(radlth) + ' for ' + NewRadio)
            Done =  1
            CSchng = 1
        else:
            print('Wrong min Length of ' + str(radlth) + ' for '+ NewRadio)

if(CSchng == 1 ): # 0 for keep old number or failed test, 1 for valid entry
    with open(RadioPath, 'w') as RadioFile:
        RadioFile.write(NewRadio + '\n') #write new node number with <lf>
        RadioFile.close()
    os.chmod(RadioPath, mode=0o764)   # set the permissions to 764
    print('New Radio1 of '+ NewRadio + ' saved\n')
    NewRadio = NewRadio + '\n'  # for final printout formatting
else:
    print('Radio1 - no change made')

################################################################
#Get Radio1 ID info
################################################################
RIDPath = InfoDir + "Radio1ID.txt"
if (path.exists(RIDPath)):
    with open(RIDPath, 'r') as RadioIDFile: # file there - open it
        RadioID = RadioIDFile.readline()  # read file contents
        RadioIDFile.close()   # close file
        print('\nCurrent Saved Radio1 ID = '+ RadioID)  # display it

else:
    print('\nRadio1ID file not found- creating default')
    with open(RIDPath, 'w') as RadioIDFile:
        RadioID = 'No_Radio1_ID\n' # create default Lat Long Elv Numbers
        RadioIDFile.write(RadioID) #write default LAt Long Elev
        RadioIDFile.close()
    os.chmod(RIDPath, mode=0o764)   # set the permissions to 764
    print('Created default Radio1 ID =', RadioID)
CSchng = 0
Done = 0
while Done == 0:
    print('Enter New Radio1 ID')
    NewRadID = input('or <enter> to keep this one > ')
    if NewRadID == '':
        print('Keeping existing Radio1 ID as ' + NewRadID)
        NewRadID = RadioID
        Done = 1
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        RIDlth = len(NewRadID)
        if  RIDlth >= 2:
            print('Correct min Length of '+ str(RIDlth) + ' for ' + NewRadID)
            Done =  1
            CSchng = 1
        else:
            print('Wrong min Length of ' + str(RIDlth) + ' for '+ NewRadID)

if(CSchng == 1 ): # 0 for keep old number or failed test, 1 for valid entry
    with open(RIDPath, 'w') as RadioIDFile:
        RadioIDFile.write(NewRadID + '\n') #write new node number with <lf>
        RadioIDFile.close()
    os.chmod(RIDPath, mode=0o764)   # set the permissions to 764
    print('New Radio1 ID of '+ NewRadID + ' saved\n')
    NewRadID = NewRadID + '\n'  # for final printout formatting 
else:
    print('Radio1 ID - no change made')

################################################################
#Get Antenna info
################################################################
AntPath = InfoDir + "Antenna.txt"
if (path.exists(AntPath)):
    with open(AntPath, 'r') as AntFile: # file there - open it
        ANT = AntFile.readline()  # read file contents
        AntFile.close()   # close file
        print('\nCurrent Saved Antenna = '+ ANT)  # display it

else:
    print('\nAntenna file not found- creating default')
    with open(AntPath, 'w') as AntFile:
        ANT = '50 Ohm Dummy Load\n' # create default Lat Long Elv Numbers
        AntFile.write(ANT) #write default LAt Long Elev
        AntFile.close()
    os.chmod(AntPath, mode=0o764)   # set the permissions to 764
    print('Created default Antenna =', ANT)
CSchng = 0
Done = 0
while Done == 0:
    print('Enter New Antenna [Model Make]')
    NewAnt = input('or <enter> to keep this one > ')
    if NewAnt == '':
        print('Keeping existing Antenna as ' + ANT[:-1])
        NewAnt = ANT
        Done = 1
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        Antlth = len(NewAnt)
        if  Antlth >= 3:
            print('Correct min Length of '+ str(Antlth) + ' for ' + NewAnt)
            Done =  1
            CSchng = 1
        else:
            print('Wrong min Length of ' + str(Antlth) + ' for '+ NewAnt)

if(CSchng == 1 ): # 0 for keep old number or failed test, 1 for valid entry
    with open(AntPath, 'w') as AntFile:
        AntFile.write(NewAnt + '\n') #write new node number with <lf>
        AntFile.close()
    os.chmod(AntPath, mode=0o764)   # set the permissions to 764
    print('New Antenna '+ NewAnt + ' saved\n')
    NewAnt = NewAnt + '\n'  # for final printout formatting
else:
    print('Antenna - no change made')
    
################################################################
#Get System info
################################################################
SysInfoPath = InfoDir + "System.txt"
if (path.exists(SysInfoPath)):
    with open(SysInfoPath, 'r') as SysInfoFile: # file there - open it
        SysInf = SysInfoFile.readline()  # read file contents
        SysInfoFile.close()   # close file
        print('\nCurrent System Info = '+ SysInf)  # display it

else:
    print('\nSystem Info file not found- creating default')
    with open(SysInfoPath, 'w') as SysInfoFile:
        SysInf = 'A Computer running Linux\n' # create default Lat Long Elv Numbers
        SysInfoFile.write(SysInf) #write default LAt Long Elev
        SysInfoFile.close()
    os.chmod(SysInfoPath, mode=0o764)   # set the permissions to 764
    print('Created default System Info =', SysInf)
CSchng = 0
Done = 0
while Done == 0:
    print('Enter New System Info [format: CPU, OS, Software Ver]')
    NewSysInf = input('or <enter> to keep this one > ')
    if NewSysInf == '':
        NewSysInf = SysInf
        print('Keeping existing System Info as ' + NewSysInf[:-1])
        Done = 1
    else:
        # check to see if entry makes sense
        # firtst check length for correct # of chars
        SysInflth = len(NewSysInf)
        if  SysInflth >= 4:
            print('Correct min Length of '+ str(SysInflth) + ' for ' + NewSysInf)
            Done =  1
            CSchng = 1
        else:
            print('Wrong min Length of ' + str(SysInflth) + ' for '+ NewSysInf)

if(CSchng == 1 ): # 0 for keep old number or failed test, 1 for valid entry
    with open(SysInfoPath, 'w') as SysInfoFile:
        SysInfoFile.write(NewSysInf + '\n') #write new node number with <lf>
        SysInfoFile.close()
    os.chmod(SysInfoPath, mode=0o764)   # set the permissions to 764
    print('New System Info of '+ NewSysInf + ' saved\n')
    NewSysInf = NewSysInf + '\n'  # for final printout formatting
else:
    print('System Info - no change made')


################################################################
#Get remaining autogenerated infor for final listing of station info
################################################################
# Get autogenerated GridSquare
GSPath = InfoDir + "GridSqr"
if (path.exists(AntPath)):
    with open(GSPath, 'r') as GSFile: # file there - open it
        GridSqr = GSFile.readline()  # read file contents
        GSFile.close()   # close file

# Get autogenerated Beacon
BcnPath = InfoDir + "Beacon1"
Beacon1 = 'Unknown\n'
#Beacon1 = 'Unknown'  #standard write of beacon file from Main prog has no <lf>
if (path.exists(BcnPath)):
    with open(BcnPath, 'r') as BcnFile: # file there - open it
        Beacon1 = BcnFile.readline()  # read file contents
        BcnFile.close()   # close file

################################################################
################################################################
print('\n\n Final Metadata for this station:\n')

print('#######################################');
print('# MetaData for Grape Gen 1 Station');
print('#')
print('# Station Node Number      ' + NewNN[:-1] )
print('# Callsign                 ' + NewCallS[:-1])
print('# Grid Square              ' + GridSqr[:-1])
print('# Lat, Long, Elv           ' + Lat + ', '+ Long + ', '+ Elev)
print('# City State               ' + NewCS[:-1])
print('# Radio1                   ' + NewRadio[:-1])
print('# Radio1ID                 ' + NewRadID[:-1])
print('# Antenna                  ' + NewAnt[:-1])
print('# Frequency Standard       ' + NewFrqStd[:-1])
print('# System Info              ' + NewSysInf[:-1])
print('#')
#print('# Beacon Now Decoded       ' + Beacon1)  #autostore of Beacon has no <lf>
print('# Beacon Now Decoded       ' + Beacon1[:-1])
print('#')
print('#######################################')
################################################################
################################################################
#Look for optional Metadat file      
MetaPath = InfoDir + "Metadata.txt"
if (path.exists(MetaPath)):
    print('# --- Extra Metadata File ---')
    with open(MetaPath, 'r') as MetaFile: # file there - open it
        Metadat = MetaFile.readline()  # read file contents
        print('# ' + Metadat[:-1])
    MetaFile.close()   # close file 
    print('# ')
    print('#######################################')
            
#"#\n"); // Make the file end look nice
################################################################
################################################################


################################################################
################################################################
################################################################
# All done - indicate so to user
print('\n\nPSWS file structure / System Info Program Exiting Gracefully')

################################################################
################################################################
################################################################
