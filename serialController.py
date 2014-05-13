import serial
import time
import urllib
import json
import sys
import os
import random
import threading
import thread
import urllib2
import datetime
import signal
import time
from time import gmtime, strftime
from subprocess import call
import rfidtag

# Use of the velleman-vm110n board assumes that our sensor pin is using
# digital input 1 and the maglock on digital output 1
# *********************************************
# 2014-05-09, velleman and serialrelay are obsolete, now using insteon devices
#   rfid tag is retrieved via rfidtag.py
# *********************************************

# this is the 3 possible methods to control the door, velleman & serialrelay are obsolete
velleman = False
serialrelay = False 
insteon = True


if velleman:
  from pyk8055 import *
  velleman = k8055(0)

# This program runs from /etc/rc and takes keyboard input.

door = "599main"
serialport = '/dev/ttyUSB0'
relayfile = None
seconds_to_keep_door_open = 6
spooldir = '/root/unlock_spool'
hour = datetime.datetime.now().hour
print hour
day = (hour >= 8 and hour < 22)
doorOpenAt = False
audioPlayTime = int(time.time())

def interrupted(signum, frame):
  global day
  print '[interrupted!] '
  if signum == 14: #ALRM
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [DAYTIME] Unlocking for day-time hours"
    day = True
    unlockTheDoor()
  if signum == 2: #INT
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [NIGHT] Locking up for after-hours"
    day = False
    lockTheDoor()

def lockTheDoor():
  print strftime("%Y-%m-%d %H:%M:%S", gmtime())+' [RELAYON] The door is now LOCKED'
  if insteon:
    os.system("insteon lobbyright off")
  if velleman:
    # This will make digital output 1 HIGH
    velleman.WriteAllDigital(0)
  if serialrelay:
    if relayfile:
      relayfile.setDTR(True)
      relayfile.setRTS(True)
    #try:
    # urllib.urlopen("http://10.15.0.17/red")
    #except:
    #  print "Unexpected error:", sys.exc_info()[0]

def unlockTheDoor():
  print strftime("%Y-%m-%d %H:%M:%S", gmtime())+' [RELAYOFF] The door is now UNLOCKED'
  if insteon:
    os.system("insteon lobbyright on")
  if velleman:
    # This will make digital output 1 LOW
    velleman.WriteAllDigital(1)
  if serialrelay:
    if relayfile:
      relayfile.setDTR(False)
      relayfile.setRTS(False)
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
  global audioPlayTime
  now = int(time.time())
  if velleman:
    if velleman.ReadDigitalChannel(1) == 1:
      if doorOpenAt:
        print "door is closed"
        call(["killall", "mpg123-alsa"])
      doorOpenAt = False
    else:
      if not doorOpenAt:
        doorOpenAt = now
      #if (now - doorOpenAt) > 20:
      #  # Door has been open for 2 minutes, sound alarm:
      #  if (now - audioPlayTime) > 10:
      #    print 'Door has been open too long!'
      #    audioPlayTime = now
      #    call(["mpg123-alsa", "/usr/local/lib/pleaseclose.mp3"])
    threading.Timer(1, checkDoorOpen).start()
  else:
    return False

checkDoorOpen()

def getUsers():
  try:
    userURL = urllib.urlopen('/opt/maglock/rfid.keys')
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
  print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [ERROR] " + str(msg)
  print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [ERROR] " + str(err)
  sys.exit(0)

def main():
  device_file = rfidtag.get_rfid_device_file()
  global relayfile
  print "\n"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Hacker Dojo RFID Entry System v0.221\n"
  if serialrelay:
    relayfile = serial.Serial(serialport, baudrate=9600)
# if it's during normal guest hours, open the door
  if day:
    unlockTheDoor()
  else:
    lockTheDoor()
  while True:
    scanLoop(device_file)

def logOpen(data):
  rndfile = ''.join([random.choice('abcdefghijklmnoprstuvwyxzABCDEFGHIJKLMNOPRSTUVWXYZ') for i in range(15)])
  f = open(spooldir+"/"+rndfile, 'w')
  data['time'] = datetime.datetime.now().isoformat()
  f.write(json.dumps(data))
  f.close()
  t = Thread(target=ThreadLog, args=(data,))
  t.start()

def openTheDoor():
  unlockTheDoor()
  time.sleep(seconds_to_keep_door_open)
  lockTheDoor()


def scanLoop(dev_file):
  global day
  signal.signal(signal.SIGALRM, interrupted)
  signal.signal(signal.SIGINT, interrupted)
  if day:
    mode = "day"
  else:
    mode = "night"
  try:
    #key = raw_input(strftime("%Y-%m-%d %H:%M:%S", gmtime())+' RFID ('+mode+')> ').strip()
    key = rfidtag.get_tag(dev_file)
    print key
  except:
    print ""
    key = ""
  if key == "unlock":
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [Overide] Unlocking"
    day = True
    unlockTheDoor()
    key = ""
  if key == "lock":
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [Overide] Locking"
    day = False
    lockTheDoor()
    key = ""
  if key in ["exit","exit()","quit","quit()"]:
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [EXIT] Exiting"
    sys.exit(0)
  # Only look at keys during the night
  if not day and key:
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [DEBUG] I just scanned " + key
    userData = getUsers()
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [DEBUG] Comparing to " + str(len(userData)) + " RFIDs..."
    foundUser = None
    username = ""
    status = "denied"
    for user in userData:
       if key == user['rfid_tag']:
          foundUser = user
          username = foundUser['username']
          status = "granted"
    url = 'https://hackerdojo-signin.appspot.com/api/doorlog?door='+door+'&status='+status+'&rfid_tag='+key+'&username='+username
    threading.Thread(target=urllib.urlopen, args=[url]).start()
    if foundUser:
      print strftime("%Y-%m-%d %H:%M:%S", gmtime())+' [FOUND] ' + foundUser['username']
      openTheDoor()
      #logOpen(foundUser)
      foundUser = None
    else:
      print strftime("%Y-%m-%d %H:%M:%S", gmtime())+' [NOTFOUND] Sorry, RFID key not found'

main()
