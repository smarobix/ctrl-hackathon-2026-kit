#!/usr/bin/env python3
"""Drives the Husky forward for two seconds, then moves the arm to two poses and back.

Plain ROS 2, no MoveIt: velocity commands on the Husky's cmd_vel and a trajectory goal for the
arm's joint trajectory controller. A starting point, not a solution.

    python3 drive_and_reach.py
"""
import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import Twist
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint

NS = "/a200_0000"
JOINTS = [f"arm_0_joint_{i}" for i in range(1, 7)]
READY = [0.0, 0.0, 1.5708, 0.0, 1.5708, 0.0]
REACH = [0.0, 0.7854, 1.5708, 0.0, 0.7854, 0.0]
SIDE = [1.5708, 0.3, 1.8, 0.0, 1.0, 0.0]


class DriveAndReach(Node):
    def __init__(self):
        super().__init__("drive_and_reach")
        self.cmd_vel = self.create_publisher(Twist, f"{NS}/cmd_vel", 10)
        self.arm = ActionClient(self, FollowJointTrajectory,
                                f"{NS}/arm_0_joint_trajectory_controller/follow_joint_trajectory")

    def drive(self, speed: float, seconds: float):
        twist = Twist()
        twist.linear.x = speed
        end = self.get_clock().now().nanoseconds + int(seconds * 1e9)
        while self.get_clock().now().nanoseconds < end:
            self.cmd_vel.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.05)
        self.cmd_vel.publish(Twist())

    def move_arm(self, poses, seconds_each: float = 3.0):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINTS
        for i, pose in enumerate(poses, start=1):
            t = seconds_each * i
            goal.trajectory.points.append(JointTrajectoryPoint(
                positions=pose, time_from_start=Duration(sec=int(t), nanosec=int((t % 1) * 1e9))))
        if not self.arm.wait_for_server(timeout_sec=10.0):
            raise RuntimeError("the arm's trajectory controller is not running")
        sent = self.arm.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, sent)
        result = sent.result().get_result_async()
        rclpy.spin_until_future_complete(self, result)
        return result.result().result.error_code


def main():
    rclpy.init()
    node = DriveAndReach()
    node.get_logger().info("driving forward")
    node.drive(0.4, 2.0)
    node.get_logger().info("moving the arm")
    code = node.move_arm([REACH, SIDE, READY])
    node.get_logger().info(f"arm done, error code {code} (0 is success)")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
