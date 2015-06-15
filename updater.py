import serial
import time
import urllib
import json
import sys

# This program runs from a cronjob every 5 minutes

from keys import maglock_key

def fatal(msg,err):
  print "\n"
  print "[ERROR] " + str(msg)
  print "[ERROR] " + str(err)
  sys.exit(0)

def main():
  try:
    base_url = 'http://signup.hackerdojo.com/api/v1/maglock/'
    response = urllib.urlopen(base_url + maglock_key)
    data = response.read()
    response.close()
  except:
    fatal("Unable to connect to server",sys.exc_info()[0])
  try:
    userData = json.loads(data)
  except:
    fatal("Unable to parse JSON",sys.exc_info()[0])
  if len(userData) < 1:
    fatal("Number of RFID tags too small")
  try:
    FILE = open("/opt/maglock/rfid.keys","w")
    FILE.writelines(data)
    FILE.close()
  except:
    fatal("Unable to write RFID data",sys.exc_info()[0])

main()
