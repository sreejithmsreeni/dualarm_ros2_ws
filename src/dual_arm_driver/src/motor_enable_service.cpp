#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <memory>
#include <chrono>

class MotorEnableService : public rclcpp::Node
{
public:
  MotorEnableService() : Node("motor_enable_service")
  {
    // Create parameter client for controller_manager
    param_client_ = std::make_shared<rclcpp::AsyncParametersClient>(
      this, "/controller_manager");
    
    // Wait for controller_manager
    while (!param_client_->wait_for_service(std::chrono::seconds(1))) {
      if (!rclcpp::ok()) {
        RCLCPP_ERROR(this->get_logger(), "Interrupted waiting for controller_manager");
        return;
      }
      RCLCPP_INFO(this->get_logger(), "Waiting for controller_manager...");
    }
    
    // Create services
    enable_service_ = this->create_service<std_srvs::srv::Trigger>(
      "enable_motors",
      std::bind(&MotorEnableService::handleEnable, this,
                std::placeholders::_1, std::placeholders::_2));
    
    disable_service_ = this->create_service<std_srvs::srv::Trigger>(
      "disable_motors",
      std::bind(&MotorEnableService::handleDisable, this,
                std::placeholders::_1, std::placeholders::_2));
    
    RCLCPP_INFO(this->get_logger(), 
                "Motor enable service ready. Motors in SWITCH_ON state.");
    RCLCPP_INFO(this->get_logger(),
                "Enable: ros2 service call /enable_motors std_srvs/srv/Trigger");
  }

private:
  void handleEnable(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;
    
    RCLCPP_INFO(this->get_logger(), "Enabling motors...");
    
    auto results = param_client_->set_parameters({
      rclcpp::Parameter("motor_operation_enabled", true)
    });
    
    if (rclcpp::spin_until_future_complete(
          this->get_node_base_interface(),
          results,
          std::chrono::seconds(1)) == rclcpp::FutureReturnCode::SUCCESS)
    {
      auto result = results.get();
      if (!result.empty() && result[0].successful) {
        response->success = true;
        response->message = "Motors transitioning to OPERATION ENABLED";
        RCLCPP_INFO(this->get_logger(), "✓ Motors enabled");
      } else {
        response->success = false;
        response->message = "Failed to set parameter";
        RCLCPP_ERROR(this->get_logger(), "Failed to enable motors");
      }
    } else {
      response->success = false;
      response->message = "Service timeout";
    }
  }

  void handleDisable(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;
    
    RCLCPP_INFO(this->get_logger(), "Disabling motors...");
    
    auto results = param_client_->set_parameters({
      rclcpp::Parameter("motor_operation_enabled", false)
    });
    
    if (rclcpp::spin_until_future_complete(
          this->get_node_base_interface(),
          results,
          std::chrono::seconds(1)) == rclcpp::FutureReturnCode::SUCCESS)
    {
      auto result = results.get();
      if (!result.empty() && result[0].successful) {
        response->success = true;
        response->message = "Motors returning to SWITCH_ON state";
        RCLCPP_INFO(this->get_logger(), "✓ Motors disabled");
      } else {
        response->success = false;
        response->message = "Failed to set parameter";
      }
    } else {
      response->success = false;
      response->message = "Service timeout";
    }
  }

  std::shared_ptr<rclcpp::AsyncParametersClient> param_client_;
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
