import serial
import time
import urllib
import json
import sys
import os
import random
import datetime

# This program runs from /etc/rc and takes keyboard input. 

serialport = '/dev/cuau1'
relayfile = None
seconds_to_keep_door_open = 6
spooldir = '/root/unlock_spool'
  
def relayOn():
  print '[RELAYON] The door is now locked'
  if relayfile:
    relayfile.setDTR(True)

def relayOff():
  print '[RELAYOFF] The door is now unlocked'
  if relayfile:
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
  userData.append({"rfid_tag":"0001890155","username":"cleaners"})
  userData.append({"rfid_tag":"0001816397","username":"benchmark.construction"})
  userData.append({"rfid_tag":"0001691797","username":"brian.klug"})
  return userData

def fatal(msg,err):
  print "\n"
  print "[ERROR] " + str(msg)
  print "[ERROR] " + str(err)
  sys.exit(0)

def main():
  global relayfile
  print "\nHacker Dojo RFID Entry System v0.221\n"
  if os.path.exists(serialport):
    relayfile = serial.Serial(serialport, baudrate=9600)
  else:
    print "WARNING: Serial port not found! Program will operate in 'pretend' mode.\n"
  relayOn() # Lock the door to start ;)
  while True:
    scanLoop()

def logOpen(data):
  rndfile = ''.join([random.choice('abcdefghijklmnoprstuvwyxzABCDEFGHIJKLMNOPRSTUVWXYZ') for i in range(15)])
  f = open(spooldir+"/"+rndfile, 'w')
  data['time'] = datetime.datetime.now().isoformat()
  f.write(json.dumps(data))
  f.close()

def openTheDoor():
  relayOff()
  time.sleep(seconds_to_keep_door_open)
  relayOn()

def scanLoop():
  key = raw_input('RFID> ').strip()
  if key in ["exit","exit()","quit","quit()"]:
    print "[EXIT] Exiting"
    sys.exit(0)  
  if key:
    print "[DEBUG] I just scanned " + key
    userData = getUsers()
    print "[DEBUG] Comparing to " + str(len(userData)) + " RFIDs..."
    foundUser = None
    for user in userData:
       if key == user['rfid_tag']:
          foundUser = user
    if foundUser:
      print '[FOUND] ' + foundUser['username']
      openTheDoor()
      logOpen(foundUser)
      foundUser = None
    else:
      print '[NOTFOUND] Sorry, RFID key not found'
      
main()
