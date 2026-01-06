cmake_minimum_required(VERSION 3.8)
project(dual_arm_description)

# Default C++ standard
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find necessary build tools
find_package(ament_cmake REQUIRED)
find_package(xacro REQUIRED)

# Install the directories containing your robot description files
install(
  DIRECTORY urdf meshes
  DESTINATION share/${PROJECT_NAME}
)

# Register the package with ament
ament_package()
