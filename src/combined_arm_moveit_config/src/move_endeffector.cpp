#include <memory>
#include <thread>
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <moveit/move_group_interface/move_group_interface.h>

int main(int argc, char* argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("dual_cartesian_demo",
    rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));

  using moveit::planning_interface::MoveGroupInterface;

  // Create MoveGroup interfaces for each arm
  MoveGroupInterface left_group(node, "left_arm");
  MoveGroupInterface right_group(node, "right_arm");

  // left_group.setEndEffectorLink("left_ttt");
  // right_group.setEndEffectorLink("right_ttt");


  // Optional: set end-effector link if not the group default
  // left_group.setEndEffectorLink("left_ee_link");
  // right_group.setEndEffectorLink("right_ee_link");

  // Configure planners for both arms
  auto configure = [](MoveGroupInterface& g) {
    g.setPlanningPipelineId("ompl");
    g.setPlannerId("RRTConnectkConfigDefault");
    g.setPlanningTime(5.0);
    g.setMaxVelocityScalingFactor(1.0);
    g.setMaxAccelerationScalingFactor(0.5);
  };
  configure(left_group);
  configure(right_group);

  // Set target pose for right arm
  geometry_msgs::msg::Pose right_pose;
  right_pose.position.x = -0.209093;  // meters
  right_pose.position.y = -0.410526;
  right_pose.position.z = -1.195594;
  right_pose.orientation.x =  0.394457;
  right_pose.orientation.y =  0.726872;
  right_pose.orientation.z = -0.277493;
  right_pose.orientation.w =  0.488935;

  // Set target pose for left arm
  geometry_msgs::msg::Pose left_pose;
  left_pose.position.x = 0.273097;
  left_pose.position.y = -0.338380;
  left_pose.position.z = -1.195761;
  left_pose.orientation.x =  0.701233;
  left_pose.orientation.y =  0.334995;
  left_pose.orientation.z = -0.628506;
  left_pose.orientation.w = -0.032106;


  // Set pose targets
  left_group.setPoseTarget(left_pose);
  right_group.setPoseTarget(right_pose);

  // Plan for each arm
  MoveGroupInterface::Plan left_plan;
  MoveGroupInterface::Plan right_plan;
  bool left_ok = (left_group.plan(left_plan) == moveit::core::MoveItErrorCode::SUCCESS);
  bool right_ok = (right_group.plan(right_plan) == moveit::core::MoveItErrorCode::SUCCESS);

  if (!left_ok || !right_ok) {
    RCLCPP_ERROR(node->get_logger(),
      "Planning failed: left_ok=%d, right_ok=%d", left_ok, right_ok);
    rclcpp::shutdown();
    return 1;
  }

  // Execute both arms' plans in parallel threads for synchronous movement
  std::thread t_left([&]() {
    left_group.execute(left_plan);
  });
  std::thread t_right([&]() {
    right_group.execute(right_plan);
  });

  t_left.join();
  t_right.join();

  RCLCPP_INFO(node->get_logger(), "Both arms reached Cartesian targets!");
  rclcpp::shutdown();
  return 0;
}

