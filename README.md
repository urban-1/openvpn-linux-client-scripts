## Intro

These are two simple scripts... The first is used to start/stop/toggle a specific tunnel as a service (init script). The second one is a script called when the tunnel is established or disconnected (up/down script). The up/down script assumes that the TAP interface will get IP using DHCP and it can handle various network configuration issues. 

## Installation

This will just create the folders needed in the home directory. The scripts can then be copied to any location.
To install do: 

    cd <project folder>
    make install

If images are not shown when you run the python script, then you need to do:

    make build


## Up/Down script

This script is meaningful only if on your setup you have to do DHCP request for the TAP interface... DHCP by default may mess up your /etc/resolv.conf file and/or the routing table by installing a default route through the VPN. Thus the script gives you the following options:

1.  Do nothing (default behaviour):
    This is going to take no action witch means that the result depends on your DHCP setup. If the DHCP server assigns default gateway you will end up with 2 default routes. Also in the case that it assigns DNS servers, your /etc/resolv.conf is going to be up dated.

2.  Redirect Default:
    This option is going to uninstall your current (real) default route from the table once the VPN has been established. Thus your DHCP server must supply a default gateway. This way all you traffic will go out through the VPN.

3.  Do not install default:
    This is the opposite of the previous option. It will do DHCP on the tap interface but it will try to delete the default route (if any) that points to the VPN. Thus the result will be to have a LAN route to the VPN + any pushed routes but the internet traffic is passed through your original provider.

## DNS
In any case the script makes a back up of your /etc/resolv.conf file on connection and restores it back when the tunnel gets down. This is needed cause in case you disconnect and you keep the old resolv.conf you are out of DNS and usually you need to redo a DHCP request on the real interface.

# Installation Rules
A sample configuration has been provided. Now if you have a look at the configuration name you will see that is the same as the init script name. This should always be the case. The init script parses it's basename to decide witch configuration to use when invoking openvpn. Thus this means that you can use the same script for any configuration/tunnel by renaming the .sh file to match the OpenVPN configuration name.

## PyQt Script
A make install should do the job... this IS THE UGLIEST VPN MANAGER I have ever seen :-) but it does the job. Supports Import/Delete configurations (which should be already written) and is able to toggle the state of each installed VPN. Multiple tunnels may co-exist. It is fast written and is my first useful python script... so it may be a bit buggy (Calls many times os.system which is not so good either).

Some basic rules:

* It will create the directory `~/.vpn_manager`. All the configs go there on import
* On import/new it is expected that in the same directory with the selected configuration there is a folder named "keys"
* `kdesudo` is used for non-root users, which may or may not exist in your system

# How To Use
Usage is fairly straight forward, into the OpenVPN client configuration you add the following (The options here are the ones described above...):

    #
    # Options:
    #  0: Do nothing (default behaviour)
    #  1: Redirect default route
    #  2: Do not install new default
    #
    up "./linux_updown.sh 1"
    down "./linux_updown.sh 1"


# Conclusion

There may be an easier way of doing the same things but at the time I was looking on it I couldn't find something... A simple VPN manager to support these options and also support multiple VPN tunnels would be really nice (especially if it doesn't look so bad as mine). These scripts though can be used without any GUI... 

That's all, I hope it is useful to somebody... 

Andreas 
