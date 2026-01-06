cmake_minimum_required(VERSION 3.8)
project(dual_arm_driver)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(ethercat_msgs REQUIRED)

install(
  DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

install(
  DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(
    PROGRAMS scripts/move_trajectory_node.py
    DESTINATION lib/${PROJECT_NAME} 
)


install(
  DIRECTORY urdf/
  DESTINATION share/${PROJECT_NAME}/urdf
)
ament_package()
