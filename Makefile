all: install

RELEASE_FILES= \
	base \
	gnome_ovpn_mgr.py  \
	kde_ovpn_mgr.py  \
	Makefile \
	README \
	res_rc.py \
	CHANGELOG \
	example  \
	images  
	

build:
	pyrcc4 res.qrc -o res_rc.py

install:
	-mkdir ~/.vpn_manager
	-mkdir ~/.vpn_manager/base
	-cp ./base/* ~/.vpn_manager/base
	-cat ./kde_ovpn_mgr.py | sed 's/kate/gedit/g' | sed 's/kdesudo/gksu/g' > ./gnome_ovpn_mgr.py
	 #pyrcc4 res.qrc -o res_rc.py
	 
release:
	tar -czf ./openvpn-linux-client-scripts.tar.gz --exclude='.svn' $(RELEASE_FILES)

