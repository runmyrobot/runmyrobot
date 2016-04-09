import os
import time

while True:

    result = os.system("wget google.com")
    print "result:", result
    if result != 0:
        print "running a down up to get connection back"
        print "ifdown", os.system("sudo ifdown wlan0")
        print "ifup", os.system("sudo ifup wlan0")
    time.sleep(30)
