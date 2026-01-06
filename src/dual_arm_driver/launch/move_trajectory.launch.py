from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

def generate_launch_description():
    """
    Launch file to spawn controllers and start the movement node sequentially.
    This ensures controllers are ready before the motion commands are sent.
    """

    # 1. Spawner for the joint_state_broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # 2. Spawner for the trajectory_controller
    trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["trajectory_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # 3. Node for continuous movement
    move_trajectory_node = Node(
        package='dual_arm_driver',  # CHANGE to your package name
        executable='move_trajectory_node.py',
        name='move_trajectory_node',
        output='screen'
    )

    # --- Event Handler Chain for Robust Startup ---
    # This chain ensures each component starts only after the previous one is active.
    event_handlers = [
        # Start trajectory_controller after joint_state_broadcaster is active
        RegisterEventHandler(
            OnProcessStart(
                target_action=joint_state_broadcaster_spawner,
                on_start=[trajectory_controller_spawner]
            )
        ),
        # Start the move_trajectory_node after the trajectory_controller is active
        RegisterEventHandler(
            OnProcessStart(
                target_action=trajectory_controller_spawner,
                on_start=[move_trajectory_node]
            )
        )
    ]

    return LaunchDescription([
        # The chain starts by launching the first spawner
        joint_state_broadcaster_spawner,
        # The event handlers will trigger the rest of the sequence
        *event_handlers
    ])
