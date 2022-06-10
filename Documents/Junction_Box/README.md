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


