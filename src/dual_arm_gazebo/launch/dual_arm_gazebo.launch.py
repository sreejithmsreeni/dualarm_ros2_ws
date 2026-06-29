import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetUseSimTime

SIM_TIME_ARGS = ['-p', 'use_sim_time:=true']


def generate_launch_description():
    package_name = 'dual_arm_description'
    urdf_file = 'dual_arm.urdf.xacro'
    urdf_file_path = os.path.join(get_package_share_directory(package_name), 'urdf', urdf_file)
    controllers_file = os.path.join(
        get_package_share_directory('dual_arm_gazebo'),
        'config',
        'dual_arm_gazebo_controllers.yaml',
    )

    robot_description_config = xacro.process_file(
        urdf_file_path,
        mappings={'use_gazebo_control': 'true'},
    )
    robot_description_xml = robot_description_config.toxml()

    # Save processed URDF so Gazebo loads mesh paths with filenames intact
    urdf_out_path = os.path.join(
        get_package_share_directory('dual_arm_gazebo'),
        'config',
        'dual_arm.gazebo.urdf',
    )
    with open(urdf_out_path, 'w', encoding='utf-8') as urdf_out:
        urdf_out.write(robot_description_xml)

    robot_description = {'robot_description': robot_description_xml}
    sim_time = {'use_sim_time': True}

    gazebo_launch_path = os.path.join(
        get_package_share_directory('ros_gz_sim'),
        'launch',
        'gz_sim.launch.py',
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[sim_time, robot_description],
        ros_arguments=SIM_TIME_ARGS,
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        parameters=[sim_time],
        arguments=[
            '-file', urdf_out_path,
            '-name', 'dual_arm',
            '-allow_renaming', 'true',
            '-x', '0', '-y', '0', '-z', '1.5',
        ],
        output='screen',
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        parameters=[sim_time],
        arguments=['joint_state_broadcaster', '--controller-manager-timeout', '60'],
        output='screen',
    )

    left_arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        parameters=[sim_time],
        arguments=[
            'left_arm_controller',
            '--param-file', controllers_file,
            '--controller-manager-timeout', '60',
        ],
        output='screen',
    )

    right_arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        parameters=[sim_time],
        arguments=[
            'right_arm_controller',
            '--param-file', controllers_file,
            '--controller-manager-timeout', '60',
        ],
        output='screen',
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[sim_time],
        ros_arguments=SIM_TIME_ARGS,
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    return LaunchDescription([
        SetUseSimTime(True),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulated clock from Gazebo',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([gazebo_launch_path]),
            launch_arguments={'gz_args': '-r -v 1 empty.sdf'}.items(),
        ),
        clock_bridge,
        robot_state_publisher,
        spawn_entity,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[
                    TimerAction(period=3.0, actions=[joint_state_broadcaster_spawner]),
                ],
            ),
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[
                    left_arm_controller_spawner,
                    right_arm_controller_spawner,
                ],
            ),
        ),
    ])
