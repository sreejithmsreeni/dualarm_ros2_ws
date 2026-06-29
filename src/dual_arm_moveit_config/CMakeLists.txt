cmake_minimum_required(VERSION 3.22)
project(dual_arm_moveit_config)

find_package(ament_cmake REQUIRED)

install(PROGRAMS
  scripts/enable_sim_time.py
  scripts/run_move_group_sim_time.sh
  DESTINATION lib/${PROJECT_NAME})

ament_package()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/launch")
  install(
    DIRECTORY launch
    DESTINATION share/${PROJECT_NAME}
    PATTERN "setup_assistant.launch" EXCLUDE)
endif()

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})
