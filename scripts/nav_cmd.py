#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''nav_cmd ROS Node'''
# license removed for brevity
from __future__ import print_function
#import roslib; roslib.load_manifest('nav_cmd')
import rospy
import os
from std_msgs.msg import Int32
from std_msgs.msg import String
from std_srvs.srv import *
from geometry_msgs.msg import Twist
import sys, select, termios , tty

msg = """
多功能社区服务车控制系统 v1.0
请通过键盘发送指令
----------------------------------------
S 启动主控程序       G 激光雷达启动/停止扫描
M 开始地图构建       N 启动导航图形界面
D 启动送餐路线       B 启动通知巡游播报
Y 键盘遥控模式       R 重启系统
----------------------------------------

按CTRL+C退出
"""
def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin],[],[],0)
    key=sys.stdin.read(1)
    termios.tcsetattr(sys.stdin,termios.TCSADRAIN,settings)
    return key

msg_teleop = """
按下列键控制服务车移动，按d退出
---------------------------
   u    i    o
   j    k    l
   m    ,    .
---------------------------
"""

moveBindings = {
		'i':(1,0,0,0),
		'o':(1,0,0,-1),
		'j':(0,0,0,1),
		'l':(0,0,0,-1),
		'u':(1,0,0,1),
		',':(-1,0,0,0),
		'.':(-1,0,0,1),
		'm':(-1,0,0,-1)
	       }

def teleop_twist_keyboard():
    os.system('clear')
    pub_vel = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
    print(msg_teleop)
    speed = 0.13
    turn = 1.0
    while(1):
        key = getKey()
        if key in moveBindings.keys():
            x = moveBindings[key][0]
            y = moveBindings[key][1]
            z = moveBindings[key][2]
            th = moveBindings[key][3]
        else:
            x = 0
            y = 0
            z = 0
            th = 0
            if (key == 'd'):
                break

        twist = Twist()
        twist.linear.x = x*speed; twist.linear.y = y*speed; twist.linear.z = z*speed
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*turn
        pub_vel.publish(twist)
is_reboot=0
if __name__ == '__main__':
    settings = termios.tcgetattr(sys.stdin)

    pub = rospy.Publisher('current_cmd', String, queue_size=10)
    rospy.init_node('nav_cmd', anonymous=True)
    rate=rospy.Rate(10)
    motor_flag=1
    os.system('clear')
    try:
        print(msg)
        while not rospy.is_shutdown():
            key=getKey()
            if key == 's':
                pub.publish('s')
                print("服务车启动中........")
                try:
                    rospy.wait_for_service('is_running',30)
                    is_running = rospy.ServiceProxy('is_running', Trigger)
                    resp = is_running()
                    if resp.success == True:
                        print("启动成功！")  
                except:
                    print("启动失败，请检查电源后重试！")     
                is_running.close()
            elif key == 'm':
                pub.publish('m')
                print("gmapping启动中........")
                os.system('rosrun rviz rviz >/dev/null &')
                teleop_twist_keyboard()
                while(1):
                    print("按s保存地图，按c放弃保存并退出")
                    key=getKey()
                    if key == 's':
                        pub.publish('savemap')
                        print("地图保存中........")
                        rospy.sleep(5)
                        print("完成！")
                        rospy.sleep(2)
                        break
                    elif key == 'c':
                        pub.publish('exitgmapping')
                        print('退出')
                        rospy.sleep(2)
                        break
                    else: 
                        pass
                os.system("clear")
                print(msg)
            elif key == 'n':
                pub.publish('n')
                os.system('rosrun rviz rviz >/dev/null &')
            elif key == 'y':
                teleop_twist_keyboard()
                os.system('clear')
                print("退出遥控模式")
                print(msg)
            elif key == 'g':
                if motor_flag==1:
                    os.system('rosservice call /stop_motor')
                    motor_flag=0
                else:
                    os.system('rosservice call /start_motor')
                    motor_flag=1
            elif key == 'r':
                print("系统重启中.............")
                is_reboot=1
                pub.publish('r')
                print("按任意键继续")
            elif key == 'd':
                os.system('roslaunch my_nav patrol_nav.launch')
            else:
                if(key== '\x03'):
                    break
                print("unkown cmd")

    except rospy.ROSInterruptException:
        pass
    finally:
        if is_reboot == 1:
            os.system('rosrun my_nav nav_cmd.py')
        else:
            print("退出控制客户端......")
