# Grape Gen 1 Documentation
- Documentation for the HamSCI Grape Low Cost Personal Space Weather Station Project

- This documentation is licensed with the Attribution-ShareAlike 4.0 International license https://creativecommons.org/licenses/by-sa/4.0/legalcode.

## "PSWSsetup.py" program for initializing the file directory structure and then filling in the Node's metadata

- Versions are shown with V#_## in the filename
- Latest version is copy of last version and is placed in home directory of PSWS station 
- This is normally /home/pi
- Entire directory structure is based off of path /home/pi/PSWS/
- Subdirectories include /Srawdata, /Sdata, /Sinfo, /Sstat, /Scode, /Splot, /Scmd, /Stemp, Smagtmp
- You will most liekly need to install the python pkg maidenhead to get this script to run. 
- Do this:
-  > pip install maidenhead (for Python2.7) 
-  or
-  > pip3 install maidenhead (for python3.7+)

## "PSWSinfo.py" program for reading in the Node's metadata and outputing it to a file

- Versions are shown with V#_## in the filename
- Latest version is copy of last version and is placed in home directory of PSWS station
- This is normally /home/pi
- This is a copy of the Header info that is presnt at the beginning of each day's file