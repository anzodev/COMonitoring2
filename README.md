# COMonitoring2

Monitoring system of signal level that uses programmable modules and [Python 3.5+](https://www.python.org/downloads/). Current app has a big bunch of changes than previous [version](https://github.com/anzodev/COMonitoring), so it was the reason to create new repository. Main features:

- system decentralization
- module's connect/disconnect dynamicly
- data integrity checking
- color creation
- chart creation

> The system was tested on Windows 7 and Ubuntu 16.04.

## Hardware

[Pololu Wixel](https://www.pololu.com/docs/0J46/1)  

![Pololu Wixel](https://github.com/anzodev/COMonitoring2/blob/master/pics/wixel.png)


Ubiquiti AirView2 (supported soon)  

![Ubiquiti AirView2](https://github.com/anzodev/COMonitoring2/blob/master/pics/ubiquti.png)


Wi-Detector v3 (supported soon)  

![Wi-Detector v3](https://github.com/anzodev/COMonitoring2/blob/master/pics/wi.png)

## Software

1. Install [Python3.5+](https://www.python.org/downloads/). Some Linux distributions have installed Python3.5 by default, so you can use it to run the app.

2. Be sure that pip is installed. If you are using Linux distribution and default Python interpreter, install pip by (for Ubuntu):

> sudo apt-get install python-pip

2. Install packages:

> pip install pyserial flask-socketio  

On Linux you can get permission error. Use sudo command to install packages.
