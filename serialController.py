import serial
import time
import urllib
import json
import sys
import os
import random
import datetime
import signal
import time
from subprocess import call
import threading

# Use of the velleman-vm110n board assumes that our sensor pin is using
# digital input 1 and the maglock on digital output 1
velleman = True

if velleman:
  from pyk8055 import *
  velleman = k8055(0)

# This program runs from /etc/rc and takes keyboard input. 

serialport = '/dev/ttyUSB0'
relayfile = None
seconds_to_keep_door_open = 6
spooldir = '/root/unlock_spool'
day = False
doorOpenAt = int(time.time())
  
def interrupted(signum, frame):
  global day
  print '[interrupted!] '
  if signum == 14: #ALRM
    print "[DAYTIME] Unlocking for day-time hours"
    day = True
    relayOff()
  if signum == 2: #INT
    print "[NIGHT] Locking up for after-hours"
    day = False
    relayOn()

def relayOn():
  print '[RELAYON] The door is now locked <red>'
  if velleman:
    # This will make digital output 1 HIGH
    velleman.WriteAllDigital(1)
  else:
    if relayfile:
      relayfile.setDTR(True)
    #try:
    # urllib.urlopen("http://10.15.0.17/red")
    #except:
    #  print "Unexpected error:", sys.exc_info()[0]

def relayOff():
  print '[RELAYOFF] The door is now unlocked <white>'
  if velleman:
    # This will make digital output 1 LOW
    velleman.WriteAllDigital(0)
  else:
    if relayfile:
      relayfile.setDTR(False)
    #try:
    #  urllib.urlopen("http://10.15.0.17/white")
    #except:
    #  print "Unexpected error:", sys.exc_info()[0]

# This function will execute once every 60 seconds
# to check if the door is open or not.  If the door
# stays open for more than 2 minutes, it will sound
# the alarm
def checkDoorOpen():
  global doorOpenAt
  now = int(time.time())
  if velleman:
    if velleman.ReadDigitalChannel(1) == 1:
      # door is closed
      print 'Door is closed'
      doorOpenAt = False
    else:
      print 'Door is open'
      if not doorOpenAt:
        doorOpenAt = now
      if (now - doorOpenAt) > 120:
        # Door has been open for 2 minutes, sound alarm:
        print 'Door has been open too long!'
        call(["mpg123-alsa", "/usr/local/lib/money.mp3"])
        threading.Timer(10, checkDoorOpen).start()
      else:
        threading.Timer(20, checkDoorOpen).start()
  else:
    return False

checkDoorOpen()

def getUsers():
  try:
    userURL = urllib.urlopen('/root/rfid.keys')
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
  global day
  signal.signal(signal.SIGALRM, interrupted)
  signal.signal(signal.SIGINT, interrupted)
  if day:
    mode = "day"
  else:
    mode = "night"
  try:
    key = raw_input('RFID ('+mode+')> ').strip()
  except:
    print ""
    key = ""
  if key in ["exit","exit()","quit","quit()"]:
    print "[EXIT] Exiting"
    sys.exit(0)  
  # Only look at keys during the night
  if not day and key:
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
