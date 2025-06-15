#!/usr/bin/env python3
import os
import struct
import sys
import random
import string

use_stdin = True

if use_stdin:
    hex_str = sys.stdin.read()
else:
    path = "/sys/kernel/debug/hid/0003:3746:FFFF.0017/rdesc"
    with open(path, "r") as f:
        hex_str = f.read().strip()

# split by spaces, convert each hex byte to int, then to bytes
broken_descriptor = bytes(int(b, 16) for b in hex_str.split())

# patch ecoflow's bad report descriptor by adding 3x 0xC0
# end collection indicator bytes to close unbalanced collections
rd = broken_descriptor + bytes.fromhex('c0c0c0')
rd_size = len(rd)

rd_size_max = 4096
if rd_size > rd_size_max:
    raise ValueError("Report descriptor is too big")

characters = string.ascii_uppercase + string.digits
serial_number = ''.join(random.choices(characters, k=16))
print(f"Using device serial number: {serial_number}")
vid=0x3746
pid=0xFFFE
print(f"Setting VID:PID={vid:04X}:{pid:04X}")

# pack UHID_CREATE2 event
event_data = struct.pack(
    f"< L 128s 64s 64s H H I I I I 4096s",
    11,  # UHID_CREATE2 event type
    b"River 3 Plus (fixed)".ljust(128, b"\0"),
    b"uhid/fake0".ljust(64, b"\0"),
    serial_number.encode().ljust(64, b"\0"),  # serial number
    rd_size,  # length of report descriptor
    0x0003,  # BUS_USB
    vid,  # vendor ID
    pid,  # product ID
    0x00000100,  # version
    0x00000000,  # country
    rd.ljust(4096, b"\0"),  # report descriptor
)

# write to /dev/uhid and keep alive
with open("/dev/uhid", "wb+", buffering=0) as uhid:
    uhid.write(event_data)
    print("Device Created!")
    try:
        while True:
            data = uhid.read(4096)
    except KeyboardInterrupt:
        uhid.write(struct.pack("L",1))
        print("Device destroyed!")
