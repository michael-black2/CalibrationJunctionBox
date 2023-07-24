# Calibration Junction Box

<img src="https://bacnet.org/wp-content/uploads/sites/4/2022/05/ASHRAE-BACnet-Logo-New-1920x391.png" width=26%><a href="https://www.sensoscientific.com"><img src="https://www.sensoscientific.com/wp-content/uploads/sensoscientific-logoblue.svg" width=40%>

[<img src="https://img.shields.io/badge/dockerhub-image-brightgreen.svg?logo=DOCKER">](<https://hub.docker.com/repository/docker/michaelblack2/senso_bacnetgateway/general>) [<img src="https://img.shields.io/badge/github-library-black.svg?logo=GITHUB">](<https://github.com/michael-black2/bacnetGateway>)

--------------

#### **Table of Contents**
- [Summary](#Summary)
- [Features](#Features)
- [Implementation](#Implementation)
  - [Hardware](#Hardware)
  - [Software](#Software)
- [Support](#Support)

--------------

#### **Summary**
Software/Firmware to operate the Calibration Junction Box. This program uses the Launcher.sh unix shell script to run a JunctionBox python script on reboot. This program references LED_UI, HTTP_POST, ADS1248, and MuxCtrl. These libraries operate the device. Another program can be used to calibrate teh device. This seperate python script is called Calibration_RTD and generates a text fiel called calibration.txt. Both Calibration_RTD and JunctionBox reference this text file to determine the calibration. 

Setup the tasks within crontab which is a usefull task management tool within ubuntu

Start by creating a power shell script
Go to terminal prompt

cd "workspace"


create a crontab script
Go to the terminal
type:
sudo crontab -e
go to the bottom and add the following

@reboot sudo "power shell program.sh" >> "location and name of log file for issues.txt" 2>&1

example:
@reboot sudo /home/pi/Documents/Junction_Box/launcher.sh >> /home/pi/Documents/Junction_Box/log.txt 2>&1


SPI and I2C need to be enabled on the device by goign to the system config and the latest updates need to be installed
https://www.takaitra.com/spi-device-raspberry-pi/
The above link gives steps in doing this

Make sure to install spidev, smbus2, and any other external libraries which are used.
--------------

#### **Features**
The following lists the features of the system which are supported.
Version: v0.0.1
- SensoScienific API Read-Only
  - Temperature (Analog Input Object)
  - Humidity (Analog Input Object)
  - Differential Pressure (Analog Input Object)
  - Light Sensor (Binary Input Object)
  - Light Intensity Sensor (Analog Input Object)
  - Universal (0-5V, 0-10V, 4-20mA) (Analog Input Object)
  - Open/Close (Binary Data Object)
  - Add/Delete/Update Local Database used by BACnet
- MongoDB Read/Write
- SQLite3 Server/Read/Write
- Microsoft SQL Read/Write
- BACnet
  - Read/Write Data Objects (Currently only utilizing read objects due to API Read-Only limitation)
  - CoV (Untested)
  - Auto-detect IP Address
  - Optional .ini configuration (overrides auto-detect if used)
- Docker
  - Dockerfile
  - Docker image build and push script not available
  - Docker image - senso_bacnetgateway (Size: 246.33 MB)

--------------

#### **Specifications**

| Subsystem               | Item        | Value                                     |
|-------------------------|-------------|-------------------------------------------|
| BACnet Service          | IP          | DHCP* and Static                          |
| -                       | Port        | 47808*                                    |
| -                       | Read        | Yes                                       |
| -                       | Write       | No                                        |
| -                       | Obj Name    | SensoScientific BACnet Gateway*           |
| -                       | GW Obj ID   | 600*                                      |
| -                       | Data Obj ID | Matches SensoScientific Node ID w/ prefix |
| SensoScientific Cloud   | IP          | DHCP                                      |
| -                       | Port        | 443*                                      |
| -                       | Read        | Yes                                       |
| -                       | Write       | No                                        |
| -                       | DNS         | https://webapi.sensoscientific.com/*      |
| -                       | Username    | user-assigned                             |
| -                       | Password    | user-assigned                             |
| -                       | Cloud Env.  | Life Science Cloud                        |

*Default Value

--------------

#### **Implementation**
The following are different implementation options for utilizing the Calibration Junction Box.

##### **Hardware**
A local Raspberry Pi 4 Model B can be used for implementation of the Calibration Junction Box. Input the following line into crontab in order to implement the SubG gateway at boot. See [Gateway Setup Guide](Ubuntu/Gateway/Gateway-Setup-Guide.md) for more instructions.

##### **Software**
An application which is run on an existing server can be used as long as the server has access to the port and subnet which the BMS server runs on. All appropriate code is available within this repository. There will be a future version with an executable or script which can run to start the BACnet service on a server.

--------------

#### **Support**
The docker image and github repository are currently supported by SensoScientific. Click on the docker image above to go to the repo web page.