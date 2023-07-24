#!/bin/bash

# Sets the BACnet Gateway to a static IP
# Sets the Interface, Router IP, and DNS IP if not set in IPConfig.ini

# Set static IP with all other paramters default
# bash Senso_SetGatewayIP.sh -d 192.168.3.54

# Set static IP and all other paramters using .ini file (make sure to set IPConfig.ini first)
# bash Senso_SetGatewayIP.sh -ini

# Set Static IP and all other paramters with input on command prompt
# bash Senso_SetGatewayIP.sh


dir="/home/senso"
set_cfg_file_name="IPConfig.ini"
next_file_name="IPConfig.yaml"
ip_address_set=0
use_ini=0
use_default=0
if [[ ! -z $1 ]]; then
    if [[ $1 -eq "-ini" ]]; then
        use_ini=1;
    elif [[ $1 -eq "-d" ]]; then
        use_default=1
        ip_address_set=$2
    fi;
fi;

interface=$( ip addr | awk '/state UP/ {print $2}' | sed 's/.$//' )
echo "current interface: ${interface}"
static_routers=$( ip route show | grep -i 'default via'| awk '{print $3}' )
echo "static_routers: ${static_routers}"
domain_name_servers=$( grep "nameserver" /etc/resolv.conf | awk '{print $2}' )
echo "domain_name_servers: ${domain_name_servers}"

cidr_subnetmask=$( ip addr | grep eno1 | grep inet | awk '{print $2}' | tr "/" " " | awk '{print $2}' )
ip_address=$( ip addr | grep eno1 | grep inet | awk '{print $2}' )
echo "current ip_address: ${ip_address}"
echo ""

if [[ $use_ini -eq 0 ]] && [[ use_default -eq 0 ]]; then
    echo "Fill in the below fields. Input nothing and press enter to keep the current configuration"
    echo -n "Set interface: "
    read interface_new
    if [[ $interface_new -ne "" ]]; then
        interface=$interface_new
    fi;

    echo -n "Set ip_address (CIDR): "
    read ip_address_new
    if [[ $ip_address_new -ne "" ]]; then
        ip_address=$ip_address_new
    fi;

    echo -n "Set static_routers ip: "
    read static_routers_new
    if [[ $static_routers_new -ne "" ]]; then
        ip_address=$static_routers_new
    fi;

    echo -n "Set domain_name_servers ip: "
    read domain_name_servers_new
    if [[ $domain_name_servers_new -ne "" ]]; then
        ip_address=$domain_name_servers_new
    fi;
    configuration=\
    "network:
      ethernets:
        ${interface}:
        dhcp4: false
         addresses:
          - ${ip_address}
         routes:
          - to: default
           via: ${static_routers}
         nameservers:
           addresses: [${domain_name_servers}]
    "
elif [[ use_default -eq 1 ]]; then
    configuration=\
    "network:
      ethernets:
        ${interface}:
        dhcp4: false
         addresses:
          - ${ip_address_set}
         routes:
          - to: default
           via: ${static_routers}
         nameservers:
           addresses: [${domain_name_servers}]
    "
else
    configuration=$( cat ${dir}/${set_cfg_file_name} )
fi;

printf $configuration
echo ""
echo "Inputing into configuration..."

# Set Static IP Configuration
sudo touch ${dir}/${next_file_name}
sudo chmod 777 ${dir}/${next_file_name}
printf "${configuration}" > ${dir}/${next_file_name}
sudo cp ${dir}/${next_file_name} /etc/netplan/50-cloud-init.yaml

dhcp=false
for i in $configuration; do
    if [[ $read_dhcp -eq 1 ]]; then
        dhcp=$i
        read_dhcp=0
    elif [[ $i -eq "dhcp4:" ]]; then
        read_dhcp=1;
    fi;
done;
if [[ $dhcp -eq false ]]; then
    # Stop Initialization at reboot which overwrites the Static IP
    sudo touch ${dir}/99-disable-network-config.cfg
    sudo chmod 777 ${dir}/99-disable-network-config.cfg
    sudo echo "network: {config: disabled}" > ${dir}/99-disable-network-config.cfg
    sudo cp ${dir}/99-disable-network-config.cfg /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
else
    # Start Initialization at reboot to overwrite the Static IP
    sudo rm /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
fi;

# Set the configuration
sudo netplan apply
if [[ $? -eq 0 ]]; then
    echo "Success"
else
    echo "Failure"
fi;