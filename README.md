# CalibrationJunctionBox

Software/Firmware to operate the Calibration Junction Box. This program uses the Launcher.sh unix shell script to run a JunctionBox python script on reboot. This program references LED_UI, HTTP_POST, ADS1248, and MuxCtrl. These libraries operate the device. Another program can be used to calibrate teh device. This seperate python script is called Calibration_RTD and generates a text fiel called calibration.txt. Both Calibration_RTD and JunctionBox reference this text file to determine the calibration. 
