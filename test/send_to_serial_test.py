import serial
import sys
import glob
     

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


#print "-----------------"
#print serial_ports()
#print "-----------------"



#ser = serial.Serial(device, baud, timeout=0)
#ser.nonblocking()
#print 'Opened %s, baud %d' % (device, baud)

#ser.write('\r\n!\r\necho off\r\n')
#time.sleep(1)
#serial.flushInput()


def sendCommandsFromUser():
    #for baud in (9600, 19200, 38400, 57600):
    for baud in (9600,):
        print "baud:", baud
        #ser = serial.Serial('/dev/tty.usbmodem12341', 19200, timeout=1)  # open serial
        ser = serial.Serial('/dev/tty.usbmodem12341', baud, timeout=1)  # open serial
        print(ser.name)         # check which port was really used
        ser.nonblocking()

        # loop to collect input
        while(True):
            s = raw_input()
            print "string:", s
            ser.write(s + "\r\n")     # write a string
            #ser.write(s)
            ser.flush()

            while ser.in_waiting > 0:
                print "read:", ser.read()

        ser.close()



def sendCommand():

    baud1 = 9600
    print "baud:", baud1
    #ser = serial.Serial('/dev/tty.usbmodem12341', 19200, timeout=1)  # open serial
    ser = serial.Serial('/dev/tty.usbmodem12341', baud1, timeout=1)  # open serial
    print(ser.name)         # check which port was really used
    ser.nonblocking()

    # loop to collect input
    s = "f"
    print "string:", s
    ser.write(s + "\r\n")     # write a string
    #ser.write(s)
    ser.flush()

    while ser.in_waiting > 0:
        print "read:", ser.read()

    ser.close()


sendCommand()


