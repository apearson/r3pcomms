#!/bin/sh

_forever="${1}"

_shutdown_soc_threshold=10
_forever_check_period=60


do_check () {
  local _soc=$(python -m r3pcomms --hid | jq '.["Charge Level"]["value"]')
  if test "${_soc}" -eq "${_soc}"; then
    if test "${_soc}" -le "${_shutdown_soc_threshold}"; then
      echo "poweroff becuase ${_soc}% <= ${_shutdown_soc_threshold}%" | systemd-cat
      poweroff
      return $?
    else
      return 0
    fi
  else
    echo "WARNING: \"${_soc}\" is not a number"
    return -1
  fi
}

if test "${_forever}" == "forever"; then
  while :; do
    do_check
    sleep "${_forever_check_period}"
  done
else
  do_check
  exit $?
fi
