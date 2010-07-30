import serial
import time
import urllib
import json
import sys

from keys import maglock_key


def fatal(msg,err):
  print "\n"
  print "[ERROR] " + str(msg)
  print "[ERROR] " + str(err)
  sys.exit(0)

try:
  userURL = urllib.urlopen('http://signup.hackerdojo.com/api/rfid?maglock:key='+maglock_key)
  data = userURL.read()
  userURL.close()
except:
  fatal("Unable to connect to server",sys.exc_info()[0])
try:
  userData = json.loads(data)
except:
  fatal("Unable to parse JSON",sys.exc_info()[0])
if len(userData) < 1:
  fatal("Number of RFID tags too small")

try:
  FILE = open("/tmp/rfid","w")
  FILE.writelines(data)
  FILE.close()
except:
  fatal("Unable to write RFID data",sys.exc_info()[0])
  
