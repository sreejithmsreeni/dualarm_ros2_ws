import os
from launch import LaunchDescription
from launch.actions import TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.substitutions import PathJoinSubstitution

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from launch_ros.parameter_descriptions import ParameterValue
import xacro

def generate_launch_description():


    xacro_file = os.path.join(
        get_package_share_directory('dual_arm_description'),
        'urdf',
        'single_arm.urdf.xacro'
    )
    robot_description_content = xacro.process_file(xacro_file).toxml()

    robot_description = ParameterValue(robot_description_content, value_type=str)

    # --- ADD THIS ---
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )
    # ----------------

    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        output='screen',
        parameters=[
            {'robot_description': robot_description},
            PathJoinSubstitution([
                FindPackageShare('dual_arm_driver'),
                'config',
                'trajectory_controller.yaml'
            ])
        ]
    )


    return LaunchDescription([
        robot_state_publisher_node,  #
        ros2_control_node,
    ])
