# BACnet Gateway Change Log

<img src="https://bacnet.org/wp-content/uploads/sites/4/2022/05/ASHRAE-BACnet-Logo-New-1920x391.png" width=26%><a href="https://www.sensoscientific.com"><img src="https://www.sensoscientific.com/wp-content/uploads/sensoscientific-logoblue.svg" width=40%>

[<img src="https://img.shields.io/badge/dockerhub-image-brightgreen.svg?logo=DOCKER">](<https://hub.docker.com/repository/docker/michaelblack2/senso_bacnetgateway/general>) [<img src="https://img.shields.io/badge/github-library-black.svg?logo=GITHUB">](<https://github.com/michael-black2/bacnetGateway>)

--------------

#### **Table of Contents**
- [Summary](#Summary)
- [v0.0.1](#v0.0.1)

--------------

#### **Summary**
Summary of changes made to the BACnet GitHub repository and Docker Image.

--------------

#### **v0.0.1**
Inital release of SensoScientific BACnet Gateway code.
- Created ***Dockerfile.UbuntuARMv8-A*** to generate a docker image.
- Created ***README<span>.</span>md***
- Created ***ERRATA<span>.</span>md***
- Created ***CHANGE-LOG<span>.</span>md***

Apps:
- Created ***BACpypes.ini*** which stores BACnet configuration data.
- Created ***Senso_BACnetApp.py*** to get cloud data from SQLite3 database and store as data objects which are readable over BACnet.
- Created ***Senso_CloudAPIApp.py*** to get cloud data and store in SQLite3 database.
- Created ***SensoCloudLogin.ini*** which stores Cloud Login credentials.

Library:
- Created ***Dashboard<span>.</span>py*** for printing dictionary/json data to logs.
- Created ***Senso_CloudAPI.py*** library for using the SensoScientific cloud API.
- Created ***Senso_DataTypes.py*** library for class structure and conditioning of SensoScientific cloud data.
- Created ***Senso_MongoDB.py*** library for interfacing with a MongoDB server.
- Created ***Senso_SQLiteDB.py*** library for interfacing with a SQLite3 server. This is added for use with ARMv8-A Architectures incompatible with MongoDB (i.e. RPI).
- Created ***Senso_SQLServerDB.py*** for interfacing with a MSSQL server (incomplete)

Ubuntu/Container/logrotate:
- Created ***BACnet*** which stores the BACnet.log configuration to be used in the Dockerfile image of senso_bacnetgateway.
- Created ***logrotate.conf*** to be used in the Dockerfile image of senso_bacnetgateway.

Ubuntu/Container:
- Created ***crontab-container*** for cron tasks in the container.
- Created ***Senso_BACnetApp.sh*** ubuntu bash to run perioidically which checks if the App is running, cleans any errors, and runs the app if not alreay running.
- Created ***Senso_CloudAPIApp.sh*** ubuntu bash to run perioidically which checks if the App is running, cleans any errors, and runs the app if not alreay running.
- Created ***Senso_DockerBuildRun.sh*** ubuntu bash to build the dockerfile and run the container locally to test it. Should be executed from the root folder (BACnetGateway).
- Created ***Senso_Install_mongoDB.sh*** ubuntu bash to be run on hardware for testing of the mongodb-community docker image.
- Created ***Senso_KillAll.sh*** ubuntu bash to kill all SensoScientific applications currently running (***Senso_CloudAPIApp.py***, ***Senso_BACnetApp.py***, etc...).
- Created ***Senso_MongoDB.sh*** ubuntu bash to run perioidically which checks if the server is running, cleans any errors, and runs the server if not alreay running.


Ubuntu/Gateway:
- Created ***crontab-gateway*** for cron tasks in the gateway.
- Created ***DHCPConfig.ini*** which stores an example DHCP configuration.
- Created ***Gateway-Setup-Guide<span>.</span>md*** which provides gateway setup instructions.
- Created ***IPConfig.ini*** which stores the IP configuration which will be used for the gateway.
- Created ***Senso_BACnetGateway.sh*** ubuntu bash to initialize and run a senso_bacnetgateway docker container on hardware (i.e. raspberry pi) and set cloud credentials.
- Created ***Senso_InstallCron.sh*** ubuntu bash to initialize gateway cron tasks.
- Created ***Senso_SetCloudCred.sh*** ubuntu bash to set the SensoScientific Cloud credentials to be used by the container.
- Created ***Senso_SetGatewayIP.sh*** ubuntu bash to set the IP configuration of the gateway.
- Created ***StaticIPConfig.ini*** which stores an example Static IP configuration.