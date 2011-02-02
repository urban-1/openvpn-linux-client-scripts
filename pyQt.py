#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os 
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class LogViewer(QDialog):
  log=""
  txtview = {}
  logTimer = {}
  
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
	self.log = fname
	
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
      
    self.txtview.setText("")
    logfile = QFile(self.log);
    if (logfile.open(QIODevice.ReadOnly) == False):
     qDebug("Unable to load file")
     return 
    
    stream = QTextStream ( logfile );
    text = stream.readAll()
    logfile.close()
    
    self.txtview.setText(text)
    
    if (scroll == True):
      sb.setValue(sb.maximum())
    else:
      sb.setValue(sv)
      
    hsb.setValue(hsv)
	

class VPNManager(QMainWindow):
    root_dir = os.getenv("HOME") + "/.vpn_manager"
    vpns = {}
    toggleBut = {}
    logBut = {}
    delBut = {}
    listTimer = {}
    logView = {}
    
    def __init__(self): 
        QMainWindow.__init__(self)
	self.setupGUI()
	self.initVPNs()
	self.disableActions()
        
        
    def setupGUI(self):
	self.resize(350, 250)
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
       

        
        self.connect(self.vpns, SIGNAL('itemSelectionChanged()'), self.enableActions)
        
        # Main Frame
        mainFrame = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(self.vpns)
        mainFrame.setLayout(layout)
        self.setCentralWidget(mainFrame)
        
        # Actions
        actFrame = QFrame()
        actLayout = QHBoxLayout()
        actFrame.setLayout(actLayout)
        
        self.toggleBut = QPushButton("Toggle")
        actLayout.addWidget(self.toggleBut)
        self.connect(self.toggleBut, SIGNAL('clicked()'), self.doToggle)
        
        self.logBut = QPushButton("View Log")
        actLayout.addWidget(self.logBut)
        self.connect(self.logBut, SIGNAL('clicked()'), self.doViewLog)
        
        self.delBut = QPushButton("Delete VPN")
        actLayout.addWidget(self.delBut)
        self.connect(self.delBut, SIGNAL('clicked()'), self.doDelete)

        layout.addWidget(actFrame)
        
        

        exit = QAction(QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, SIGNAL('triggered()'), SLOT('close()'))
        
        newConfig = QAction(QIcon('icons/new.png'), 'New', self)
        newConfig.setShortcut('Ctrl+N')
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
	  
    def enableActions(self):
      self.toggleBut.setEnabled(1)
      self.logBut.setEnabled(1)
      self.delBut.setEnabled(1)
      
    def doToggle(self):
      vpn_name =self.getVPN_name()
      cmd = " kdesudo "+ self.root_dir+"/"+vpn_name+"/"+vpn_name+".sh toggle"
      qDebug(cmd)
      os.system(str(cmd))
      
    def doViewLog(self):
      vpn_name =self.getVPN_name()
      path = self.root_dir+"/"+vpn_name+"/"+vpn_name+".log"
      qDebug("Opening Log: "+path)
      self.logView.setLog(path)
      self.logView.show()
      
    def doDelete(self):
      vpn_name = self.getVPN_name()
      msgBox = QMessageBox()
      msgBox.setText("Are you SURE you want to delete it??");
      msgBox.setInformativeText("No way back... ");
      msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel);
      msgBox.setDefaultButton(QMessageBox.Cancel);
      ret = msgBox.exec_();
      if (ret == QMessageBox.Ok):
	os.system(str("rm -r "+self.root_dir+"/"+vpn_name))
	self.updateList()
	
      
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
      
      self.updateList()
     


# MAIN
app = QApplication(sys.argv)
mainwin = VPNManager()
mainwin.show()
sys.exit(app.exec_())