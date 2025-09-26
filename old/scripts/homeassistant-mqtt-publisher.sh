#!/bin/sh

_number_of_times="${1:-0}"

#export MQTTUI_BROKER="mqtt://192.168.1.1:1883"
#export MQTTUI_USERNAME="homeassistant"
#export MQTTUI_PASSWORD="your hass mqtt password here"

UNIT_SERIAL="$(python -m r3pcomms --serial /dev/ttyACM0 | jq -r '.["Serial Num"]["value"]')"
sleep 1
python -m r3pcomms -n "${_number_of_times}" --hid --serial /dev/ttyACM0 | xargs -d'\n' -L1 mqttui publish "r3pcomms/${UNIT_SERIAL}"
