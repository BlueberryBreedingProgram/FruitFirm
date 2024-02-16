# FruitFirm
Locate the FruitFirm machine, an Ethernet Cable, a USB drive, and a USB keyboard.

Load the above python script, and system service file, onto the USB drive, and connect the drive and the USB keyboard to each of the two free FruitFirm USB ports. Connect the FuritFirm to ethernet to any of the wall ports in the Fruit Quality lab (I've been told they are already activated and have tested them as of August).

Power the FruitFirm on using the switch on the back, when the boot process completes, you should be on the main screen of the FruitFirm graphical interface. It's necessary to get to the Command line interface, this can be done by using the keyboard to enter "Ctrl+Alt+F2". 

Run the following command "pip3 install requests numpy watchdog" to install the script dependencies globally.

Navigate to the directory where the mounted USB stick resides, I believe it is "/media/pi/usb/", and execute two "cp" commands to copy and paste FirebaseUploadService.py to "/home/pi/" for example or whatever the corresponding user directory is on the FruitFirm. and copy firebaseuploadservice.service to " /etc/systemd/system/ " . You might need to adjust the contents of firebaseuploadservice.service using a text editor like nano, if the python script is placed in a directory other than /home/pi/. 

Adjust permissions to ensure the script is executable using a command like "chmod +x /home/pi/FirebaseUploadService.py"
You might need to adjust FirebaseUploadService.py, to change the variable "TARGET_DIRECTORY" in the event that I'm wrong about the USB stick mount path being "/media/pi/usb/" . 

Reload the system service daemon: "sudo systemctl daemon-reload"

Enable the service: "sudo systemctl enable firebaseuploadservice"

Check the service status: "sudo systemctl status firebaseuploadservice"

Restart the FruitFirm and try to do a "run" with some berries, the test run should utilize the test barcode "55".

** NOTE: I believe that when the FruitFirm is operating normally, the files are places on the root of the USB stick in the "/media/pi/usb/", it is possible that they are places in something like "/media/pi/usb/{currentDate}", if thats the case, the python script path will need to be modified to change the TARGET PATH, which is marked with a comment. ​***
