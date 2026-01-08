#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <memory>
#include <chrono>

class MotorEnableService : public rclcpp::Node
{
public:
  MotorEnableService() : Node("motor_enable_service")
  {
    // Create parameter client
    param_client_ = std::make_shared<rclcpp::AsyncParametersClient>(
      this, "/controller_manager");
    
    // Wait for service (in a separate thread to not block startup)
    init_thread_ = std::thread([this]() {
      while (!param_client_->wait_for_service(std::chrono::seconds(1))) {
        if (!rclcpp::ok()) return;
        RCLCPP_INFO(this->get_logger(), "Waiting for controller_manager...");
      }
      RCLCPP_INFO(this->get_logger(), "Controller manager connected.");
    });
    
    // Create services
    enable_service_ = this->create_service<std_srvs::srv::Trigger>(
      "enable_motors",
      std::bind(&MotorEnableService::handleEnable, this,
                std::placeholders::_1, std::placeholders::_2));
    
    disable_service_ = this->create_service<std_srvs::srv::Trigger>(
      "disable_motors",
      std::bind(&MotorEnableService::handleDisable, this,
                std::placeholders::_1, std::placeholders::_2));
    
    RCLCPP_INFO(this->get_logger(), "Motor enable service ready.");
  }
  
  ~MotorEnableService() {
    if (init_thread_.joinable()) init_thread_.join();
  }

private:
  void handleEnable(
    const std::shared_ptr<std_srvs::srv::Trigger::Request>,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    RCLCPP_INFO(this->get_logger(), "Enabling motors...");
    
    // NON-BLOCKING call - don't use spin_until_future_complete here!
    auto future = param_client_->set_parameters({
      rclcpp::Parameter("motor_operation_enabled", true)
    });
    
    // Wait for result with a timeout manually (safe inside callback)
    // Note: This is a simple blocking wait on the future, NOT spinning the node
    auto status = future.wait_for(std::chrono::seconds(2));
    
    if (status == std::future_status::ready) {
      auto result = future.get();
      if (!result.empty() && result[0].successful) {
        response->success = true;
        response->message = "Motors enabled (Parameter set)";
        RCLCPP_INFO(this->get_logger(), "✓ Parameter set successfully");
      } else {
        response->success = false;
        response->message = "Failed to set parameter";
      }
    } else {
      response->success = false;
      response->message = "Timeout setting parameter";
    }
  }

  void handleDisable(
    const std::shared_ptr<std_srvs::srv::Trigger::Request>,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    RCLCPP_INFO(this->get_logger(), "Disabling motors...");
    
    auto future = param_client_->set_parameters({
      rclcpp::Parameter("motor_operation_enabled", false)
    });
    
    auto status = future.wait_for(std::chrono::seconds(2));
    
    if (status == std::future_status::ready) {
      auto result = future.get();
      if (!result.empty() && result[0].successful) {
        response->success = true;
        response->message = "Motors disabled (Parameter set)";
        RCLCPP_INFO(this->get_logger(), "✓ Parameter set successfully");
      } else {
        response->success = false;
        response->message = "Failed to set parameter";
      }
    } else {
      response->success = false;
      response->message = "Timeout setting parameter";
    }
  }

  std::shared_ptr<rclcpp::AsyncParametersClient> param_client_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr enable_service_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr disable_service_;
  std::thread init_thread_;
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MotorEnableService>();
  // MultiThreadedExecutor is safer for service-within-service calls
  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  executor.spin();
  rclcpp::shutdown();
  return 0;
}
