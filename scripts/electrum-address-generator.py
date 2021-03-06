#!/usr/bin/env python
'''
This script is based on https://github.com/spesmilo/electrum/blob/master/scripts/merchant.py (authored by homasv@gitorious) thus license: GPL (v3 or later), see <http://www.gnu.org/licenses/>

Requirements:

sudo apt-get install python-twisted
sudo apt-get install python-setuptools
sudo easy_install txJSON-RPC
sudo apt-get install python-pip
sudo pip install http://download.electrum.org/download/Electrum-1.6.2.tar.gz#md5=4e40d5c6c13e7e7d09b559cc6f4eb982

'''




def handle_help():
    print "\nElectrum address generator serves up deterministic bitcoin addresses by their indices.\n"
    print "  Config file: electrum-address-generator.conf\n"
    print "  Usage: python electrum-address-generator.py <options>\n"
    print "  Options:"
    print "       -daemon                 starts rpc daemon that responds to request 'getaddress' with integer argument 'index'"
    print "       getaddress <index>      outputs deterministic bitcoin address by index\n\n"

from twisted.web import server
from twisted.internet import reactor
from txjsonrpc.web import jsonrpc
from electrum import Wallet, SimpleConfig
from electrum.util import set_verbosity

import ConfigParser
config = ConfigParser.ConfigParser()
config.read("electrum-address-generator.conf")
rpc_port = int(config.get('daemon','port'))
set_verbosity(0)
wallet_config = SimpleConfig()
wallet_config.set_key('master_public_key', config.get('electrum','master_public_key'))
wallet = Wallet(wallet_config)
wallet.synchronize = lambda: None # prevent address creation by the wallet

class Json_Rpc_Server(jsonrpc.JSONRPC):
    def jsonrpc_getaddress(self, index):
        return handle_getaddress(int(index))

class Json_Rpc_Daemon():
    def __init__(self):
        reactor.listenTCP(rpc_port, server.Site(Json_Rpc_Server()))
        print "Electrum address generator daemon started at port "+str(rpc_port)+" and ready to serve RPC requests:\n     getaddress <index>"
        reactor.run()

def handle_getaddress(index):
    return wallet.get_new_address(0, 0, index)

if __name__ == "__main__":
    try:
      import sys
      cmd = sys.argv[1]
      if (cmd=="-daemon"):
          rpc_server = Json_Rpc_Daemon()
      elif (cmd=="getaddress") and (len(sys.argv)==3):
          print handle_getaddress(int(sys.argv[2]))
      else:
          handle_help()
    except Exception, e:
      print "Couldn't do it: %s" % e
      handle_help()