#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <fstream>

class MotorEnableService : public rclcpp::Node
{
public:
  MotorEnableService() : Node("motor_enable_service")
  {
    enable_service_ = this->create_service<std_srvs::srv::Trigger>(
      "enable_motors",
      std::bind(&MotorEnableService::handleEnable, this,
                std::placeholders::_1, std::placeholders::_2));
    
    disable_service_ = this->create_service<std_srvs::srv::Trigger>(
      "disable_motors",
      std::bind(&MotorEnableService::handleDisable, this,
                std::placeholders::_1, std::placeholders::_2));
    
    // Initialize file to disabled
    writeState(false);
    
    RCLCPP_INFO(this->get_logger(), "Motor enable service ready.");
  }

private:
  void handleEnable(
    const std::shared_ptr<std_srvs::srv::Trigger::Request>,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    RCLCPP_INFO(this->get_logger(), "Enabling motors...");
    writeState(true);
    response->success = true;
    response->message = "Motors enabled";
    RCLCPP_INFO(this->get_logger(), "✓ Motors enabled");
  }

  void handleDisable(
    const std::shared_ptr<std_srvs::srv::Trigger::Request>,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    RCLCPP_INFO(this->get_logger(), "Disabling motors...");
    writeState(false);
    response->success = true;
    response->message = "Motors disabled";
    RCLCPP_INFO(this->get_logger(), "✓ Motors disabled");
  }

  void writeState(bool enabled) {
    std::ofstream file("/tmp/motor_enable_state");
    file << (enabled ? "1" : "0");
    file.close();
  }

  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr enable_service_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr disable_service_;
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MotorEnableService>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
