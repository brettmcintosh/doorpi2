## DoorPi

#### Overview:

The aim of this project is to create a low-cost, customizable security system using a Raspberry Pi and Python3.
The Pi uses sensors to detect if a door has been opened and a camera to record the entry.
The alarm can be armed or disarmed using an NFC card or via the web interface.
The alarm status is indicated by sounds and addressable LED animations.
The alarm will send an email notification if not disarmed within a set amount of time.
[Here](https://youtu.be/7nwuVskN5R8) is a video of the system in action.

#### Spec:
* If an NFC card is scanned and the NFC ID is valid:
    * If the alarm is armed:
        * The alarm status changes to disarmed.
        * The remaining tasks in the entry routine are canceled.
        * The sensors stop scanning and the camera is turned off.
        * The disarm routine is started:
            * The disarmed LED animation is displayed.
            * The disarmed sound is played.
    * If the alarm is disarmed:
        * The alarm status changes to armed and the arm routine is started:
            * The countup LED animation is displayed.
            * The arming sound is played.
            * After 18 seconds, the alarm LED animation is displayed and the armed sound is played.
        * After 20 seconds, the sensors start scanning and the camera is initialized.
* If the alarm is armed and any of the sensors are tripped:
    * The alarm is triggered.
    * The camera records for 7 seconds and continues to record 7 second clips whenever the sensors are tripped.
    * The entry routine is started:
        * The countdown LED animation is displayed.
        * The entry sound is played and then played again after 7 and 14 seconds.
        * The alarm LED animation is displayed.
        * The notification sound is played.
        * A notification email is sent.
* If the alarm is armed via the web interface:
    * The sensors immediately start scanning and the camera is initialized.
* If the alarm is disarmed via the web interface:
    * The sensors immediately stop scanning and the camera is turned off.
    * The remaining tasks in the entry routine are canceled.

#### Dependencies:
* sqlite3
    * Contains NFC IDs and user info for web interface login.
    * NFC IDs and user passwords are hashed and salted using passlib.
* celery
    * Celery workers execute all tasks in routines, including playing sounds, displaying LED animations and sending emails.
* rabbitmq
    * Message queue for celery.
* libnfc and nfc-eventd
    * Reads NFC cards and sends the NFC ID the alarm system.
* pygame-mixer for python3
    * Plays sound files.

#### Parts:
* Raspberry Pi (I used a model B) with SD card, case and power supply
* RPi Camera
* PIR sensor (https://www.adafruit.com/products/189)
* Door sensor (https://www.adafruit.com/products/375)
* PN532 NFC/RFID board (https://www.adafruit.com/product/364)
* LED ring (https://www.adafruit.com/products/1586)
* 5v 1A power supply for LED ring
* teensy 3.0 (https://www.pjrc.com/store/teensy3.html)
* micro USB cable to connect RPi to teensy
* small speaker to play sounds from RPi
* USB hub (optional)
* jumper wires and headers

Licensed under GNU GPLv2