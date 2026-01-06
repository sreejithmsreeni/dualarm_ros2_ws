#include <memory>
#include <vector>
#include <chrono>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto const node = std::make_shared<rclcpp::Node>(
    "moveit_joint_control",
    rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true)
  );

  auto const logger = rclcpp::get_logger("moveit_joint_control");
  using moveit::planning_interface::MoveGroupInterface;

  // ⚙️  Replace with your MoveIt SRDF group name (NOT controller name)
  auto move_group = MoveGroupInterface(node, "dual_arm");

  move_group.setPlanningPipelineId("ompl");
  move_group.setPlannerId("RRTConnectkConfigDefault");
  move_group.setPlanningTime(5.0);
  move_group.setMaxVelocityScalingFactor(0.5);
  move_group.setMaxAccelerationScalingFactor(0.5);

  RCLCPP_INFO(logger, "Initialized MoveGroupInterface for group: %s", move_group.getName().c_str());

  // --Define Joint Targets ---

  // 1️⃣ Target Joint Configuration
  std::vector<double> target_joints = {

    -1.43940855,
    -0.73566565,
    -0.00832632,
    -1.6057372799999998,
    1.5477535199999999,
    0.00396912,
    0.7632139199999999,
    1.56716135,
    -0.7279901999999999,
    -5.2919999999999995e-05,
    -1.60570968,
    1.54769856,
    0.00393648,
    0.7632819599999999 , // left_joint7
  };

  // 2️⃣ Zero Joint Configuration
  // std::vector<double> zero_joints(14, 0.0);
  
  //Pick position
  std::vector<double> zero_joints(14, 0.0);

  // 3️⃣ Cycle between them
  std::vector<std::vector<double>> poses = {target_joints, zero_joints};
  size_t current_pose_index = 0;

  while (rclcpp::ok())
  {
    std::vector<double> goal = poses[current_pose_index];
    RCLCPP_INFO(logger, "Planning to move to pose %zu (%s)",
                current_pose_index + 1,
                current_pose_index == 0 ? "target_joints" : "zero_joints");
    move_group.setStartStateToCurrentState();
    move_group.setJointValueTarget(goal);

    moveit::planning_interface::MoveGroupInterface::Plan plan;
    bool success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);

    if (success)
    {
      RCLCPP_INFO(logger, "Planning succeeded! Executing...");
      move_group.execute(plan);
      RCLCPP_INFO(logger, "Reached target pose!");
    }
    else
    {
      RCLCPP_ERROR(logger, "Planning failed for this pose!");
      break;
    }

    // Switch between target ↔ zero pose
    current_pose_index =  1 - current_pose_index;

    // Wait 5 seconds before next move
    rclcpp::sleep_for(std::chrono::seconds(5));
  }

  rclcpp::shutdown();
  return 0;
}
