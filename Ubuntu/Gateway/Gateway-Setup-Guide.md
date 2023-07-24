# Gateway Setup Guide

### Initialization Image
Generate an image from RPI Imager
- Root Image: "Ubuntu Server 23.04 (64-bit)
- Check Set hostname: "senso-bacnetgateway"
- Check Enable SSH
    - Check Use Password authentication
- Check Set username and password
    - username: "senso"
    - password: (See password manager)
- Check Set locale settings
    - Time zone: "America/Los_Angeles"
    - Keyboard layout: "us"

Install the SD into the device and connect to ethernet. After connected, ping the senso-bacnetgateway hostname to confirm that connection is established.

Input the following files into the RPI by sending files over SSH:
> scp crontab-gateway DHCPConfig.ini IPConfig.ini Senso_BACnetGateway.sh Senso_SetCloudCred.sh Senso_SetGatewayIP.sh StaticIPConfig.ini Senso_InstallCron.sh senso@senso-bacnetgateway.local:/home/senso/

### Install Existing Image to SD
If the image already exists, install using the RPI utility and select the latest image. It is not neccessary to initialize a new image each time. If the image is already created and initalized properly, it will have all documents required to setup the device:
- Senso_InstallCron.sh - Sets the crontab-gateway task
    - crontab-gateway - Configuration for cron task
- Senso_BACnetGateway.sh - Starts BACnet container and sets credentials
- Senso_SetGatewayIP.sh - Sets the device IP Address (static or DHCP)
    - IPConfig.ini - Configuration to be used by the script
    - StaticIPConfig.ini - Example of Static IP Configuration
    - DHCPConfig.ini - Example of DHCP Configuration
- Senso_SetCloudCred.sh - Sets the cloud credentials (used by Senso_BACnetGateway.sh)

### Setup Instructions
The following must be done in order to configure a device for application operation.

1. The cloud credentials must be set in crontab-gateway:
> cd /home/senso/
> nano crontab-gateway
>> @reboot sudo bash /home/senso/Senso_BACnetGateway.sh "my@cloud-username.com" "cloud-password123" >> /var/log/cron.log 2>&1
* Note: Keep the quotation marks around the username and password

2. The IP configuration must be set in IPConfig (see instructions below)

3. The cron task must be installed:
> sudo bash Senso_InstallCron.sh

4. Reboot the device. After rebooting, the device may take a up to 5 minutes to download all updates and connect to cloud.

5. Check if the configuration was successful. Connect to the device and check the device logs:
> ssh senso@"static ip or hostname"
> cat /var/log/cron.log

Below is an example of a successfuly output within cron.log:

    Docker version 20.10.21, build 20.10.21-0ubuntu3
    Login Succeeded
    michaelblack2/senso_bacnetgateway latest 1e98b65d7b0f 20 hours ago 246MB
    michaelblack2/senso_bacnetgateway image found
    Cannot call openvswitch: ovsdb-server.service is not running.

    ** (process:1257): WARNING **: 10:32:57.448: Permissions for /etc/netplan/00-default-nm-renderer.yaml are too open. Netplan configuration should NOT be accessible by others.
    latest: Pulling from michaelblack2/senso_bacnetgateway
    Digest: sha256:347198a00db74558e0e733653939b4d2c598dbf90701411b32613c5ff8810f2b
    Status: Image is up to date for michaelblack2/senso_bacnetgateway:latest
    docker.io/michaelblack2/senso_bacnetgateway:latest
    container status: false
    Container is created but not running
    Restarting container: bacnetgateway

    ** (process:1257): WARNING **: 10:32:58.762: Permissions for /etc/netplan/00-default-nm-renderer.yaml are too open. Netplan configuration should NOT be accessible by others.

    ** (process:1257): WARNING **: 10:32:58.762: Permissions for /etc/netplan/00-default-nm-renderer.yaml are too open. Netplan configuration should NOT be accessible by others.
    Success
    bacnetgateway
    Container is running
    Setting SensoScientific Cloud credentials..

### Set Static IP
Set the configuration of the Static IP configuration using:
> cd /home/senso/
> nano StaticIPConfig.ini

Once complete copy the file to the IP Configuration using:
> cp StaticIPConfig.ini IPConfig.ini

Either reboot the device or run the following command:
> bash Senso_SetGatewayIP.sh -ini

The above command will likely halt the SSH session and kick out the user. Check if the configuration worked by pinging to new assigned Static IP:
> ping "static ip"

SSH to this new Static IP by using:
> ssh senso@"static ip"

For example:
> ssh senso@192.168.3.232

### Set DHCP
Copy the DHCP configuration file to the IP Configuration using:
> cp DHCPConfig.ini IPConfig.ini

Either reboot the device or run the following command:
> bash Senso_SetGatewayIP.sh -ini

The above command will likely halt the SSH session and kick out the user. Check if the configuration worked by pinging to new assigned Static IP:
> ping senso-bacnetgateway

### Connect to Container
Connect to the container from inside the RPI to check the logs of the services running:
Connect to RPI SSH:
> ssh senso@senso-bacnetgatway.local

or
> ssh senso@"static ip"

Connect to the container:
> sudo docker exec -it bacnetgateway sh