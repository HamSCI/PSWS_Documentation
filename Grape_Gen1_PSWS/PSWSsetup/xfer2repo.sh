#!/bin/bash
# xfer2repo.sh - bash script to transfer the daily created data files from a Grape1 PSWS to the main repo
# 1-29-2022 Ver 1.00 by KD8CGH / N8OBJ
ls -1 /home/pi/PSWS/Sxfer/ > /home/pi/PSWS/Stemp/sflist
awk '{print "/home/pi/PSWS/Sxfer/" $0}' /home/pi/PSWS/Stemp/sflist > /home/pi/PSWS/Stemp/go2repo
echo 'Files to send to Repo:'
cat /home/pi/PSWS/Stemp/go2repo
echo 'Attempting xfer to repo...'
if (< /home/pi/PSWS/Stemp/go2repo xargs -I %  curl -u "grape@wwvarc.org:5F3gjdEKEt" -T "{%}" ftp://208.109.41.230/);
then
    echo 'Files transferred ok - removing them from ~/Sxfer/'; rm /home/pi/PSWS/Sxfer/*;
else
    echo 'File xfer failed - leaving files in /SXfer/ for next try tomorrow';
fi
