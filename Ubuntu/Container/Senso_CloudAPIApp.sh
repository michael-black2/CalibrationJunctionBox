#!/bin/bash

# To be run every minute in crontab for monitoring and restarting the app as necessary

path="/opt/BACnetGateway/Apps"
logpath="/var/log/BACnetGateway"
program_name="python3 ${path}/Senso_CloudAPIApp.py"
logname="CloudAPI"

active=0
duplicate=0
killed=0
error=0

pid_list=$(pgrep -d, -f "${program_name}")
if [[ ! -z "$pid_list" ]];then
    progs=$(ps --no-headers -p"${pid_list}" -o state)
    for i in ${progs};do
        if [[ "${i}" == "S" ]] && [[ ${active} == 0 ]];then
            echo Active program found;
            active=1;
        elif [[ "${i}" -eq "S" ]] && [[ ${active} -eq 1 ]];then
            echo Duplicate program found;
            duplicate=1;
        fi;
    done;
fi;

if [[ ${active} == 1 ]] && [[ ${duplicate} == 0 ]];then
    echo "Active with no issues";
    exit 0
fi;

if [[ ${duplicate} == 1 ]];then
    echo "Killing all programs due to duplicate found"
    for i in $(pgrep -f "${program_name}");do 
        kill $i;
        if [[ $? -ne 0 ]];then 
            echo "Not able to kill programs";
            error=1;
            exit 1
        fi;
    done;
fi;

if [[ ${active} == 0 ]];then
    echo "Starting ${program_name}";
    nohup ${program_name} >> ${logpath}/${logname}.log 2>&1 &
    exit 0
fi;