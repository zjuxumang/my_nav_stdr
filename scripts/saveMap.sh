#!/bin/bash

rosrun map_server map_saver map:=/gmapping/map -f ~/stdr_ws/src/my_nav_stdr/maps/mymap
rosnode kill slam_gmapping
play ~/catkin_ws/map_saved.wav
exit 0