# -*- coding: cp1252 -*-
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import *
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import QThread
import sys,os,psutil,subprocess,ctypes,datetime,requests,json,atexit,time,daemonrpc,ConfigParser,urllib2,ssl
from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth

global p
global p2
global targetblock
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)
def kill_proc(name):
    for proc in psutil.process_iter(attrs=["name", "exe", "cmdline"]):
        if proc.info['name'] == name:
            proc.kill()
            
kill_proc("electroneumd.exe")
kill_proc("electroneum-wallet-cli.exe")
if os.path.isfile("electroneum-wallet-rpc.8974.login"):
    os.remove("electroneum-wallet-rpc.8974.login")
if not os.path.isdir(os.path.expanduser('Wallets')):
        os.makedirs(os.path.expanduser('Wallets'))
Config = ConfigParser.ConfigParser()
if  not os.path.isfile("walletsettings.ini"):
    cfgfile = open("walletsettings.ini",'w')
    Config.add_section('electroneumd')
    Config.set('electroneumd','datadir','C:\ProgramData\electroneum')
    Config.write(cfgfile)
    cfgfile.close()
else:
    Config.read("walletsettings.ini")
p = subprocess.Popen(['electroneumd.exe','--data-dir',Config.get('electroneumd','datadir')],creationflags = 0x08000000)
p2 = subprocess.Popen(['electroneum-wallet-rpc.exe', '--rpc-bind-port=8974' ,'--wallet-dir=' + "Wallets" ,'--rpc-login=monero:1234'],creationflags = 0x08000000)
time.sleep(1.5)
targetblock = daemonrpc.getTargetBlock()
def appExec(app,p,p2):
    app.exec_()
    daemonrpc.stopRPCWallet()
    p.kill()
    p2.kill()
    os.remove("electroneum-wallet-rpc.8974.login")
    

class syncStatusTimer(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        global syncstatus
        global currentblock,targetblock
        currentblock = daemonrpc.getSyncHeight()
        QApplication.processEvents()
        if (currentblock > targetblock): 
            statustext = "Syncronized: " + str(currentblock) + " Blocks"
        else:
            statustext = "Syncronized: " + str(currentblock) + "/" + str(targetblock)+ " Blocks"
        syncstatus.setText( statustext )
        
class sendTransfer(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        global payto,payid,amount,sendP,serror
        sendP.setEnabled(False)
        result = daemonrpc.transfer( payto.text(), amount.text(), payid.text() )
        try:
            serror.setText("Sent Tx ID:" + str( result['result']['tx_hash'] ) + " Fee: " + str ( float(result['result']['fee']) / 100) )
        except:
            serror.setText("Error: " + str( result['error']['message'] ))
        sendP.setEnabled(True)

class updateWalletData(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        global address
        addr = daemonrpc.getWalletAddress()
   
        address.setText(str(addr['result']['address']))

       
class pingBalance(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        global balance,ubalance,btcbalance,gbpbalance
       
        temp = daemonrpc.getBalance()
        try:
            btcetn = urllib2.urlopen("https://api.coinmarketcap.com/v1/ticker/electroneum/")
            btcetn = btcetn.read()
            btcetn = json.loads(btcetn)
            btcetn = btcetn[0]['price_btc']
            btcetnout = str( float(temp['result']['balance']) / 100 * float(btcetn)) + " BTC"
        except:
            btcetnout = "Unknown"

        try:
            btcgbp = urllib2.urlopen("https://api.coinbase.com/v2/prices/sell?currency=GBP")
            btcgbp = btcgbp.read()
            btcgbp = json.loads(btcgbp)
            btcgbp = btcgbp['data']['amount']
            btcgbpout = u"\xA3" + str( round(float(temp['result']['balance']) / 100 * float(btcetn) * float(btcgbp),2))
        except:
            btcgbpout = "Unknown"
            
        ubalance.setText(  str( float(temp['result']['unlocked_balance']) / 100) + " ETN")
        balance.setText(  str( float(temp['result']['balance']) / 100) + " ETN")
        btcbalance.setText( btcetnout )
        gbpbalance.setText( btcgbpout )
        
class getTransactions(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        global intable,outtable,currentblock
        out = daemonrpc.getTransfers()
        intable.setRowCount(0)
        try:
            for tin in out['result']['in']:
                rowPosition = intable.rowCount()
                intable.insertRow(rowPosition)
                timestamp = (datetime.datetime.fromtimestamp( tin['timestamp'] ) ).strftime('%d-%m-%Y %H:%M:%S')
                
                intable.setItem(rowPosition,0, QTableWidgetItem( str(timestamp ) ) )
                intable.setItem(rowPosition,1, QTableWidgetItem( str( float (tin['amount']) / 100) + " ETN" ) )
                intable.setItem(rowPosition,2, QTableWidgetItem( str( tin['txid'] ) ) )
                intable.setItem(rowPosition,3, QTableWidgetItem( str(  tin['height']) ) )
        except:
            pass
        outtable.setRowCount(0)
        try:
            for tout in out['result']['out']:
                rowPosition = outtable.rowCount()
                outtable.insertRow(rowPosition)
                timestamp = (datetime.datetime.fromtimestamp( tout['timestamp'] ) ).strftime('%d-%m-%Y %H:%M:%S')
                
                outtable.setItem(rowPosition,0, QTableWidgetItem( str(timestamp ) ) )
                outtable.setItem(rowPosition,1, QTableWidgetItem( str( float ( tout['amount'] ) / 100) + " ETN" ) )
                outtable.setItem(rowPosition,2, QTableWidgetItem( str( tout['txid'] ) ) )
                outtable.setItem(rowPosition,3, QTableWidgetItem( str( tout['height']) ) )
        except:
            pass
        intable.sortItems(3,1)
        outtable.sortItems(3,1)
class importWalletFromKeys(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        global newwalletname,newpass1,openwButton
        walletcli = subprocess.Popen(['electroneum-wallet-cli.exe','--generate-from-json','import.json'],creationflags = 0x08000000)
        time.sleep(5)
        walletcli.kill()
        if os.path.isfile("import.json"):
            os.remove("import.json")
        walletname.setText(str(newwalletname.text()))
        password.setText(str(newpass1.text()))
        openwButton()
def main():
    global w,p,p2,syncstatus,walletname,password,address,balance,ubalance,intable,outtable,Qt,currentblock,payto,payid,amount,sendP,serror,btcbalance,gbpbalance,newwalletname,newpass1,openwButton

    app = QApplication(sys.argv)
    w	= QTabWidget()

    # Create tabs
    wallettab	= QWidget()	
    sendtab	= QWidget()
    transintab = QWidget()
    transouttab = QWidget()
    w.resize(800, 500)
    
    # Add tabs
    w.addTab(wallettab,"Wallet")
    w.addTab(sendtab,"Send")
    w.addTab(transintab,"Transactions In")
    w.addTab(transouttab,"Transactions Out")
    
    # Set title and show
    w.setWindowTitle('Electroneum GUI Wallet by Frozennova')
    w.setWindowIcon(QIcon(resource_path(".") + '/etn.ico'))
    syncstatus = QLabel("                                                                                                                                                                 ",w)
    
    syncstatus.width()
    syncstatus.move(10, 480)

    #Create Timers    
    global updateWalletDataThread
    
    updateWalletDataThread = updateWalletData()
    synctimer = QTimer()
    syncStatusThread = syncStatusTimer()
    synctimer.timeout.connect(syncStatusThread.start)
    syncStatusThread.start()
    synctimer.start(3000)
    transactionStatusThread = getTransactions()
    transactionTimer = QTimer()
    transactionTimer.timeout.connect(transactionStatusThread.start)
    importWalletFromKeysThread = importWalletFromKeys()

    global balanceStatusThread,balancetimer,wallettimer,openw,oerror,nerror,importw
    
    balanceStatusThread = pingBalance()
    balancetimer = QTimer()
    balancetimer.timeout.connect(balanceStatusThread.start)

    wallettimer = QTimer()
    updateWalletDataThread = updateWalletData()

    # Open Existing Wallet  
    walletnamel = QLabel("Wallet File:",wallettab)
    walletnamel.move(30, 60)

    waddress = QLabel("Your Address: ",wallettab)
    waddress.move(30, 160)

    address = QLineEdit(wallettab)
    address.setReadOnly(True)
    address.setFrame(False)
    address.resize(700,20)
    address.move(100,156)
    
    
    walletname = QLineEdit(wallettab)
    walletname.move(90, 55)
    walletname.resize(110,20)
    walletname.setText("")

    passwordl = QLabel("Password:",wallettab)
    passwordl.move(30, 90)

    password = QLineEdit(wallettab)
    password.move(90, 85)
    password.resize(110,20)
    password.setText("")
    password.setEchoMode(QLineEdit.Password)
    
    openw = QPushButton('Open Wallet', wallettab)
    openw.move(100,120)

    ubalancel = QLabel("Unlocked Balance",w)
    ubalancel.move(690, 30)

    ubalance = QLineEdit(w)
    ubalance.move(690, 50)
    ubalance.resize(80,20)
    ubalance.setReadOnly(True)
    ubalance.setFrame(True)
    ubalance.setText("00.00")

    balancel = QLabel("Balance",w)
    balancel.move(620, 30)

    balance = QLineEdit(w)
    balance.move(600, 50)
    balance.resize(80,20)
    balance.setReadOnly(True)
    balance.setFrame(True)
    balance.setText("00.00")

    btcbalancel = QLabel("BTC Value",w)
    btcbalancel.move(430, 30)

    btcbalance = QLineEdit(w)
    btcbalance.move(420, 50)
    btcbalance.resize(80,20)
    btcbalance.setReadOnly(True)
    btcbalance.setFrame(True)
    btcbalance.setText("00.00")

    gbpbalancel = QLabel("GBP Value",w)
    gbpbalancel.move(520, 30)

    gbpbalance = QLineEdit(w)
    gbpbalance.move(510, 50)
    gbpbalance.resize(80,20)
    gbpbalance.setReadOnly(True)
    gbpbalance.setFrame(True)
    gbpbalance.setText("00.00")




    oerror = QLabel(wallettab)
    oerror.move(90, 150)
    oerror.setText("                                                                             ")

    # Create New Wallet
    newwalletname = QLineEdit(wallettab)
    newwalletname.move(90, 228)
    newwalletname.resize(110,20)
    newwalletname.setText("")
    newwalletl = QLabel("New Wallet\nName:",wallettab)
    newwalletl.move(30, 225)

    newpass1 = QLineEdit(wallettab)
    newpass1.move(90, 258)
    newpass1.resize(110,20)
    newpass1.setText("")
    newpass1l = QLabel("Password:",wallettab)
    newpass1l.move(30, 260)
    newpass1.setEchoMode(QLineEdit.Password)

    repeatpass1 = QLineEdit(wallettab)
    repeatpass1.move(90, 288)
    repeatpass1.resize(110,20)
    repeatpass1.setText("")
    repeatpass1l = QLabel("Repeat:",wallettab)
    repeatpass1l.move(30, 290)
    repeatpass1.setEchoMode(QLineEdit.Password)

    importw = QPushButton('Create Wallet', wallettab)
    importw.move(100,320)

    nerror = QLabel(wallettab)
    nerror.move(90, 350)
    nerror.setText("                                                                            ")

    #import from keys
    importaddress = QLineEdit(wallettab)
    importaddress.move(270, 228)
    importaddress.resize(110,20)
    importaddress.setText("")
    importaddressl = QLabel("Wallet\nAddress:",wallettab)
    importaddressl.move(210, 225)
    
    spendkey = QLineEdit(wallettab)
    spendkey.move(270, 258)
    spendkey.resize(110,20)
    spendkey.setText("")
    spendkeyl = QLabel("Spend Key:",wallettab)
    spendkeyl.move(210, 260)

    viewkey = QLineEdit(wallettab)
    viewkey.move(270, 288)
    viewkey.resize(110,20)
    viewkey.setText("")
    viewkeyl = QLabel("View Key:",wallettab)
    viewkeyl.move(210, 290)

    importfromkeys = QPushButton('Import From Keys', wallettab)
    importfromkeys.move(280,320)

    
    #Buttons
    @pyqtSlot()
    def importwButton():
        global nerror,importw,walletname,password
        if (repeatpass1.text() == newpass1.text()):
            daemonrpc.newWallet( str(newwalletname.text()),str(newpass1.text()) )
            importw.setEnabled(False)
            nerror.setText("New Wallet Created")
            walletname.setText(str(newwalletname.text()))
            password.setText(str(newpass1.text()))
            openwButton()
                                
        else:
            nerror.setText("Passwords Do not match")
    @pyqtSlot()
    def openwButton():
        global walletname,password,oerror,openw,balanceStatusThread,balancetimer,updateWalletDataThread
        res = daemonrpc.openWalletRPC(walletname.text(),password.text())
        oerror.setText("")
        try:
            res['result']
            updateWalletDataThread.start()
            balanceStatusThread.start()
            transactionStatusThread.start()
            balancetimer.start(150000)
            transactionTimer.start(30000)
        except:
            oerror.setText(res['error']['message'])
    @pyqtSlot()
    def importfromkeysButton():
        global nerror,walletname,password
        if (repeatpass1.text() == newpass1.text()):

            importfile = {}
            importfile['address'] = str(importaddress.text())
            importfile['viewkey'] = str(viewkey.text())
            importfile['spendkey'] = str(spendkey.text())
            importfile['password'] = str(newpass1.text())
            importfile['filename'] = str(newwalletname.text())
            importfile['version'] = int(1)

            F = open("import.json",'w')
            F.write(json.dumps(importfile))
            F.close()
            importWalletFromKeysThread.start()
                                
        else:
            nerror.setText("Passwords Do not match")
    importfromkeys.clicked.connect(importfromkeysButton)
    openw.clicked.connect(openwButton)
    importw.clicked.connect(importwButton)


    #Transactions In table
    intable = QTableWidget(transintab)
    intable.resize(770, 380)
    intable.move(10,60)
    intable.setRowCount(0)
    intable.setColumnCount(4)
    intable.setEditTriggers(QAbstractItemView.NoEditTriggers)
    inheader = intable.horizontalHeader()
    inheader.setResizeMode(0, QHeaderView.ResizeToContents)
    inheader.setResizeMode(1, QHeaderView.ResizeToContents)
    inheader.setResizeMode(2, QHeaderView.Stretch)
    inheader.setResizeMode(3, QHeaderView.ResizeToContents)
    intable.setHorizontalHeaderLabels(("Time;Amount;Transaction ID;Block #").split(";"))
    intable.setSortingEnabled(True)


    #Transactions Out table
    outtable = QTableWidget(transouttab)
    outtable.resize(770, 380)
    outtable.move(10,60)
    outtable.setRowCount(0)
    outtable.setColumnCount(4)
    outtable.setEditTriggers(QAbstractItemView.NoEditTriggers)
    outheader = outtable.horizontalHeader()
    outheader.setResizeMode(0, QHeaderView.ResizeToContents)
    outheader.setResizeMode(1, QHeaderView.ResizeToContents)
    outheader.setResizeMode(2, QHeaderView.Stretch)
    outheader.setResizeMode(3, QHeaderView.ResizeToContents)
    outtable.setHorizontalHeaderLabels(("Time;Amount;Transaction ID;Block #").split(";"))
    outtable.setSortingEnabled(True)

    #Send Tab

    paytol = QLabel("To Address",sendtab)
    paytol.move(20, 70)

    payto = QLineEdit(sendtab)
    payto.resize(550,20)
    payto.move(80,68)
    payto.setText("etnjzKFU6ogESSKRZZbdqraPdcKVxEC17Cm1Xvbyy76PARQMmgrgceH4krAH6xmjKwJ3HtSAKuyFm1BBWYqtchtq9tBap8Qr4M")

    payidl = QLabel("Payment ID",sendtab)
    payidl.move(20, 100)

    payid = QLineEdit(sendtab)
    payid.resize(550,20)
    payid.move(80,98)
    payid.setText("07fc21356e77eb4ad707bdb7fe55f3e466dd511b2796a28574f4e2bd1de21565")
    
    amountl = QLabel("Amount",sendtab)
    amountl.move(20, 130)

    amountetn = QLabel("ETN",sendtab)
    amountetn.move(210, 130)

    amount = QLineEdit(sendtab)
    amount.resize(120,20)
    amount.move(80,128)
    amount.setText("10")

    serror = QLineEdit(sendtab)
    serror.resize(550,20)
    serror.move(80,190)
    serror.setReadOnly(False)
    serror.setFrame(False)

    sendP = QPushButton('Send Payment', sendtab)
    sendP.move(20,160)

    sendTransferThread = sendTransfer()
    @pyqtSlot()
    def sendPButton():
        global walletname,password,oerror,openw,balanceStatusThread,balancetimer,updateWalletDataThread
        sendTransferThread.start()
    sendP.clicked.connect(sendPButton)
    #Show/Exit


    w.show()
    sys.exit(appExec(app,p,p2))
  
 
if __name__ == '__main__':
    main()
