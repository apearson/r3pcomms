#!/usr/bin/env bash
# this probably needs the following before it'll work: sudo mount -t debugfs none /sys/kernel/debug
#
# you might then run this like: sudo ./scripts/fetch-rd.sh > ./data/river3plus.rd.hex.txt

VENDOR_ID=3746
PRODUCT_ID=FFFF
cat /sys/kernel/debug/hid/0003\:${VENDOR_ID}\:${PRODUCT_ID}.*/rdesc
