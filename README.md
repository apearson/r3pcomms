# r3pcomms
River 3 Plus comms from scratch via USB CDC (ACM)

## Usage
```
$ python3 -m r3pcomms --port /dev/ttyACM0 --serial --metrics --help
usage: python -m r3pcomms [-h] [--version] --port PORT [--serial] [--metrics]

Local communication with River 3 Plus

options:
  -h, --help            show this help message and exit
  --version, -V         show program's version number and exit
  --port PORT, -p PORT  comms port to use, like "COM3" or "/dev/ttyACM0" or "/dev/serial/by-id/usb-EcoFlow_EF-UPS-RIVER_3_Plus_${SERIALNUMBER}-if01"
  --serial, -s          get unit serial number
  --metrics, -m         get all metrics
```
### Examples
```
$ python3 -m r3pcomms --port COM3 --serial
REDACTED
```
```
$ python3 -m r3pcomms --port /dev/ttyACM0 --serial
REDACTED
```
```
$ python3 -m r3pcomms --port /dev/ttyACM0 --metrics
```
## Installation
### From the Arch User Repository via paru
```
$ paru -Syu python-r3pcomms-git
```
