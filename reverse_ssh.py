import argparse
import thread
import subprocess
from socketIO_client import SocketIO, LoggingNamespace


def main():

   global commandArgs
   global robotID
   global appServerSocketIO

   parser = argparse.ArgumentParser(description='start robot control program')

   parser.add_argument('robot_id', help='Robot ID')   
   parser.add_argument('--reverse-ssh-key-file', default='/home/pi/reverse_ssh_key1.pem')
   parser.add_argument('--reverse-ssh-host', default='ubuntu@52.52.204.174')
   
   commandArgs = parser.parse_args()
   print commandArgs
   robotID = commandArgs.robot_id


   print "connecting to app server socket.io"
   appServerSocketIO = SocketIO('letsrobot.tv', 8022, LoggingNamespace)
   print "finished connecting to app server"
   
   appServerSocketIO.on('connect', onHandleAppServerConnect)
   appServerSocketIO.on('reconnect', onHandleAppServerReconnect)
   appServerSocketIO.on('disconnect', onHandleAppServerDisconnect)
    
   appServerSocketIO.on('reverse_ssh_8872381747239', startReverseSshProcess)
   appServerSocketIO.on('end_reverse_ssh_8872381747239', endReverseSshProcess)


   while True:
      appServerSocketIO.wait(seconds=1)



def startReverseSshProcess(*args):
   thread.start_new_thread(handleStartReverseSshProcess, args)

   
def endReverseSshProcess(*args):
   thread.start_new_thread(handleEndReverseSshProcess, args)



def handleStartReverseSshProcess(args):
    print "starting reverse ssh"
    appServerSocketIO.emit("reverse_ssh_info", "starting")

    returnCode = subprocess.call(["/usr/bin/ssh",
                                  "-X",
                                  "-i", commandArgs.reverse_ssh_key_file,
                                  "-N",
                                  "-R", "2222:localhost:22",
                                  commandArgs.reverse_ssh_host])

    appServerSocketIO.emit("reverse_ssh_info", "return code: " + str(returnCode))
    print "reverse ssh process has exited with code", str(returnCode)

    
def handleEndReverseSshProcess(args):
    print "handling end reverse ssh process"
    resultCode = subprocess.call(["killall", "ssh"])
    print "result code of killall ssh:", resultCode



def onHandleAppServerConnect(*args):
    print
    print "chat socket.io connect"
    print
    identifyRobotID()


def onHandleAppServerReconnect(*args):
    print
    print "app server socket.io reconnect"
    print
    identifyRobotID()    
    

def onHandleAppServerDisconnect(*args):
    print
    print "app server socket.io disconnect"
    print


    
def identifyRobotID():
    """tells the server which robot is using the connection"""
    print "sending identify robot id messages"
    appServerSocketIO.emit('identify_robot_id', robotID);


    

      
main()

