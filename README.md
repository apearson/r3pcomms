# r3pcomms
River 3 Plus comms from scratch via USB CDC (ACM)

## Usage
```
$ python -m r3pcomms --help
usage: python -m r3pcomms [-h] [--version] --port PORT [--debug] [--serial] [--redact-serial] [--metrics METRICS]

Local communication with River 3 Plus

options:
  -h, --help            show this help message and exit
  --version, -V         show program's version number and exit
  --port PORT, -p PORT  comms port to use, like "COM3" or "/dev/ttyACM0" or "/dev/serial/by-id/usb-EcoFlow_EF-UPS-RIVER_3_Plus_${SERIALNUMBER}-if01"
  --debug, -d           print raw comms messages
  --serial, -s          get unit serial number
  --redact-serial, -r   redact serial number from all prints
  --metrics METRICS, -m METRICS
                        number of times to get all metrics
```
### Examples
in Windows using com port:
```
$ python -m r3pcomms --port COM3 --serial --redact-serial
REDACTED
```
in Linux using serial port:
```
$ python -m r3pcomms --port /dev/ttyACM0 --serial --redact-serial
REDACTED
```
with debugging (actual serial number redacted/replaced with 0xff here):
```
$ python -m r3pcomms --port /dev/ttyACM0 --serial --metrics 3 --debug --redact-serial
>>> aa030200f40d00000000ffff22020101660316006293
<<< aa031400dd0f00000000014402220101660301160010ffffffffffffffffffffffffffffffffa1b9
REDACTED
>>> aa030000de2d01000000ffff2202010166027b2c
<<< aa03b800392f0100000001440222010166020000010103010501010101020105013301010501051515181804010501010101070105010101010601050101018109010501010101080105010101010b0105010101010a0105010101010d0105010101010c0105590301010f0105010101010e01053d010101110105010101011001050101010113010501010101120105010101011501050101010114010501010101170111ffffffffffffffffffffffffffffffff160105321601011901050101010118010522000103cd9c
<x< aa03b800392f0100000001440222010166020101000002000400000000030004003200000400041414191905000400000000060004000000000700040000008008000400000000090004000000000a0004000000000b0004000000000c0004000000000d0004580200000e0004000000000f00043c000000100004000000001100040000000012000400000000130004000000001400040000000015000400000000160010ffffffffffffffffffffffffffffffff170004331700001800040000000019000423010002
[{'name': 'unknown', 'type': 2, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Design Capacity', 'type': 3, 'data': '0x00320000', 'value': 12800, 'unit': 'Ah'}, {'name': 'Capacity?/Battery Voltage?', 'type': 4, 'data': '0x14141919', 'value': (5140, 6425), 'unit': '?'}, {'name': 'unknown', 'type': 5, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 6, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Total Load', 'type': 7, 'data': '0x00000080', 'value': -0.0, 'unit': 'W'}, {'name': 'Total Draw', 'type': 8, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw', 'type': 9, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw Frequency?', 'type': 10, 'data': '0x00000000', 'value': (0, 0), 'unit': 'Hz'}, {'name': 'unknown', 'type': 11, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Solar/DC Draw', 'type': 12, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 13, 'data': '0x58020000', 'value': 8.407790785948902e-43, 'unit': '?'}, {'name': 'AC Load', 'type': 14, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'AC Load Frequency?', 'type': 15, 'data': '0x3c000000', 'value': (60, 0), 'unit': 'Hz'}, {'name': 'DC Load', 'type': 16, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-A Load', 'type': 17, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-C Load', 'type': 18, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 19, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 20, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 21, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'serial', 'type': 22, 'data': '0xffffffffffffffffffffffffffffffff', 'value': 'REDACTED', 'unit': ''}, {'name': 'Time left?', 'type': 23, 'data': '0x33170000', 'value': (98.98333333333333, 0.0), 'unit': 'Hr?'}, {'name': 'unknown', 'type': 24, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 25, 'data': '0x23010002', 'value': 9.404281028860795e-38, 'unit': '?'}, {'name': 'preamble', 'data': 'aa03b800392f01000000014402220101660201010000', 'value': 0, 'unit': ''}]
>>> aa030000de2d02000000ffff2202010166027f28
<<< aa03b800392f02000000014402220101660203030202000206020202020102060230020206020616161b1b0702060202020204020602020202050206020202820a0206020202020b02060202020208020602020202090206020202020e0206020202020f02065a0002020c0206020202020d02063e020202120206020202021302060202020210020602020202110206020202021602060202020217020602020202140212ffffffffffffffffffffffffffffffff150206311502021a0206020202021b020621030200749b
<x< aa03b800392f0200000001440222010166020101000002000400000000030004003200000400041414191905000400000000060004000000000700040000008008000400000000090004000000000a0004000000000b0004000000000c0004000000000d0004580200000e0004000000000f00043c000000100004000000001100040000000012000400000000130004000000001400040000000015000400000000160010ffffffffffffffffffffffffffffffff170004331700001800040000000019000423010002
[{'name': 'unknown', 'type': 2, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Design Capacity', 'type': 3, 'data': '0x00320000', 'value': 12800, 'unit': 'Ah'}, {'name': 'Capacity?/Battery Voltage?', 'type': 4, 'data': '0x14141919', 'value': (5140, 6425), 'unit': '?'}, {'name': 'unknown', 'type': 5, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 6, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Total Load', 'type': 7, 'data': '0x00000080', 'value': -0.0, 'unit': 'W'}, {'name': 'Total Draw', 'type': 8, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw', 'type': 9, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw Frequency?', 'type': 10, 'data': '0x00000000', 'value': (0, 0), 'unit': 'Hz'}, {'name': 'unknown', 'type': 11, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Solar/DC Draw', 'type': 12, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 13, 'data': '0x58020000', 'value': 8.407790785948902e-43, 'unit': '?'}, {'name': 'AC Load', 'type': 14, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'AC Load Frequency?', 'type': 15, 'data': '0x3c000000', 'value': (60, 0), 'unit': 'Hz'}, {'name': 'DC Load', 'type': 16, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-A Load', 'type': 17, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-C Load', 'type': 18, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 19, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 20, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 21, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'serial', 'type': 22, 'data': '0xffffffffffffffffffffffffffffffff', 'value': 'REDACTED', 'unit': ''}, {'name': 'Time left?', 'type': 23, 'data': '0x33170000', 'value': (98.98333333333333, 0.0), 'unit': 'Hr?'}, {'name': 'unknown', 'type': 24, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 25, 'data': '0x23010002', 'value': 9.404281028860795e-38, 'unit': '?'}, {'name': 'preamble', 'data': 'aa03b800392f02000000014402220101660201010000', 'value': 0, 'unit': ''}]
>>> aa030000de2d03000000ffff22020101660282eb
<<< aa03b800392f03000000014402220101660202020303010307030303030003070331030307030717171a1a0603070303030305030703030303040307030303830b0307030303030a03070303030309030703030303080307030303030f0307030303030e03075b0103030d0307030303030c03073f030303130307030303031203070303030311030703030303100307030303031703070303030316030703030303150313ffffffffffffffffffffffffffffffff140307301403031b0307030303031a030720020301e259
<x< aa03b800392f0300000001440222010166020101000002000400000000030004003200000400041414191905000400000000060004000000000700040000008008000400000000090004000000000a0004000000000b0004000000000c0004000000000d0004580200000e0004000000000f00043c000000100004000000001100040000000012000400000000130004000000001400040000000015000400000000160010ffffffffffffffffffffffffffffffff170004331700001800040000000019000423010002
[{'name': 'unknown', 'type': 2, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Design Capacity', 'type': 3, 'data': '0x00320000', 'value': 12800, 'unit': 'Ah'}, {'name': 'Capacity?/Battery Voltage?', 'type': 4, 'data': '0x14141919', 'value': (5140, 6425), 'unit': '?'}, {'name': 'unknown', 'type': 5, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 6, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Total Load', 'type': 7, 'data': '0x00000080', 'value': -0.0, 'unit': 'W'}, {'name': 'Total Draw', 'type': 8, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw', 'type': 9, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'AC Draw Frequency?', 'type': 10, 'data': '0x00000000', 'value': (0, 0), 'unit': 'Hz'}, {'name': 'unknown', 'type': 11, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'Solar/DC Draw', 'type': 12, 'data': '0x00000000', 'value': 0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 13, 'data': '0x58020000', 'value': 8.407790785948902e-43, 'unit': '?'}, {'name': 'AC Load', 'type': 14, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'AC Load Frequency?', 'type': 15, 'data': '0x3c000000', 'value': (60, 0), 'unit': 'Hz'}, {'name': 'DC Load', 'type': 16, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-A Load', 'type': 17, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'USB-C Load', 'type': 18, 'data': '0x00000000', 'value': -0.0, 'unit': 'W'}, {'name': 'unknown', 'type': 19, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 20, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 21, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'serial', 'type': 22, 'data': '0xffffffffffffffffffffffffffffffff', 'value': 'REDACTED', 'unit': ''}, {'name': 'Time left?', 'type': 23, 'data': '0x33170000', 'value': (98.98333333333333, 0.0), 'unit': 'Hr?'}, {'name': 'unknown', 'type': 24, 'data': '0x00000000', 'value': 0.0, 'unit': '?'}, {'name': 'unknown', 'type': 25, 'data': '0x23010002', 'value': 9.404281028860795e-38, 'unit': '?'}, {'name': 'preamble', 'data': 'aa03b800392f03000000014402220101660201010000', 'value': 0, 'unit': ''}]
```
## Installation
### From the Arch User Repository via paru
```
$ paru -Syu python-r3pcomms-git
```
