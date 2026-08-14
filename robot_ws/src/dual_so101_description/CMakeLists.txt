cmake_minimum_required(VERSION 3.16)
project(dual_so101_description)
find_package(ament_cmake REQUIRED)
install(DIRECTORY urdf config DESTINATION share/${PROJECT_NAME})
ament_package()

