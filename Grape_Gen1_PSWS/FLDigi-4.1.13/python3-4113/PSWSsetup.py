#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 21, 2020
Create PSWS directory Structure

@author jcgibbons N8OBJ
"""

import os
from os import path
import sys

# ~ points to users home directory - usually /home/pi/
homepath = os.path.expanduser('~')
print('Home Path = ' + homepath)

PSWSDir = homepath + "/PSWS/"
RawdataDir = PSWSDir + 'Srawdata'
InfoDir = PSWSDir + 'Sinfo'
CmdDir = PSWSDir + "Scmd"
TempDir = PSWSDir + "Stemp"
StatDir = PSWSDir + "Sstat"
CodeDir = PSWSDir + "Scode"
PlotDir = PSWSDir + "Splot"
DataDir = PSWSDir + "Sdata"

#Check for main base Directory 
# make sure PSWS path exists - if not, create it with correct permissions
if (path.exists(PSWSDir)):
    print('Base Dir PSWS exists ' + PSWSDir)
else:
    print('PSWS Not there - Creating path ' + PSWSDir)
    os.mkdir(PSWSDir)           # create tyhe directory
    os.chmod(PSWSDir, mode=0o774)   # set the permissions to 764

#Check for the subdirectories
# make sure Rawdata path exists - if not, create it with correct permissions
if (path.exists(RawdataDir)):
    print('Srawdata exists ' + RawdataDir)
else:
    print('Not there - making path ' + RawdataDir)
    os.mkdir(RawdataDir)           # create tyhe directory
    os.chmod(RawdataDir, mode=0o764)   # set the permissions to 764

# make sure Sinfo path exists - if not, create it with correct permissions
if (path.exists(InfoDir)):
    print('Sinfo exists ' + InfoDir)
else:
    print('Not there - making path ' + InfoDir)
    os.mkdir(InfoDir)           # create tyhe directory
    os.chmod(InfoDir, mode=0o764)   # set the permissions to 764

# make sure Scmd path exists - if not, create it with correct permissions
if (path.exists(CmdDir)):
    print('Scmd exists ' + CmdDir)
else:
    print('Not there - making path ' + CmdDir)
    os.mkdir(CmdDir)           # create tyhe directory
    os.chmod(CmdDir, mode=0o774)   # set the permissions to 764

# make sure Stemp path exists - if not, create it with correct permissions
if (path.exists(TempDir)):
    print('Stemp exists ' + TempDir)
else:
    print('Not there - making path ' + TempDir)
    os.mkdir(TempDir)           # create tyhe directory
    os.chmod(TempDir, mode=0o764)   # set the permissions to 764

# make sure Sstat path exists - if not, create it with correct permissions
if (path.exists(StatDir)):
    print('Sstat exists ' + StatDir)
else:
    print('Not there - making path ' + StatDir)
    os.mkdir(StatDir)           # create tyhe directory
    os.chmod(StatDir, mode=0o764)   # set the permissions to 764

# make sure Scode path exists - if not, create it with correct permissions
if (path.exists(CodeDir)):
    print('Scode exists ' + CodeDir)
else:
    print('Not there - making path ' + CodeDir)
    os.mkdir(CodeDir)           # create tyhe directory
    os.chmod(CodeDir, mode=0o774)   # set the permissions to 764

# make sure Splot path exists - if not, create it with correct permissions
if (path.exists(PlotDir)):
    print('Splot exists ' + PlotDir)
else:
    print('Not there - making path ' + PlotDir)
    os.mkdir(PlotDir)           # create tyhe directory
    os.chmod(PlotDir, mode=0o774)   # set the permissions to 764

# make sure Sdata path exists - if not, create it with correct permissions
if (path.exists(DataDir)):
    print('Sdata exists ' + DataDir)
else:
    print('Not there - making path ' + DataDir)
    os.mkdir(DataDir)           # create tyhe directory
    os.chmod(DataDir, mode=0o764)   # set the permissions to 764

print('Exiting PSWS file structure creation program gracefully')
