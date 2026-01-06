#include <memory>
#include <vector>
#include <chrono>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto const node = std::make_shared<rclcpp::Node>(
    "moveit_control",
    rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true)
  );

  auto const logger = rclcpp::get_logger("moveit_control");
  using moveit::planning_interface::MoveGroupInterface;
  
  // NOTE: This should be your SRDF planning group name (e.g., "dual_arm").
  // Using a controller name here is unconventional but kept as per your confirmation.
  auto arm_group_interface = MoveGroupInterface(node, "dual_arm");

  // --- Configuration ---
  arm_group_interface.setPlanningPipelineId("ompl");
  arm_group_interface.setPlannerId("RRTConnectkConfigDefault");
  arm_group_interface.setPlanningTime(5.0);
  
  // Set velocity and acceleration scaling factors
  arm_group_interface.setMaxVelocityScalingFactor(0.1);
  arm_group_interface.setMaxAccelerationScalingFactor(0.1); 

  // Log settings
  RCLCPP_INFO(logger, "Planning pipeline: %s", arm_group_interface.getPlanningPipelineId().c_str());
  RCLCPP_INFO(logger, "Planner ID: %s", arm_group_interface.getPlannerId().c_str());
  RCLCPP_INFO(logger, "Max acceleration scaling: %.2f", arm_group_interface.getMaxAccelerationScalingFactor());

  // --- Main Loop for Pose Cycling ---
  
  // 1. Define the named poses to cycle through
  std::vector<std::string> pose_names = {"grasp_pose", "release_pose"};
  size_t current_pose_index = 0;

  // 2. Loop until Ctrl+C is pressed
  while (rclcpp::ok())
  {
    // Select the next target pose
    std::string target_pose = pose_names[current_pose_index];
    RCLCPP_INFO(logger, "Planning to move to pose: '%s'", target_pose.c_str());

    // Set the named target
    arm_group_interface.setNamedTarget(target_pose);

    // Plan to the named pose
    auto const [success, plan] = [&arm_group_interface] {
      
      
      moveit::planning_interface::MoveGroupInterface::Plan msg;
      auto const ok = static_cast<bool>(arm_group_interface.plan(msg));
      return std::make_pair(ok, msg);
    }();

    // Execute if planning succeeded
    if (success)
    {
      RCLCPP_INFO(logger, "Planning succeeded! Executing...");
      rclcpp::sleep_for(std::chrono::seconds(1));
      arm_group_interface.execute(plan);
      RCLCPP_INFO(logger, "Reached pose: '%s'", target_pose.c_str());
    }
    else
    {
      RCLCPP_ERROR(logger, "Planning failed for pose: '%s'. Stopping.", target_pose.c_str());
      break; // Exit the loop if planning fails
    }

    // Switch to the other pose for the next iteration
    current_pose_index = 1 - current_pose_index;

    // Wait for a second before starting the next move
    rclcpp::sleep_for(std::chrono::seconds(5));
  }

  rclcpp::shutdown();
  return 0;
}
