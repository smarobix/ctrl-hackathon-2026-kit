#!/usr/bin/env python3
"""A ROS 2 node that reads the robot's low-level state and prints a summary once a second.

The robot publishes rt/lowstate on Unitree's DDS; ROS 2 sees it as /lowstate, typed with the
message packages from unitree_ros2 (unitree_go for the Go2, unitree_hg for the G1). Works the
same against the simulation and the real robot. A starting point, not a solution.

    python3 watch_lowstate.py go2      or      python3 watch_lowstate.py g1
"""
import math
import sys

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

ROBOT = sys.argv[1] if len(sys.argv) > 1 else "go2"
if ROBOT == "go2":
    from unitree_go.msg import LowState
else:
    from unitree_hg.msg import LowState


class WatchLowState(Node):
    def __init__(self):
        super().__init__("watch_lowstate")
        self.count = 0
        self.last = None
        self.create_subscription(LowState, "lowstate", self.on_state, 10)
        self.create_timer(1.0, self.report)

    def on_state(self, msg):
        self.count += 1
        self.last = msg

    def report(self):
        if self.last is None:
            self.get_logger().info("waiting for /lowstate")
            return
        imu = self.last.imu_state
        # The simulations fill the IMU's quaternion and accelerometer, not its rpy field.
        quaternion = " ".join(f"{v:+.2f}" for v in imu.quaternion)
        gravity = math.sqrt(sum(a * a for a in imu.accelerometer))
        joints = " ".join(f"{m.q:+.2f}" for m in self.last.motor_state[:6])
        self.get_logger().info(
            f"{self.count} msg/s  imu quaternion [{quaternion}] |acc| {gravity:.1f} m/s2  "
            f"first joints [rad] {joints}")
        self.count = 0


def main():
    rclpy.init()
    try:
        rclpy.spin(WatchLowState())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
