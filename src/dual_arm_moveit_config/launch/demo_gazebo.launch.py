import os
import tempfile

import yaml
from ament_index_python.packages import get_package_prefix
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.utilities import perform_substitutions
from launch_ros.actions import Node, SetUseSimTime
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launch_utils import DeclareBooleanLaunchArg
from srdfdom.srdf import SRDF

SIM_TIME_ARGS = ["-p", "use_sim_time:=true"]
USE_SIM_TIME_FILE = "config/use_sim_time.yaml"


def _write_params_yaml(params):
    fd, path = tempfile.mkstemp(suffix=".yaml", prefix="moveit_params_")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        yaml.dump({"/**": {"ros__parameters": params}}, handle, default_flow_style=False)
    return path


def _launch_move_group(context, *args, **kwargs):
    moveit_config = kwargs["moveit_config"]
    use_sim_time_yaml = kwargs["use_sim_time_yaml"]

    should_publish = perform_substitutions(
        context, [LaunchConfiguration("publish_monitored_planning_scene")]
    ).lower() in ("true", "1")

    move_group_configuration = {
        "publish_robot_description_semantic": True,
        "allow_trajectory_execution": True,
        "capabilities": "",
        "disable_capabilities": "",
        "publish_planning_scene": should_publish,
        "publish_geometry_updates": should_publish,
        "publish_state_updates": should_publish,
        "publish_transforms_updates": should_publish,
        "monitor_dynamics": False,
    }

    wrapper = os.path.join(
        get_package_prefix("dual_arm_moveit_config"),
        "lib",
        "dual_arm_moveit_config",
        "run_move_group_sim_time.sh",
    )

    cmd = [wrapper]
    for params in (moveit_config.to_dict(), move_group_configuration):
        cmd.extend(["--params-file", _write_params_yaml(params)])
    cmd.extend(["--params-file", use_sim_time_yaml])

    return [ExecuteProcess(cmd=cmd, output="screen", name="move_group")]


def generate_launch_description():
    """MoveIt + RViz for Gazebo Sim (no mock ros2_control; Gazebo owns controllers)."""
    moveit_config = (
        MoveItConfigsBuilder("dual_arm", package_name="dual_arm_moveit_config")
        .to_moveit_configs()
    )
    launch_package_path = moveit_config.package_path
    use_sim_time_yaml = str(launch_package_path / USE_SIM_TIME_FILE)

    ld = LaunchDescription()
    ld.add_action(SetUseSimTime(True))
    ld.add_action(DeclareBooleanLaunchArg("db", default_value=False))
    ld.add_action(DeclareBooleanLaunchArg("debug", default_value=False))
    ld.add_action(DeclareBooleanLaunchArg("use_rviz", default_value=True))
    ld.add_action(
        DeclareBooleanLaunchArg("publish_monitored_planning_scene", default_value=True)
    )

    name_counter = 0
    for _, xml_contents in moveit_config.robot_description_semantic.items():
        srdf = SRDF.from_xml_string(xml_contents)
        for vj in srdf.virtual_joints:
            ld.add_action(
                Node(
                    package="tf2_ros",
                    executable="static_transform_publisher",
                    name=f"static_transform_publisher{name_counter}",
                    output="log",
                    parameters=[use_sim_time_yaml],
                    ros_arguments=SIM_TIME_ARGS,
                    arguments=[
                        "--frame-id",
                        vj.parent_frame,
                        "--child-frame-id",
                        vj.child_link,
                    ],
                )
            )
            name_counter += 1

    ld.add_action(
        OpaqueFunction(
            function=_launch_move_group,
            kwargs={
                "moveit_config": moveit_config,
                "use_sim_time_yaml": use_sim_time_yaml,
            },
        )
    )

    ld.add_action(
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="log",
            respawn=False,
            arguments=["-d", str(launch_package_path / "config/moveit.rviz")],
            parameters=[
                moveit_config.planning_pipelines,
                moveit_config.robot_description_kinematics,
                moveit_config.joint_limits,
                use_sim_time_yaml,
            ],
            ros_arguments=SIM_TIME_ARGS,
            condition=IfCondition(LaunchConfiguration("use_rviz")),
        )
    )

    ld.add_action(
        Node(
            package="dual_arm_moveit_config",
            executable="enable_sim_time.py",
            name="enable_sim_time",
            output="screen",
            parameters=[{"target_nodes": ["rviz2"]}],
        )
    )

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/warehouse_db.launch.py")
            ),
            condition=IfCondition(LaunchConfiguration("db")),
        )
    )

    return ld
