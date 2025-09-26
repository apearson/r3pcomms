#!/usr/bin/env python3
import sys
from hidtools.hid import ReportDescriptor

from_stdin = True

if from_stdin:
    hex_str = sys.stdin.read()
else:
    path = "/sys/kernel/debug/hid/0003:3746:FFFF.000A/rdesc"
    with open(path, "r") as f:
        hex_str = f.read().strip()

# Split by spaces, convert each hex byte to int, then to bytes
rd = bytes(int(b, 16) for b in hex_str.split())
#rd = rd+bytes.fromhex("c0c0c0")

try:
    rdesc = ReportDescriptor.from_bytes(rd)
    print("Parsed HID Report Descriptor successfully!")
    print(rdesc.dump())
except Exception as e:
    print(f"Error parsing report descriptor: {e}")

