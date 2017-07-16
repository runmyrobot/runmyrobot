import RunMyRobot
robotID = 'ChangeMe'

@RunMyRobot.commands
def commands(args):
    print args	
	
@RunMyRobot.messages
def messages(args):
    print args
	
@RunMyRobot.exclusive_control
def exclusive_control(args):
    print args
	
RunMyRobot.run(robotID)
	
