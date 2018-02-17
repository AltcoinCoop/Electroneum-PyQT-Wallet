import requests
from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth
import json,urllib2
from collections import OrderedDict
def getSyncHeight():
    url = "http://localhost:24091/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"getblockcount"}
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers)
    rpcout = json.loads(response.text)
    return rpcout['result']['count']

def getTargetBlock():
        response = urllib2.urlopen("http://ocukminingpool.com:8117/stats")
        response = response.read()
        response = json.loads(response)
        return response['network']['height']

def openWalletRPC(walletname,password):
    url = "http://localhost:8974/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"open_wallet","params":{"filename":str(walletname),"password":str(password)}}
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers,auth=HTTPDigestAuth('monero', "1234"))
    rpcout = json.loads(response.text)
    return rpcout
def stopRPCWallet():
    url = "http://localhost:8974/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"stop_wallet"}
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers,auth=HTTPDigestAuth('monero', "1234"))
    rpcout = json.loads(response.text)
    return rpcout
def getWalletAddress():
    url = "http://localhost:8974/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"getaddress"}
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers,auth=HTTPDigestAuth('monero', "1234"))
    rpcout = json.loads(response.text)
    return rpcout
def getBalance():
    url = "http://localhost:8974/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"getbalance"}
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers,auth=HTTPDigestAuth('monero', "1234"))
    rpcout = json.loads(response.text)
    return rpcout
def newWallet(walletname,password):
    url = "http://localhost:8974/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"create_wallet","params":{"filename":walletname,"password":password,"language":"English"}}
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers,auth=HTTPDigestAuth('monero', 1234))
    rpcout = json.loads(response.text)
    return rpcout
def rescanBalance():
    url = "http://localhost:8974/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"rescan_blockchain"}
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers,auth=HTTPDigestAuth('monero', "1234"))
    rpcout = json.loads(response.text)
    return rpcout
def getTransfers():
    url = "http://localhost:8974/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"get_transfers","params":{"in":True,"out":True,"pool":True,"pending":True}}
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers,auth=HTTPDigestAuth('monero', "1234"))
    rpcout = json.loads(response.text,object_pairs_hook=OrderedDict)
    return rpcout

def transfer(to,amount,payid):
    url = "http://localhost:8974/json_rpc"
    headers = {'content-type': 'application/json'}
    rpc_input = {"jsonrpc":"2.0","id":"0","method":"transfer","params":{"destinations":[{"amount":(int( float(amount) * float(100) ) ),"address":str(to)}],"mixin":1,"get_tx_key": True}}
    if payid != "":
        rpc_input['params']['payment_id'] = str(payid)
    response = requests.post(url,data=json.dumps(rpc_input),headers=headers,auth=HTTPDigestAuth('monero', "1234"))
    rpcout = json.loads(response.text)
    return rpcout
    

