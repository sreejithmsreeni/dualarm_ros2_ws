#!/bin/bash
# Launch move_group with use_sim_time as the last CLI argument (required on Jazzy).
set -e

PARAM_ARGS=()
while [[ $# -gt 0 ]]; do
  PARAM_ARGS+=("$1")
  shift
done

exec ros2 run moveit_ros_move_group move_group --ros-args \
  -r __node:=move_group \
  "${PARAM_ARGS[@]}" \
  -p use_sim_time:=true
