#!/usr/bin/env python3
"""Set and verify use_sim_time=true on MoveIt nodes."""

import subprocess
import sys

import rclpy
from rclpy.node import Node


class EnableSimTime(Node):
  def __init__(self):
    super().__init__('enable_sim_time')
    self.declare_parameter('target_nodes', ['rviz2'])
    self._targets = list(
      self.get_parameter('target_nodes').get_parameter_value().string_array_value
    )
    if not self._targets:
      self._targets = ['rviz2']
    self.get_logger().info(f'Waiting to enable use_sim_time on: {self._targets}')
    self._pending = set(self._targets)
    self._timer = self.create_timer(0.5, self._tick)
    self._attempts = 0

  def _is_sim_time_enabled(self, node_name):
    result = subprocess.run(
      ['ros2', 'param', 'get', f'/{node_name}', 'use_sim_time'],
      capture_output=True,
      text=True,
    )
    if result.returncode != 0:
      return False
    return 'True' in result.stdout

  def _enable_sim_time(self, node_name):
    subprocess.run(
      ['ros2', 'param', 'set', f'/{node_name}', 'use_sim_time', 'true'],
      capture_output=True,
      text=True,
    )
    return self._is_sim_time_enabled(node_name)

  def _tick(self):
    if not self._pending:
      self.get_logger().info('use_sim_time verified on all target nodes')
      self._timer.cancel()
      self._done = True
      return

    self._attempts += 1
    if self._attempts > 120:
      self.get_logger().error(
        f'Failed to enable use_sim_time on: {sorted(self._pending)}'
      )
      self._timer.cancel()
      self._failed = True
      return

    done = []
    for node_name in self._pending:
      if self._enable_sim_time(node_name):
        self.get_logger().info(f'verified use_sim_time=true on /{node_name}')
        done.append(node_name)

    for node_name in done:
      self._pending.remove(node_name)


def main():
  rclpy.init()
  node = EnableSimTime()
  node._done = False
  node._failed = False
  try:
    while rclpy.ok() and not node._done and not node._failed:
      rclpy.spin_once(node, timeout_sec=0.1)
  finally:
    exit_code = 1 if node._failed else 0
    node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
  main()
