
import robot_util


def sendSettings(ser, args):

    if args.right_wheel_forward_speed is not None:
        robot_util.sendSerialCommand(ser, "rwfs " + str(args.right_wheel_forward_speed))

    if args.right_wheel_backward_speed is not None:
        robot_util.sendSerialCommand(ser, "rwbs " + str(args.right_wheel_backward_speed))

    if args.left_wheel_forward_speed is not None:
        robot_util.sendSerialCommand(ser, "lwfs " + str(args.left_wheel_forward_speed))

    if args.left_wheel_backward_speed is not None:
        robot_util.sendSerialCommand(ser, "lwbs " + str(args.left_wheel_backward_speed))

    if args.straight_delay is not None:
        robot_util.sendSerialCommand(ser, "straight-distance " + str(int(args.straight_delay * 255)))

    if args.turn_delay is not None:
        robot_util.sendSerialCommand(ser, "turn-distance " + str(int(args.turn_delay * 255)))
        
    if args.led_max_brightness is not None:
        robot_util.sendSerialCommand(ser, "led-max-brightness " + str(args.led_max_brightness))
