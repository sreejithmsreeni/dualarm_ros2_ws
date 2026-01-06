cmake_minimum_required(VERSION 3.22)
project(combined_arm_moveit_config)

find_package(ament_cmake REQUIRED)

ament_package()

find_package(ament_cmake REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(moveit_visual_tools REQUIRED)
find_package(rclcpp REQUIRED)


install(DIRECTORY config DESTINATION share/${PROJECT_NAME})

install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

add_executable(trajectory_move src/trajectory_move.cpp)
ament_target_dependencies(
  trajectory_move
  "moveit_msgs"
  "moveit_ros_planning_interface"
  "moveit_visual_tools"
  "rclcpp"
)
install(TARGETS trajectory_move DESTINATION lib/${PROJECT_NAME})


add_executable(move_endeffector src/move_endeffector.cpp)
ament_target_dependencies(
  move_endeffector
  "moveit_msgs"
  "moveit_ros_planning_interface"
  "moveit_visual_tools"
  "rclcpp"
)
install(TARGETS move_endeffector DESTINATION lib/${PROJECT_NAME})


install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})



add_executable(named_trajectory_move src/named_trajectory_move.cpp)
ament_target_dependencies(
  named_trajectory_move
  "moveit_msgs"
  "moveit_ros_planning_interface"
  "moveit_visual_tools"
  "rclcpp"
)
install(TARGETS named_trajectory_move DESTINATION lib/${PROJECT_NAME})

