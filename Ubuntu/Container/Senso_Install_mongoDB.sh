#!/bin/bash

# Start docker mongodb container on local machine (not docker container)

sudo cat Docker_password.txt | docker login --quiet --username "michaelblack2" --password-stdin
if [[ $? -ne 0 ]];then
    exit 1
fi

mongoDB_version="6.0.4-ubi8-20230612T062634Z"
container_name="mongodb"
image_exists=0

for i in $(docker image ls);do 
    if [[ ${i} == ${mongoDB_version} ]];then 
        image_exists=1;
    fi;
done;

# If image does not exist pull it to local
if [[ ${image_exists} -eq 0 ]];then
    docker pull mongodb/mongodb-community-server:$mongoDB_version
fi

# If container is running
if [ "$( docker container inspect -f '{{.State.Running}}' $container_name )" = "true" ]; then 
    echo "container is running"
    exit 0
else
    echo "container is not running"
    docker run --name ${container_name} -d -p 27017:27017 mongodb/mongodb-community-server:$mongoDB_version
fi

# If container is still not running
if [ "$( docker container inspect -f '{{.State.Running}}' $container_name )" = "true" ]; then 
    echo "container is running"
else
    echo "container start failed!"
    docker restart mongodb
    if [[ $? == $container_name ]];then
        echo "container restarted successfully"
    fi
fi