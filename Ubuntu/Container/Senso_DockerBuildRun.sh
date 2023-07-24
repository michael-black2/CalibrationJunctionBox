#!/bin/bash

# Build and Push the Docker Image

path="/home/mblack/Documents/GitHub/BACnetGateway"
cd ${path}
username="michaelblack2"
image_name="senso_bacnetgateway"
tag1="v0.0.1"
tag2="latest"
container_name="bacnetgateway"
dockerfile_name="Dockerfile.UbuntuARMv8-A"

cloud_username=""
cloud_password=""

docker container kill ${container_name}
docker container rm ${container_name}
docker image rm "${username}/${image_name}:${tag1}" 
docker image rm "${username}/${image_name}:${tag2}" 

docker build -f ${dockerfile_name} -t "${username}/${image_name}:${tag1}" -t "${username}/${image_name}:${tag2}" .

# docker network create --subnet=192.168.3.232/23 my-net
#-p 443:443/tcp
# --network=my-net --ip=192.168.3.232
docker container run -d --name ${container_name} -p 47808:47808/udp --privileged "${username}/${image_name}:${tag2}"

if [[ ${cloud_username} -ne "" ]] && [[ ${cloud_password} -ne "" ]]; then
    echo "Setting SensoScientific Cloud credentials.."
    bash Senso_SetCloudCred.sh ${cloud_username} ${cloud_password}
else
    echo "SensoScientific Cloud credentials are not set"
fi;