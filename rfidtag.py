import os
#!/usr/bin/env python

# below is the string name of the USB device we want to read
#   the rfid tags from 
DEVICE_NAME="NewRoad Sem. NewRoad System PS2 Interface"

# find how many hidraw devices are connected and then
#   find which hidraw device the rfid reader is connected to
def get_rfid_device_file():
	numdevs = len(os.popen('ls /dev |grep hidraw').read().split("\n"))
	for i in range(numdevs):
		path = '/sys/class/hidraw/hidraw' + str(i) + '/device/uevent'
		device_info = os.popen('cat ' + path).read()
		if DEVICE_NAME in device_info:
			return '/dev/hidraw'+str(i)
	return '/dev/null'
		
# get the rfid code
def get_tag(dev):
    """
    Get rfidtag.

    This function reads an hidraw data stream from a rfidtag scanner
    returns the numeric value of the rfidtag scnned.

    Parameters
    ----------
    dev : str, optional
        Full path hidraw device from which to read hidraw data stream.
        Default path is `/dev/hidraw0`.

    Returns
    -------
    rfidtag : str
        String representation of numerical value of scanned rfidtag.

    """
    hiddev = open(dev, "rb")
 
    rfidtag = ''

    continue_looping = True

    k = 0

    while continue_looping:
        report = hiddev.read(10)

        # print "k value: ", k
        k += 1

        for i in report:
            j = ord(i)
            # # print j
            if j == 0:
                # print "j = ", j
                continue

            if j == 0x1E:
                rfidtag += '1'
                # print "j = ", j
                continue
            elif j == 0x1F:
                rfidtag += '2'
                # print "j = ", j
                continue
            elif j == 0x20:
                rfidtag += '3'
                # print "j = ", j
                continue
            elif j == 0x21:
                rfidtag += '4'
                # print "j = ", j
                continue
            elif j == 0x22:
                rfidtag += '5'
                # print "j = ", j
                continue
            elif j == 0x23:
                rfidtag += '6'
                # print "j = ", j
                continue
            elif j == 0x24:
                rfidtag += '7'
                # print "j = ", j
                continue
            elif j == 0x25:
                rfidtag += '8'
                # print "j = ", j
                continue
            elif j == 0x26:
                rfidtag += '9'
                # print "j = ", j
                continue
            elif j == 0x27:
                rfidtag += '0'
                # print "j = ", j
                continue
            elif j == 0x28:
                # print "j = ", j
                # print rfidtag
                hiddev.close()
                continue_looping = False
                break
            else:
                pass
                # print "+++ Melon melon melon +++"
                # print "j = ", j
                # hiddev.close()
                # continue_looping = False
                # break

    return rfidtag
