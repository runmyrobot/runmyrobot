#import the USB and Time librarys into Python
import usb.core, usb.util, time

# led pesistence variable
led = 0  

#Allocate the name 'RoboArm' to the USB device
RoboArm = usb.core.find(idVendor=0x1267, idProduct=0x000)
 
#Check if the arm is detected and warn if not
if RoboArm is None:
    raise ValueError("Arm not found")
 
#Create a variable for duration
#Duration=1

def CtrlTransfer(a, b, c, d, e, f):
    global led
    error = 0
    while True :
        try:
            e[2] = led
            RoboArm.ctrl_transfer(a, b, c, d, e, f)
            break
        except:
            error += 1
            print("USB timeout!")
            time.sleep(0.1)
            if error == 5:
               sys.exit()
            pass
 
#Define a procedure to execute each movement
def MoveArm(Duration, ArmCmd):
    #Start the movement
#    RoboArm.ctrl_transfer(0x40,6,0x100,0,ArmCmd,3)
    CtrlTransfer(0x40,6,0x100,0,ArmCmd,3)
    #Stop the movement after waiting a specified duration
    time.sleep(Duration)
    ArmCmd=[0,0,0]
#    RoboArm.ctrl_transfer(0x40,6,0x100,0,ArmCmd,3)
    CtrlTransfer(0x40,6,0x100,0,ArmCmd,3)

def handleOwiArm(command):
    global led

    if command == 'L':
        MoveArm(0.15, [0,2,0]) # Rotate counter-clockwise
    if command == 'R':
        MoveArm(0.15, [0,1,0]) # Rotate clockwise
    if command == 'B':
        MoveArm(0.15, [128,0,0]) # Rotate Shoulder down
    if command == 'F':
        MoveArm(0.15, [64,0,0]) # Rotate Shoulder up
    if command == 'U':
        MoveArm(0.15, [16,0,0]) # Rotate Elbow up
    if command == 'D':
        MoveArm(0.15, [32,0,0]) # Rotate Elbow down
    if command == 'W':
        MoveArm(0.15, [4,0,0]) # Rotate Wrist Up
    if command == 'S':
        MoveArm(0.15, [8,0,0]) # Rotate Wrist Down
    if command == 'C':
        MoveArm(0.15, [2,0,0]) # Open Gripper
    if command == 'V':
        MoveArm(0.15, [1,0,0]) # Close Gripper
    if command == '1':
        led = 1;
        MoveArm(0.15, [0,0,1]) # LED On
    if command == '0':
        led = 0;
        MoveArm(0.15, [0,0,0]) # LED Off

