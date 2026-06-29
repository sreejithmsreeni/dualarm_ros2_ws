import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    # Paths to packages
    moveit_cfg = get_package_share_directory('combined_arm_moveit_config')
 
    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_cfg, 'launch', 'move_group.launch.py')
        ),
        launch_arguments={
            'use_fake_hardware': 'false',
            'use_sim_time': 'false',
        }.items()
    )

    # 3) Include RViz with MoveIt config
    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_cfg, 'launch', 'moveit_rviz.launch.py')
        )
    )

    return LaunchDescription([
        # driver_bringup,
        move_group,
        rviz,
    ])
