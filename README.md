# dualarm_ros2_ws 

`ros2 launch dual_arm_gazebo dual_arm_gazebo.launch.py`

# Enable/Disable service
`ros2 run dual_arm_driver motor_enable_service`

# enable motors
`ros2 service call /enable_motors std_srvs/srv/Trigger {}`