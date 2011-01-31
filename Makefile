all: install

install:
	-mkdir ~/.vpn_manager
	-mkdir ~/.vpn_manager/base
	-cp ./base/* ~/.vpn_manager/base

