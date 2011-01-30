#!/bin/bash

conf=`ls *[0-9].conf | sed 's/\.conf//g'`;

iface=$2;
#
# Operation:
#  0: Going UP
#  1: Going DOWN
#
op=`ifconfig $iface 2>&1`
op=`echo "$op"| grep "not found" | wc -l`;



#
# Routes:
#  0: Do nothing (both routes)
#  1: Redirect Gateway
#  2: Do not install default
#
red_route=$1

remote=`cat ./$conf.conf | grep remote | grep -v ";" | grep -v "#" | grep -v persist | cut -d' ' -f2`;

echo -e "\nFixing routes for interface: $iface, operation: $op"

function start(){

  next_hop=`route -n | grep -v $iface |   awk -F' +'   '$1 ~ /0.0.0.0/{ print $2;}'`
  orig_dev=`route -n | grep -v $iface |   awk -F' +'   '$1 ~ /0.0.0.0/{ print $8;}'`


  echo "Next Hop for $remote is: $next_hop from $orig_dev ... setting up routes"
 
  echo "Deleting old route to $remote"
  route del -host $remote 2> /dev/null

  if [ "$orig_dev" == "ppp0" ]; then
	  echo "P-t-P mode"
	  echo "route add -host $remote dev $orig_dev"
	  route add -host $remote dev $orig_dev
  else 
	  echo "Multi Access Medium mode"
	  echo "route add -host $remote gw $next_hop "
	  route add -host $remote gw $next_hop dev $orig_dev
  fi

  echo "Saving the resovl.conf"
  cp /etc/resolv.conf /tmp/ovpn_resolv_${conf};
  
  # Fix routing
  if [ $2 -eq 1 ];then
    route del default
    dhclient $1&
  elif [ $2 -eq 2 ];then
   (dhclient $1 &&  route del default dev $1)&
  fi

  #
  # ... if MTU is 1500 file transfers crash, anything big collapses????!
  # HAVENT BEEN TESTED ON TCP!!!!
  #ifconfig $1 mtu 1200
}

function getRemoteIP(){
  remote=$1
  ip=`echo "$remote" | egrep '^([1-9]{1,3}\.){3}[1-9]{1,3}$'`
  if [ "$ip" == "" ]; then
    ip=`host $remote | sed 's/.*has address \(.*\)/\1/g'`
  fi
  echo $ip
}

function stop(){
  echo "Stoping interface $1"
  dhcp_pid=`ps -ef | grep dhclient | grep $1 | awk -F' +' '{print $2}'`
  dhclient -d -r $1
  kill -s KILL $dhcp_pid 2> /dev/null
  
  echo "Fixing resolv.conf"
  cp /tmp/ovpn_resolv_${conf} /etc/resolv.conf
  rm /tmp/ovpn_resolv_${conf}
  
  remote_ip=`getRemoteIP $remote`
  echo "Remote is $remote, IP is $remote_ip"
  next_hop=`route -n | grep -v $iface | grep $remote_ip |  awk -F' +'   '{ print $2;}'`
  orig_dev=`route -n | grep -v $iface | grep $remote_ip |  awk -F' +'   '{ print $8;}'`

  
  echo "Previous GW: $next_hop from $orig_dev"
  
  if [ $2 -eq 0 ] || [ $2 -eq 2 ] ;then
    echo "Nothing to do"
    exit 0
  elif [ $2 -eq 1 ];then
    echo "Fixing default route"
    route add default gw $next_hop dev $orig_dev
  fi
  
  route del -host $remote

  
}


#
# MAIN
#
if [ $op -eq 0 ]; then
  start $iface $red_route
elif [ $op -eq 1 ]; then
  stop $iface $red_route
fi



exit 0 
