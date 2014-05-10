import serial
import time
import urllib
import json
import sys
import os
import signal
from time import gmtime, strftime

# 2014-05-09; this program removed from cronjob as it fails
#   see below comments for where it probably fails;
#   we made a command decision to not fix it, as we don't really 
#   need it.
# This program runs from a cronjob every 15 minutes

from keys import maglock_key

def interrupted(signum, frame):
  noop = True
      
def fatal(msg,err):
  print "\n"
  print "[ERROR] " + str(msg)
  print "[ERROR] " + str(err)
  sys.exit(0)

def main():
  signal.signal(signal.SIGALRM, interrupted)
  signal.signal(signal.SIGINT, interrupted)
  localtime = time.localtime(time.time())
  nowish = strftime("%Y-%m-%dT%H:%M:%S", localtime)[:-3]
  try:
    userURL = urllib.urlopen('http://events.hackerdojo.com/events.json')
    data = userURL.read()
    userURL.close()
  except:
    fatal("Unable to connect to server",sys.exc_info()[0])
  try:
    eventData = json.loads(data)
  except:
    fatal("Unable to parse JSON",sys.exc_info()[0])
  if len(eventData) < 1:
    fatal("Number of events too small")
  for e in eventData:
		if 'approved' in e['status']: 
			# 2014-05-09; this program fails apparently at a below noted line
			# print statements for troubleshooting
			print nowish + " nowish"
			print e['start_time'][:-3] + " whatsup"
			# here is where if fails - it must run exactly at the time the start time is
			#   or it will not open the door
			if nowish in e['start_time'][:-3]:
				print "UNLOCK"
				os.system('/usr/bin/killall -ALRM python')
			if nowish in e['end_time'][:-3]:
				print "LOCK"
				os.system('/usr/bin/killall -INT python')
          
main()
