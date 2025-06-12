#!/usr/bin/env python3

path = "/sys/kernel/debug/hid/0003:3746:FFFF.000A/rdesc"

with open(path, "r") as f:
    hex_str = f.read().strip()

# Split by spaces, convert each hex byte to int, then to bytes
raw_bytes = bytes(int(b, 16) for b in hex_str.split())

from hidtools.hid import ReportDescriptor

try:
    rdesc = ReportDescriptor.from_bytes(raw_bytes)
    print("Parsed HID Report Descriptor successfully!")
    print(rdesc.dump())
except Exception as e:
    print(f"Error parsing report descriptor: {e}")

