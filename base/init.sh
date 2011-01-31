#!/bin/bash
#
# Start n Stop VPN Client...
#

conf=`basename $0 | sed 's/\.sh//g'`
dir=`dirname $0`

case "$1" in
start)
  if [ ! -f /var/run/openvpn.${conf}.pid  ]; then
	openvpn --route-delay 15 --log ${dir}/${conf}.log --writepid /var/run/openvpn.${conf}.pid --cd ${dir} --config ${dir}/${conf}.conf --script-security 2 --daemon;
  else
    echo "Client Tunnel (${conf}) is already started"
  fi
  ;;
stop)
  if [ -f /var/run/openvpn.${conf}.pid  ]; then
        kill `cat /var/run/openvpn.${conf}.pid`;
	rm /var/run/openvpn.${conf}.pid;
  else
    echo "Client Tunnel (${conf}) is already stoped"
  fi

  ;;
toggle)
  if [ ! -f /var/run/openvpn.${conf}.pid  ]; then
       $0 start;
  else
       $0 stop;
  fi
  ;;
restart)
  $0 stop;
  sleep 1
  $0 start;
  ;;
force-stop)
   kill `cat /var/run/openvpn.${conf}.pid` 2> /dev/null
   rm /var/run/openvpn.${conf}.pid 2> /dev/null
  ;;
*)
  echo "Usage: $0 {start|stop|toggle|restart|force-stop}" >&2
  exit 1
  ;;
esac

exit 0
