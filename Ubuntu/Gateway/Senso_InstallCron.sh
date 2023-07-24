#!/bin/bash

sudo cp /home/senso/crontab-gateway /etc/cron.d/BACnet-cron
sudo chmod 0644 /etc/cron.d/BACnet-cron
sudo touch /var/log/cron.log
sudo crontab /etc/cron.d/BACnet-cron