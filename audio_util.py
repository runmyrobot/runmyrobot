import subprocess
import re

def getAudioDeviceByName(name):

	text = subprocess.check_output(['aplay', '-l'])
	lines = text.splitlines()
	for line in lines:
		if name in line:
			print line
			result = re.match("card (.*?):", line)
			print result.group(0)
			print result.group(1)
			return int(result.group(1))



if __name__ == "__main__":
	print "as a test, checking for Yeti mic"
	print getAudioDeviceByName("Yeti")


