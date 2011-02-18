all: install

install:
	-mkdir ~/.vpn_manager
	-mkdir ~/.vpn_manager/base
	-cp ./base/* ~/.vpn_manager/base
	-cat ./kde_ovpn_mgr.py | sed 's/kate/gedit/g' | sed 's/kdesudo/gksu/g' > ./gnome_ovpn_mgr.py

