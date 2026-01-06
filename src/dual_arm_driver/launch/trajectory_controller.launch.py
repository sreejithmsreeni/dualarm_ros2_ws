import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.actions import TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessStart


def generate_launch_description():
    # Define the path to your ros2_control.xml file
    robot_description_path = os.path.join(
        get_package_share_directory('dual_arm_driver'),
        'config',
        'ros2_control.xml'
    )

    # Use ParameterValue to ensure the robot_description is passed as a string
    robot_description_content = ParameterValue(
        Command(['cat ', robot_description_path]),
        value_type=str
    )

    # 1. Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}]
    )

    # 2. ros2_control node (Controller Manager)
    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
            PathJoinSubstitution([FindPackageShare('dual_arm_driver'), 'config', 'trajectory_controller.yaml'])
        ],
    )

    # 3. Joint state broadcaster spawner
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # 4. Trajectory controller spawner
    trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["trajectory_controller", "-c", "/controller_manager"],
        output='screen'
    )

    # 5. Startup node (init_trajectory_node.py)
    startup_node = Node(
        package='dual_arm_driver',
        executable='init_trajectory_node.py',
        output='screen',
    )

    # Event handlers for proper startup sequence
    # Order: ros2_control_node -> delay -> joint_state_broadcaster -> trajectory_controller -> startup_node
    delay_after_control_node = TimerAction(
        period=15.0,  # 5 seconds delay after ros2_control_node starts
        actions=[joint_state_broadcaster_spawner],
    )

    event_handlers = [
        # Start joint_state_broadcaster 5 seconds after ros2_control_node
        RegisterEventHandler(
            OnProcessStart(
                target_action=ros2_control_node,
                on_start=[delay_after_control_node]
            )
        ),
        # Start trajectory_controller after joint_state_broadcaster
        RegisterEventHandler(
            OnProcessStart(
                target_action=joint_state_broadcaster_spawner,
                on_start=[trajectory_controller_spawner]
            )
        ),
        # # Start startup_node after trajectory_controller
        # RegisterEventHandler(
        #     OnProcessStart(
        #         target_action=trajectory_controller_spawner,
        #         on_start=[startup_node]
        #     )
        # ),
    ]

    return LaunchDescription([
        robot_state_publisher_node,
        ros2_control_node,
        # Note: Don't add the spawners directly - they're handled by event handlers
        # *event_handlers,  # Unpack all event handlers
    ])
