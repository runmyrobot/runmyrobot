import RunMyRobot
robotID = 'ChangeMe'

	
@RunMyRobot.messages
def messages(args):
    print args
	
@RunMyRobot.exclusive_control
def exclusive_control(args):
    print args
	
RunMyRobot.run(robotID)
	
