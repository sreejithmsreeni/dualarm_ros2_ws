#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import time

class MoveTrajectoryNode(Node):
    """
    A ROS2 node that continuously publishes alternating joint trajectories
    to move a 7-DOF robot between two predefined positions.
    """
    def __init__(self):
        super().__init__('move_trajectory_node')
        # Define the joint names for the robot
        self.joint_names = ['Joint1', 'Joint2', 'Joint3', 'Joint4', 'Joint5', 'Joint6', 'Joint7']
        
        # Create a publisher for the joint trajectory topic
        self.trajectory_publisher = self.create_publisher(
            JointTrajectory,
            '/trajectory_controller/joint_trajectory',
            10
        )
        self.get_logger().info('Move Trajectory Node has started.')

    def send_trajectory(self, positions):
        """
        Builds and publishes a JointTrajectory message to a target set of positions.
        """
        trajectory_msg = JointTrajectory()
        trajectory_msg.header.frame_id = 'base_link'
        trajectory_msg.joint_names = self.joint_names

        # Create a trajectory point
        point = JointTrajectoryPoint()
        point.positions = positions
        point.velocities = [0.0] * len(self.joint_names)
        point.accelerations = [0.0] * len(self.joint_names)
        point.time_from_start.sec = 2  # Time to reach the target

        trajectory_msg.points.append(point)
        self.trajectory_publisher.publish(trajectory_msg)
        self.get_logger().info(f'Publishing trajectory to positions: {positions}')

    def run_loop(self):
        """
        Main loop to alternate between two target positions.
        """
        # Define the two target positions
        position_1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        position_2 = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3] # Example second position

        # Wait a moment for everything to initialize
        time.sleep(2.0)

        while rclpy.ok():
            # Send to position 1
            self.send_trajectory(position_1)
            time.sleep(6.0)  # Wait for 2s to move and 2s to hold

            # Send to position 2
            self.send_trajectory(position_2)
            time.sleep(6.0)  # Wait for 2s to move and 2s to hold

def main(args=None):
    rclpy.init(args=args)
    move_trajectory_node = MoveTrajectoryNode()
    
    try:
        move_trajectory_node.run_loop()
    except KeyboardInterrupt:
        pass
    finally:
        move_trajectory_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

