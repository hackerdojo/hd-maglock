#!/usr/local/bin/python
import sys, os, simplejson
from twisted.python     import log
from twisted.internet   import reactor, serialport
from twisted.web        import client as http, error as http_error
from twisted.protocol   import basic

class RelayProtocol(basic.LineReceiver):
    pass

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    device = "/dev/ttyS0"
    baudrate = 4800
    serialport.SerialPort(RelayProtocol(), device, reactor, baudrate=baudrate)
    reactor.run()