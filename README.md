# r3pcomms
River 3 Plus comms from scratch via USB CDC (ACM)

## Usage
```
$ python -m r3pcomms --help
usage: python -m r3pcomms [-h] [--version] --port PORT [--serial] [--metrics METRICS]

Local communication with River 3 Plus

options:
  -h, --help            show this help message and exit
  --version, -V         show program's version number and exit
  --port PORT, -p PORT  comms port to use, like "COM3" or "/dev/ttyACM0" or "/dev/serial/by-id/usb-EcoFlow_EF-UPS-RIVER_3_Plus_${SERIALNUMBER}-if01"
  --serial, -s          get unit serial number
  --metrics METRICS, -m METRICS
                        number of times to get all metrics
```
### Examples
in Windows using com port:
```
$ python -m r3pcomms --port COM3 --serial
REDACTED
```
in Linux using serial port:
```
$ python -m r3pcomms --port /dev/ttyACM0 --serial
REDACTED
```
```
python -m r3pcomms --port /dev/ttyACM0 --serial --metrics 3
REDACTED
[{'name': 'unknown', 'type': 2, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 3, 'data': '0x00320000', 'value': 1.7936620343357659e-41, 'unit': '?'}, {'name': 'Capacity?/Battery Voltage?', 'type': 4, 'data': '0x14141919', 'value': (5140, 6425), 'unit': '?'}, {'name': 'unknown', 'type': 5, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 6, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Total Load', 'type': 7, 'data': '0x00000080', 'value': -0.0, 'unit': 'W'}, {'name': 'Total Draw', 'type': 8, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw', 'type': 9, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw Frequency?', 'type': 10, 'data': '0x00000000', 'value': (0, 0), 'unit': 'Hz'}, {'name': 'unknown', 'type': 11, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Solar/DC Draw', 'type': 12, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 13, 'data': '0x58020000', 'value': 8.407790785948902e-43, 'unit': '?'}, {'name': 'AC Load', 'type': 14, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'AC Load Frequency?', 'type': 15, 'data': '0x3c000000', 'value': (60, 0), 'unit': 'Hz'}, {'name': 'DC Load', 'type': 16, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-A Load', 'type': 17, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-C Load', 'type': 18, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 19, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 20, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 21, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'serial', 'type': 22, 'data': '0xREDACTED', 'value': 'REDACTED', 'unit': ''}, {'name': 'Time left?', 'type': 23, 'data': '0x33170000', 'value': (98.98333333333333, 0.0), 'unit': 'Hr?'}, {'name': 'unknown', 'type': 24, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 25, 'data': '0x23010002', 'value': 9.404281028860795e-38, 'unit': '?'}, {'name': 'preamble', 'data': '392f01000000014402220101660201010000', 'value': 0, 'unit': ''}]
[{'name': 'unknown', 'type': 2, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 3, 'data': '0x00320000', 'value': 1.7936620343357659e-41, 'unit': '?'}, {'name': 'Capacity?/Battery Voltage?', 'type': 4, 'data': '0x14141919', 'value': (5140, 6425), 'unit': '?'}, {'name': 'unknown', 'type': 5, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 6, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Total Load', 'type': 7, 'data': '0x00000080', 'value': -0.0, 'unit': 'W'}, {'name': 'Total Draw', 'type': 8, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw', 'type': 9, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw Frequency?', 'type': 10, 'data': '0x00000000', 'value': (0, 0), 'unit': 'Hz'}, {'name': 'unknown', 'type': 11, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Solar/DC Draw', 'type': 12, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 13, 'data': '0x58020000', 'value': 8.407790785948902e-43, 'unit': '?'}, {'name': 'AC Load', 'type': 14, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'AC Load Frequency?', 'type': 15, 'data': '0x3c000000', 'value': (60, 0), 'unit': 'Hz'}, {'name': 'DC Load', 'type': 16, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-A Load', 'type': 17, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-C Load', 'type': 18, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 19, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 20, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 21, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'serial', 'type': 22, 'data': '0xREDACTED', 'value': 'REDACTED', 'unit': ''}, {'name': 'Time left?', 'type': 23, 'data': '0x33170000', 'value': (98.98333333333333, 0.0), 'unit': 'Hr?'}, {'name': 'unknown', 'type': 24, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 25, 'data': '0x23010002', 'value': 9.404281028860795e-38, 'unit': '?'}, {'name': 'preamble', 'data': '392f02000000014402220101660201010000', 'value': 0, 'unit': ''}]
[{'name': 'unknown', 'type': 2, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 3, 'data': '0x00320000', 'value': 1.7936620343357659e-41, 'unit': '?'}, {'name': 'Capacity?/Battery Voltage?', 'type': 4, 'data': '0x14141919', 'value': (5140, 6425), 'unit': '?'}, {'name': 'unknown', 'type': 5, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 6, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Total Load', 'type': 7, 'data': '0x00000080', 'value': -0.0, 'unit': 'W'}, {'name': 'Total Draw', 'type': 8, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw', 'type': 9, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw Frequency?', 'type': 10, 'data': '0x00000000', 'value': (0, 0), 'unit': 'Hz'}, {'name': 'unknown', 'type': 11, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Solar/DC Draw', 'type': 12, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 13, 'data': '0x58020000', 'value': 8.407790785948902e-43, 'unit': '?'}, {'name': 'AC Load', 'type': 14, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'AC Load Frequency?', 'type': 15, 'data': '0x3c000000', 'value': (60, 0), 'unit': 'Hz'}, {'name': 'DC Load', 'type': 16, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-A Load', 'type': 17, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-C Load', 'type': 18, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 19, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 20, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 21, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'serial', 'type': 22, 'data': '0xREDACTED', 'value': 'REDACTED', 'unit': ''}, {'name': 'Time left?', 'type': 23, 'data': '0x33170000', 'value': (98.98333333333333, 0.0), 'unit': 'Hr?'}, {'name': 'unknown', 'type': 24, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 25, 'data': '0x23010002', 'value': 9.404281028860795e-38, 'unit': '?'}, {'name': 'preamble', 'data': '392f03000000014402220101660201010000', 'value': 0, 'unit': ''}]
```
## Installation
### From the Arch User Repository via paru
```
$ paru -Syu python-r3pcomms-git
```
