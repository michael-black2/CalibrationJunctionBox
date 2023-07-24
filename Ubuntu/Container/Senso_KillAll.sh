#!/bin/bash

# Kill all senso applications

#program_name="python3 /home/mblack/Documents/GitHub/bacnetGateway/Apps/Senso_"
programs=("python3 /opt/BACnetGateway/Apps/Senso_" "mongod")
error=0
killcount=0
total=0

echo "Killing all Senso BACnet applications..."
for program in ${programs};do
    for pid in $(pgrep -f "${program}");do 
        kill -9 $pid;
        if [[ $? -ne 0 ]];then 
            echo "Not able to kill this application";
            error=$(( $error + 1 ));
            total=$(( $total + 1 ));
        else
            killcount=$(( $killcount + 1 ));
            total=$(( $total + 1 ));
        fi;
    done;
done;

if [[ ${error} -eq 0 ]];then
    echo "All applications killed successfully"
    echo "${killcount} applications killed"
else
    echo "Not all applications killed successfully"
    echo "${error} of ${total} application killed"
fi
