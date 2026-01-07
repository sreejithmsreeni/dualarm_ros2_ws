#ifndef DUAL_ARM_DRIVER__ETHERCAT_DRIVER_WITH_ENABLE_HPP_
#define DUAL_ARM_DRIVER__ETHERCAT_DRIVER_WITH_ENABLE_HPP_

#include "ethercat_driver/ethercat_driver.hpp"
#include "ethercat_generic_plugins/generic_ec_cia402_drive.hpp"
#include <rclcpp/rclcpp.hpp>

namespace dual_arm_driver
{

class EthercatDriverWithEnable : public ethercat_driver::EthercatDriver
{
public:
  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override
  {
    auto ret = ethercat_driver::EthercatDriver::on_init(info);
    
    if (ret != hardware_interface::CallbackReturn::SUCCESS) {
      return ret;
    }
    
    // Declare parameter for motor enable
    motor_operation_enabled_ = false;
    
    return hardware_interface::CallbackReturn::SUCCESS;
  }

  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override
  {
    // Check parameter value (every N cycles for performance)
    if (read_counter_++ % 100 == 0) {
      checkParameterUpdate();
    }
    
    return ethercat_driver::EthercatDriver::read(time, period);
  }

  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override
  {
    // Apply enable flag to all CiA402 drives
    applyEnableFlagToAllDrives();
    
    return ethercat_driver::EthercatDriver::write(time, period);
  }

private:
  void checkParameterUpdate()
  {
    try {
      auto node = rclcpp::Node::make_shared("_temp_param_reader");
      auto client = std::make_shared<rclcpp::SyncParametersClient>(node, "/controller_manager");
      
      std::string param_name = info_.name + ".motor_operation_enabled";
      
      if (client->has_parameter(param_name)) {
        bool new_value = client->get_parameter<bool>(param_name);
        
        if (new_value != motor_operation_enabled_) {
          motor_operation_enabled_ = new_value;
          RCLCPP_INFO(rclcpp::get_logger("EthercatDriverWithEnable"),
                      "Motor operation: %s", 
                      motor_operation_enabled_ ? "ENABLED" : "DISABLED");
        }
      }
    } catch (const std::exception& e) {
      // Ignore errors during parameter read
    }
  }

  void applyEnableFlagToAllDrives()
  {
    // Get all slaves from base class
    for (auto & slave : ec_slaves_) {
      // Try to cast to CiA402 drive
      auto cia402_drive = std::dynamic_pointer_cast<ethercat_generic_plugins::EcCiA402Drive>(slave);
      
      if (cia402_drive) {
        cia402_drive->setOperationEnabled(motor_operation_enabled_);
      }
    }
  }

  bool motor_operation_enabled_{false};
  size_t read_counter_{0};
};

}  // namespace dual_arm_driver

#endif  // DUAL_ARM_DRIVER__ETHERCAT_DRIVER_WITH_ENABLE_HPP_
