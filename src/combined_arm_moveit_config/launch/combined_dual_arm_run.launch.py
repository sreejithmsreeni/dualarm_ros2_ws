import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    # Paths to packages
    moveit_cfg = get_package_share_directory('combined_arm_moveit_config')
    driver_pkg = get_package_share_directory('dual_arm_driver')

    # 1) Include your EtherCAT bringup (ros2_control + controller spawners)
    driver_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(driver_pkg, 'launch', 'dual_arm_bringup.launch.py')
        )
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    # left_arm_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["left_arm_controller", "--controller-manager", "/controller_manager"],
    # )

    # right_arm_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["right_arm_controller", "--controller-manager", "/controller_manager"],
    # )

    dual_arm_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["dual_arm_controller", "--controller-manager", "/controller_manager"],
    )
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
        joint_state_broadcaster_spawner,
        # left_arm_spawner,
        # right_arm_spawner,
        dual_arm_spawner,
        move_group,
        rviz,
    ])
