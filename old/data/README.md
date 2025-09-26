fetch raw (possibly screwed up) report descriptor data with something like
```
# sudo mount -t debugfs none /sys/kernel/debug
sudo cat /sys/kernel/debug/hid/0003\:3746\:FFFF.0004/rdesc > river3plus.rd.hex.txt
```
