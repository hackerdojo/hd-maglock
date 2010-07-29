import serial
import time
import urllib
import json
import sys

relayfile = serial.Serial('/dev/cuau0', baudrate=9600)
print "\nHacker Dojo RFID Entry System v0.2\n"

def relayOn():
  print '[RELAY] On'
  relayfile.setDTR(True)

def relayOff():
  print '[RELAY] Off'
  relayfile.setDTR(False)

def getUsers():
  try:
    userURL = urllib.urlopen('/tmp/rfid')
    data = userURL.read()
    userURL.close()
  except:
    fatal("Unable to open RFID file",sys.exc_info()[0])
  try:
    userData = json.loads(data)
  except:
    fatal("Unable to parse JSON",sys.exc_info()[0])
  if len(userData) < 1:
    fatal("Number of RFID tags too small")
  return userData

def fatal(msg,err):
  print "\n"
  print "[ERROR] " + str(msg)
  print "[ERROR] " + str(err)
  sys.exit(0)

while True:
  key = raw_input('RFID> ').strip()
  if key in ["exit","exit()","quit","quit()"]:
    print "[EXIT] Exiting"
    sys.exit(0)  
  if key:
    print "[DEBUG] I just scanned " + key
    userData = getUsers()
    print "[DEBUG] Comparing to " + str(len(userData)) + " RFIDs"
    foundUser = None
    for user in userData:
       if key == user['rfid_tag']:
          foundUser = user
    if foundUser:
      print '[FOUND] ' + foundUser['username']
      relayOff()
      time.sleep(3)
      relayOn()
      foundUser = None
    else:
      print '[NOTFOUND] Sorry, RFID key not found'
      
      