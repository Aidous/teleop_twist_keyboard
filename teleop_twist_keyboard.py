#!/usr/bin/env python

from __future__ import print_function

import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy

from geometry_msgs.msg import Twist

import sys, select, termios, tty

msg = """
Reading from the keyboard  and Publishing to Twist!

CTRL-C to quit
"""

speedBindings={
        'w':(0.1,0.0),
        's':(-0.1,0.0),
        'a':(0.0,0.1),
        'd':(0.0,-0.1),
    }

def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
    rospy.init_node('teleop_twist_keyboard_speed')

    speed = rospy.get_param("~speed", 0.0)
    turn = rospy.get_param("~turn", 0.0)
    x = 0
    y = 0
    z = 0
    th = 0
    status = 0

    try:
        print(msg)
        print(vels(speed,turn))
        while(1):
            key = getKey()
            if key in speedBindings.keys():
                speed = speed + speedBindings[key][0]
                turn = turn + speedBindings[key][1]

		if (speed > 6.0):
		   speed = 6.0
		elif (speed < -6.0):
		   speed = -6.0

		if (turn > 32.0):
		   turn = 32.0
		elif (turn < -32.0):
		   turn = -32.0

                print(vels(speed,turn))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
            else:
                x = 0
                y = 0
                z = 0
                th = 0
                if (key == '\x03'):
                    break

            twist = Twist()
            twist.linear.x = speed; twist.linear.y = 0.0; twist.linear.z = 0.0;
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = turn
            pub.publish(twist)

    except Exception as e:
        print(e)

    finally:
        twist = Twist()
        twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        pub.publish(twist)

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
