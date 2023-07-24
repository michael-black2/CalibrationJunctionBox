#!/bin/bash

# Set the SensoScientific Cloud username and password for the Docker Container

username=""
password=""

if [[ ! -z $1 ]] && [[ ! -z $2 ]]; then
    username=$1
    password=$2
fi;

container_name="bacnetgateway"

file="[SensoCloudLogin]\nusername: ${username}\npassword: ${password}";
destdir=/opt/BACnetGateway/Apps/SensoCloudLogin.ini;
docker exec ${container_name} sh -c "echo '${file}' > '${destdir}'";