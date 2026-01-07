#include "dual_arm_driver/ethercat_driver_with_enable.hpp"
#include <pluginlib/class_list_macros.hpp>

PLUGINLIB_EXPORT_CLASS(
  dual_arm_driver::EthercatDriverWithEnable,
  hardware_interface::SystemInterface)
