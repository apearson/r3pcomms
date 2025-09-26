#!/usr/bin/env bash
echo -n '$ '
sleep 1
echo 'python3 -m r3pcomms --help'
sleep 2
python3 -m r3pcomms --help
echo -n '$ '
sleep 1
echo 'python3 -m r3pcomms --serial /dev/ttyACM0 --hid --humanize --number 10 --redact-serial'
sleep 3
python3 -m r3pcomms --serial /dev/ttyACM0 --hid --humanize --number 10 --redact-serial
echo -n '$ '
