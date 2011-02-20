#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os 
import shlex, subprocess 
import res_rc
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class InfoViewer(QDialog):
  local_lbl={}
  remote_lbl={}
  routes_lbl={}
  dns_lbl={}
  if_name_lbl={}
  vpn_log=""
  if_name=""
  
  def __init__(self):
    QDialog.__init__(self)
    self.setupGUI()
      
  def setupGUI(self):
    #self.resize(200, 500)
    self.setWindowTitle('Info Viewer')
    
    self.init_labels();
    
    ip_grp = QGroupBox("IP Settings")
    ip_layout = QGridLayout();
    local_txt=QLabel("Local:")
    ip_layout.addWidget(local_txt,0,0)
    ip_layout.addWidget(self.local_lbl,0,1)
    remote_txt=QLabel("Remote:")
    ip_layout.addWidget(remote_txt,1,0)
    ip_layout.addWidget(self.remote_lbl,1,1)
    ip_grp.setLayout(ip_layout)
    
    
    routes_grp = QGroupBox("Routes from VPN")
    routes_layout = QGridLayout();
    routes_layout.addWidget(self.routes_lbl)
    routes_grp.setLayout(routes_layout)
    
    dns_grp = QGroupBox("DNS Servers")
    dns_layout = QGridLayout();
    dns_layout.addWidget(self.dns_lbl)
    dns_grp.setLayout(dns_layout)
    
    self.layout=QVBoxLayout(self)
    self.layout.addWidget(self.if_name_lbl)
    self.layout.addWidget(ip_grp)
    self.layout.addWidget(routes_grp)
    self.layout.addWidget(dns_grp)
    
  def init_labels(self):
    self.local_lbl=QLabel("")
    self.remote_lbl=QLabel("")
    self.routes_lbl=QLabel("")
    self.dns_lbl=QLabel("")
    self.if_name_lbl=QLabel("Interface: ")
    
  def reset_labels(self):
    self.local_lbl.setText("")
    self.remote_lbl.setText("")
    self.routes_lbl.setText("")
    self.dns_lbl.setText("")
    self.if_name_lbl.setText("Interface: DOWN")
    
      
    
  def getInfo(self):
    self.if_name = ""
    output=""
    try:
      #cmd="cat "+self.vpn_log+" | grep tap | sed 's/.*\(tap[0-9]*\).*/\1/g' | head -n1"
      p1=subprocess.Popen(["cat",self.vpn_log], stdout=subprocess.PIPE)
      p2=subprocess.Popen(["grep","tap"],stdin=p1.stdout, stdout=subprocess.PIPE)
      p3=subprocess.Popen(["sed","s/.*\(tap[0-9]*\).*/\\1/g"],stdin=p2.stdout, stdout=subprocess.PIPE)
      p4=subprocess.Popen(["head","-n1"],stdin=p3.stdout, stdout=subprocess.PIPE)
      p1.stdout.close()
      p2.stdout.close()
      p3.stdout.close()
      output = p4.communicate()[0]
      p1.wait();
    except:
      self.reset_labels()
      self.getInfo()
      return
      
   
    if (p1.returncode != 0):
      qDebug("Code:"+str(p1.returncode))
      self.reset_labels()
      return
          
    # Update Interface name
    self.if_name = output.replace("\n","")
    self.if_name_lbl.setText("Interface: "+self.if_name)
    
    #  ifconfig tap0  | awk -F'[ :]*' '/inet addr/{print $4}'
    p1=subprocess.Popen(["ifconfig",self.if_name], stdout=subprocess.PIPE)
    p2=subprocess.Popen(["awk","-F","[ :]*","/inet addr/{print $4}"],stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    
    self.local_lbl.setText(output)
    
    
    # route -n |  awk -F'[ ]*' '/tap0/{print $1"/"$3}'
    p1=subprocess.Popen(["route","-n"], stdout=subprocess.PIPE)
    p2=subprocess.Popen(["awk","-F","[ ]*","/"+self.if_name+"/{print $1\"/\"$3}"],stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    
    self.routes_lbl.setText(output)
    
    
    # cat /etc/resolv.conf | grep -v '#'
    p1=subprocess.Popen(["cat","/etc/resolv.conf"], stdout=subprocess.PIPE)
    p2=subprocess.Popen(["grep","-v","#"],stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    
    self.dns_lbl.setText(output)
    
    
  def setLog(self,vpn_log):
    if (vpn_log==self.vpn_log):
      return
    self.vpn_log = vpn_log
    self.getInfo()
    

class LogViewer(QDialog):
  log=""
  txtview = {}
  logTimer = {}
  logfile = {}
  opened=False
  
  def __init__(self): 
        QDialog.__init__(self)
	self.setupGUI()
	
  def setupGUI(self):
	self.resize(1000, 500)
        self.setWindowTitle('OpenVPN Manager - Log Viewer')
        self.txtview = QTextEdit(self)
        self.txtview.setReadOnly(True)
        self.txtview.setLineWrapMode(QTextEdit.NoWrap)
        
        self.layout=QHBoxLayout(self)
        self.layout.addWidget(self.txtview)
        
        self.logTimer = QTimer(self)
	self.connect(self.logTimer, SIGNAL('timeout()'), self.updateText)
	
        
  def setLog(self, fname):
	if (fname==self.log):
	  return
	if (self.opened == True):
	  self.logfile.close()
	  
	self.log = fname
	self.logfile = QFile(self.log);
	
	if (self.logfile.open(QIODevice.ReadOnly) == False):
	  qDebug("Unable to load file")
	  self.opened=False
	  return
	  
	self.opened=True

	
  def show(self):
    QDialog.show(self)
    self.updateText()
    self.logTimer.start(500)
    
  def done(self, code):
    self.logTimer.stop()
    QDialog.done(self, code)
    
  def updateText(self):
    scroll = False
    sb = self.txtview.verticalScrollBar()
    hsb = self.txtview.horizontalScrollBar()
    hsv = hsb.value()
    sv = sb.value()
    if (sb.value() == sb.maximum()):
      scroll = True
      
    
    if (self.logfile.error() != 0):
     qDebug("Unable to load file")
     self.txtview.setText("Unable to load file, error:" + self.logfile.errorString())
     # Try again
     if (self.logfile.open(QIODevice.ReadOnly) == True):
       self.opened = True;
     return 
    
    newtext = ""
    while (self.logfile.atEnd() == False):
      line=self.logfile.readLine()
      if (line != ""):
	newtext += line
	
    if (newtext != ""):
      if ((len(newtext) > 2) & (newtext[len(newtext)-1] == '\n') ):
	newtext = newtext[0:len(newtext)-2]
	
      self.txtview.append(newtext.__str__())
      
    
    if (scroll == True):
      sb.setValue(sb.maximum())
    else:
      sb.setValue(sv)
      
    hsb.setValue(hsv)
	

class VPNManager(QMainWindow):
    root_dir = os.getenv("HOME") + "/.vpn_manager"
    sudo_cmd=" gksu "
    editor=" gedit "
    vpns = {}
    toggleBut = {}
    logBut = {}
    delBut = {}
    nfoBut = {}
    editBut = {}
    listTimer = {}
    logView = {}
    nfoView = {}
    
    
    
    def __init__(self): 
        QMainWindow.__init__(self)
	self.setupGUI()
	self.initVPNs()
	self.disableActions()
	self.setWindowIcon(QIcon(':/images/applications-internet.png'))
        
        
    def setupGUI(self):
        self.setWindowTitle('OpenVPN Manager')

	self.vpns = QTableWidget()
        headers = QStringList()
        headers << "Configuration" << "Status" 
	self.vpns.setColumnCount(2)
	self.vpns.setSelectionBehavior(QTableView.SelectRows)
	self.vpns.setSelectionMode(QTableView.SingleSelection)
	self.vpns.setAlternatingRowColors(True)
        self.vpns.setHorizontalHeaderLabels(headers)
        self.vpns.horizontalHeader().setResizeMode( 0, QHeaderView.Stretch );
       

        
        self.connect(self.vpns, SIGNAL('itemSelectionChanged()'), self.vpnChanged)
        
        # Main Frame
        mainFrame = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(self.vpns)
        mainFrame.setLayout(layout)
        self.setCentralWidget(mainFrame)
        
        # Actions
        actLayout = QHBoxLayout()
        actLayout2 = QHBoxLayout()
        
        self.toggleBut = QPushButton(QIcon(":/images/adept_update.png"), "Toggle")
        actLayout.addWidget(self.toggleBut)
        self.connect(self.toggleBut, SIGNAL('clicked()'), self.doToggle)
        
        self.logBut = QPushButton(QIcon(":/images/find.png"),"View Log")
        actLayout.addWidget(self.logBut)
        self.connect(self.logBut, SIGNAL('clicked()'), self.doViewLog)
        
        self.delBut = QPushButton(QIcon(":/images/button_cancel.png"),"Delete VPN")
        actLayout.addWidget(self.delBut)
        self.connect(self.delBut, SIGNAL('clicked()'), self.doDelete)
        
        self.editBut = QPushButton(QIcon(":/images/edit.png"),"Edit Config")
        actLayout2.addWidget(self.editBut)
        self.connect(self.editBut, SIGNAL('clicked()'), self.doEdit)
        
        self.nfoBut = QPushButton(QIcon(":/images/info.png"),"View Info")
        actLayout2.addWidget(self.nfoBut)
        self.connect(self.nfoBut, SIGNAL('clicked()'), self.doViewInfo)

        layout.addLayout(actLayout)
        layout.addLayout(actLayout2)
        
        

        exit = QAction(QIcon(':/images/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, SIGNAL('triggered()'), SLOT('close()'))
        
        newConfig = QAction(QIcon(':/images/filenew.png'), 'Import', self)
        newConfig.setShortcut('Ctrl+I')
        newConfig.setStatusTip('Import Config')
        self.connect(newConfig, SIGNAL('triggered()'), self.doImport)

        self.statusBar()

        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(newConfig)
        file.addSeparator()
        file.addAction(exit)
        
        listTimer = QTimer(self)
	self.connect(listTimer, SIGNAL('timeout()'), self.updateList)
	listTimer.start(3000)
	
	self.logView = LogViewer()
	self.nfoView = InfoViewer()
	self.resize(200, 200)
        
    def vpnChanged(self):
      self.enableActions()
      # Update Open Dialogs
      vpn_name =self.getVPN_name()
      if (vpn_name == ""):
	return
      path = self.root_dir+"/"+vpn_name+"/"+vpn_name+".log"
      self.logView.setLog(path)
      self.nfoView.setLog(path)
      
    def initVPNs(self, selected=""):
	self.vpns.setAlternatingRowColors(True)
	it=QDirIterator(self.root_dir)
	count = 0;
	while (it.hasNext()):
	  
	    entry = it.next()
	    fi = QFileInfo(entry)

	    if ((fi.baseName() != "" ) & (str(fi.baseName()) != "base")):
		
		tableit = QTableWidgetItem(fi.baseName())
		tableit.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
		self.vpns.insertRow(count);
		self.vpns.setItem(count,0,tableit)
		
		# Status
		status = QFileInfo( "/var/run/openvpn."+fi.baseName()+".pid")
		stat_it = QTableWidgetItem("UP")
		stat_it.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )
		font = QFont()
		brush = QBrush()
		font.setBold(1)
		stat_it.setFont(font)
		
		if (status.exists()):
		  #qDebug("Adding "+ fi.baseName() + " UP")
		  brush.setColor(Qt.green)
		  stat_it.setForeground(brush)
		  self.vpns.setItem(count,1,stat_it)
		else:
		  #qDebug("Adding "+ fi.baseName() + " DOWN")
		  stat_it.setText("DOWN")
		  brush.setColor(Qt.red)
		  stat_it.setForeground(brush)
		  self.vpns.setItem(count,1,stat_it)
		  
		# Fix Selected
		if (fi.baseName() == selected):
		  self.vpns.setRangeSelected(QTableWidgetSelectionRange(count,0,count,1), True)
		  
		self.vpns.setRowHeight(count,18);
		  
		count+=1
		
	# End Of While

		
    def getVPN_name(self):
      vpn_name=""
      if (len(self.vpns.selectedIndexes()) != 0 ):
	row = self.vpns.selectedIndexes().pop().row()
	vpn_name = self.vpns.item(row,0).text()
	
      return vpn_name
		
    def updateList(self):
	name=self.getVPN_name()
	self.clearVPNs()
	self.initVPNs(name)
	
		
    def clearVPNs(self):
	self.vpns.clearContents()
	self.vpns.setRowCount(0)
		
    def disableActions(self):
	  self.toggleBut.setEnabled(0)
	  self.logBut.setEnabled(0)
	  self.delBut.setEnabled(0)
	  self.editBut.setEnabled(0)
	  self.nfoBut.setEnabled(0)
	  
    def enableActions(self):
      self.toggleBut.setEnabled(1)
      self.logBut.setEnabled(1)
      self.delBut.setEnabled(1)
      self.editBut.setEnabled(1)
      self.nfoBut.setEnabled(1)
      
    def doToggle(self):
      vpn_name =self.getVPN_name()
      cmd = self.sudo_cmd+ self.root_dir+"/"+vpn_name+"/"+vpn_name+".sh toggle"
      qDebug(cmd)
      os.system(str(cmd))
      
    def doEdit(self):
      vpn_name =self.getVPN_name()
      cmd = self.editor+ self.root_dir+"/"+vpn_name+"/"+vpn_name+".conf&"
      qDebug(cmd)
      os.system(str(cmd))
      
    def doViewLog(self):
      vpn_name =self.getVPN_name()
      path = self.root_dir+"/"+vpn_name+"/"+vpn_name+".log"
      self.logView.setLog(path)
      self.logView.show()
      
    def doViewInfo(self):
      vpn_name =self.getVPN_name()
      self.nfoView.setLog( self.root_dir+"/"+vpn_name+"/"+vpn_name+".log")
      self.nfoView.show()
      
    def doDelete(self):
      vpn_name = self.getVPN_name()
      msgBox = QMessageBox()
      msgBox.setText("Are you SURE you want to delete it??");
      msgBox.setInformativeText("No way back... ");
      msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel);
      msgBox.setDefaultButton(QMessageBox.Cancel);
      ret = msgBox.exec_();
      if (ret == QMessageBox.Ok):
	self.deleteVpn(vpn_name)
      
      
    def deleteVpn(self, vpn_name):
      os.system(str("rm -r "+self.root_dir+"/"+vpn_name))
      self.updateList()
      self.disableActions()

    def getPassFile(self, conf):
      pass_file=""
      p=subprocess.Popen(["awk","-F"," *","/auth-user-pass/{print $1} ",conf], stdout=subprocess.PIPE)
      pass_file=p.communicate()[0]
      
      if (pass_file!=""):
	return True
	
      return False
      
      
    def doImport(self):
      fileName = ""
      fileName = QFileDialog.getOpenFileName(self,
	"Import Configuration", os.getenv("HOME"));
      if (fileName == ""):
	return
      finfo = QFileInfo(fileName)
      directory = finfo.absolutePath()
      basename = finfo.baseName()
      
      instDir = QDir(self.root_dir+"/"+basename)
      if (instDir.exists() == 1):
	QErrorMessage.showMessage (
	  QErrorMessage.qtHandler(), 
	  "Configuration already exists"
	 )
      
      configFile = QFile(fileName)
      keysDir = QDir(directory+"/keys")
      if (keysDir.exists() == 0):
	QErrorMessage.showMessage (
	  QErrorMessage.qtHandler(), 
	  "There is no keys folder next to the config file... \nThere should be "+directory+"/keys folder.")
	return
	
      # Create directories
      instDir = QDir(self.root_dir)
      instDir.mkdir(basename)
      instDir = QDir(self.root_dir+"/"+basename)
      instDir.mkdir("keys")
      
      # Copy
      os.system(str("cp "+fileName+" "+self.root_dir+"/"+basename))
      os.system(str("cp -r "+directory+"/keys/* "+self.root_dir+"/"+basename+"/keys"))
      os.system(str("cp "+self.root_dir+"/base/init.sh"+" "+self.root_dir+"/"+basename+"/"+basename+".sh"))
      os.system(str("cp "+self.root_dir+"/base/linux_updown.sh"+" "+self.root_dir+"/"+basename))
      
      # Check for password in the configuration
      if (self.getPassFile(fileName)):
	self.setConfigPass(basename)
	
      
      self.updateList()
     
    def setConfigPass(self, basename):
      username=QInputDialog.getText ( self, "Enter Info", "Your VPN username", QLineEdit.Normal, "")
      password=QInputDialog.getText ( self, "Enter Info", "Your VPN password", QLineEdit.Password, "")
      
      if (username[1] == False | password[1] == False ):
	self.deleteVpn(basename)
	return

      passfile=QFile(self.root_dir+"/"+basename+"/"+basename+".pswd")
      if (passfile.open(QIODevice.WriteOnly) == False):
	self.deleteVpn(basename)
	return
	
      passfile.write(str(username[0]+"\n"+password[0]))
      passfile.close()
      QFile.setPermissions(self.root_dir+"/"+basename+"/"+basename+".pswd", QFile.WriteOwner|QFile.ReadOwner)
      
      # Fix Config
      os.system(str("cat "+self.root_dir+"/"+basename+"/"+basename+".conf | sed 's/auth-user-pass/auth-user-pass "+basename+".pswd/g' > "+
      self.root_dir+"/"+basename+"/tmp"))
      os.system(str("mv "+self.root_dir+"/"+basename+"/tmp "+self.root_dir+"/"+basename+"/"+basename+".conf"))
      
      
# MAIN
app = QApplication(sys.argv)
mainwin = VPNManager()
mainwin.show()
sys.exit(app.exec_())