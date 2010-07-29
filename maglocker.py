#!/usr/local/bin/python
import sys, os, simplejson
from twisted.python     import log
from twisted.internet   import reactor, serialport
from twisted.web        import client as http, error as http_error
from twisted.protocol   import basic

class RelayProtocol(basic.LineReceiver):
    # Here's an echo implementation to show you read/write
    def lineReceived(self, line):
        self.sendLine(self, line)
        

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    device = "/dev/ttyS0"
    baudrate = 4800
    serialport.SerialPort(RelayProtocol(), device, reactor, baudrate=baudrate)
    reactor.run()