#!/bin/bash

# Runs SensoScientific BACnet Gateway Functionality on local hardware (i.e. Raspberry Pi)

# Implimentation
# >> /etc/crontab
# @reboot root bash Senso_BACnetGateway.sh
# Starts system and runs a check upon reboot

#
# @reboot bash ./Senso_CloudAPIApp.sh <cloud_username> <cloud_password>
#

# SensoScientific Cloud Login Credentials
if [[ ! -z $1 ]] && [[ ! -z $2 ]];then
    cloud_username=$1
    cloud_password=$2
    set_cred=1
else
    set_cred=0
fi;

docker --version
if [[ $? -ne 0 ]];then
    echo "Docker engine not yet install"
    echo "Installing docker.io..."
    sudo apt-get update
    #docker_version="5:24.0.2-1~ubuntu.22.04~jammy"
    #sudo apt-get install docker-ce=${docker_version} docker-ce-cli=${docker_version} containerd.io docker-buildx-plugin docker-compose-plugin
    sudo apt-get install -y docker.io
fi;

#sudo cat Docker_password.txt | docker login --quiet --username "michaelblack2" --password-stdin
sudo docker login --username "michaelblack2" --password "michael89" 2> /dev/null
if [[ $? -ne 0 ]];then
    echo "Authentication failed, aborting!"
    exit 1
fi;

image="michaelblack2/senso_bacnetgateway"
version="latest"
fallback_version="v0.0.1"
container_name="bacnetgateway"

image_exists=0;
image_version_exists=0;

check_image_list=$( sudo docker image ls | grep ${image} );
echo ${check_image_list}
if [[ -z $check_image_list ]];then
    echo "${image} image not found"
    image_exists=0
else
    echo "${image} image found"
    image_exists=1
fi;

# Check for image tag (version)
#if [[ ${image_exists} -eq 1 ]];then
#    for i in $( docker image ls | grep ${repo} );do 
#        echo ${i}
#        if [[ ${i} == ${version} ]];then 
#            echo "${repo}:${version} image version found"
#            image_version_exists=1;
#        fi;
#    done;
#fi;

# Get the latest image
sudo docker pull ${image}:${version}
if [[ $? -ne 0 ]];then
    echo "Error pulling repo"
    exit 1
fi;

# Check if container is running
container_running=0
status=$( sudo docker container inspect -f '{{.State.Running}}' ${container_name} )
echo "container status: $status"
if [[ "${status}" == "" ]]; then 
    echo "container is not running"
    container_running=0;
    echo "Start running container: ${container_name}"
    sudo docker run --name ${container_name} -d -p 47808:47808/udp ${image}:${version}
elif [[ "${status}" == "false" ]]; then 
    echo "Container is created but not running" 
    echo "Restarting container: ${container_name}"
    sudo docker restart ${container_name}
elif [[ "${status}" == "true" ]]; then 
    echo "container is running"
    container_running=1;
fi;


# If container is still not running
if [[ ${container_running} -eq 0 ]]; then
    status=$( sudo docker container inspect -f '{{.State.Running}}' ${container_name} )
    if [[ "${status}" == "true" ]]; then 
        echo "Container is running"
        container_running=1
    elif [[ "${status}" == "false" ]]; then
        echo "Container start failed!"
        echo "Restarting the container: ${container_name}"
        sudo docker restart ${container_name}
        if [[ $? == ${container_name} ]];then
            echo "container restarted successfully"
            container_running=1;
        else    
            exit 1;
        fi;
    fi;
    else
        echo "Unknown error occurred"
fi;

if [[ ${set_cred} -eq 1 ]]; then
    echo "Setting SensoScientific Cloud credentials.."
    bash /home/senso/Senso_SetCloudCred.sh ${cloud_username} ${cloud_password}
else
    echo "SensoScientific Cloud credentials are not set"
fi;