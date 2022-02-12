#!/bin/bash
# Xfer all old processed files to repo
# Jan 19, 2022 N8OBJ
#
# first - processed Sdata files
#
ls -1 /home/pi/PSWS/Sdata/ > /home/pi/PSWS/Stemp/sfsdlist
awk '{print "/home/pi/PSWS/Sdata/" $0}' /home/pi/PSWS/Stemp/sfsdlist > /home/pi/PSWS/Stemp/sdgo2repo
echo 'Sdata Files to send to Repo:'
cat /home/pi/PSWS/Stemp/sdgo2repo
echo 'Attempting xfer to repo...'
if (< /home/pi/PSWS/Stemp/sdgo2repo xargs -I %  curl -u "ftpuser:2021HamSciWWV" -T "{%}" ftp://35.85.92.69/);
    then
    echo 'Sdata Files transferred ok!';rm /home/pi/PSWS/Stemp/sfsdlist; rm /home/pi/PSWS/Stemp/sdgo2repo;
else
    echo 'Sdata File xfer failed';
fi
#
# second - processed Splot files
#
ls -1 /home/pi/PSWS/Splot/ > /home/pi/PSWS/Stemp/sfsplist
awk '{print "/home/pi/PSWS/Splot/" $0}' /home/pi/PSWS/Stemp/sfsplist > /home/pi/PSWS/Stemp/spgo2repo
echo 'Splot Files to send to Repo:'
cat /home/pi/PSWS/Stemp/spgo2repo
echo 'Attempting xfer to repo...'
if (< /home/pi/PSWS/Stemp/spgo2repo xargs -I %  curl -u "ftpuser:2021HamSciWWV" -T "{%}" ftp://35.85.92.69/);
    then
    echo 'Splot Files transferred ok!';rm /home/pi/PSWS/Stemp/sfsplist; rm /home/pi/PSWS/Stemp/spgo2repo;
else
    echo 'Splot File xfer failed';
fi
