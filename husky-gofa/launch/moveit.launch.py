"""MoveIt's move_group for the GoFa on the Husky, in the robot's namespace.

The robot description is the one Clearpath generated for the running simulation. The semantic
description is written here: one planning group, arm_0, from the arm's base to its flange, and
collision checks switched off where they can never matter (the Husky's parts among themselves,
the arm's base and first link against the Husky, arm links that never touch).
"""
import itertools
import os
import xml.etree.ElementTree as ET

import xacro
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

ARM = "arm_0_"
ARM_JOINTS = [f"{ARM}joint_{i}" for i in range(1, 7)]
POSES = {
    "home": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "ready": [0.0, 0.0, 0.6, 0.0, 0.9708, 0.0],
    "reach_front": [0.0, 0.9, 0.6, 0.0, 0.0708, 0.0],
}
# Arm link pairs that never touch: neighbours, and pairs MoveIt's collisions_updater found never in
# contact over 10000 random poses of the arm alone.
ARM_PAIRS = [("base_link", "link_1"), ("base_link", "link_3"), ("link_1", "link_2"),
             ("link_1", "link_3"), ("link_1", "link_4"), ("link_2", "link_3"),
             ("link_3", "link_4"), ("link_3", "link_5"), ("link_3", "link_6"),
             ("link_4", "link_5"), ("link_5", "link_6")]


def semantic_description(urdf: str, robot_name: str) -> str:
    links = [l.get("name") for l in ET.fromstring(urdf).findall("link") if l.find("collision") is not None]
    platform = [l for l in links if not l.startswith(ARM)]
    srdf = ET.Element("robot", name=robot_name)
    group = ET.SubElement(srdf, "group", name="arm_0")
    ET.SubElement(group, "chain", base_link=f"{ARM}base_link", tip_link=f"{ARM}link_6")
    for pose, values in POSES.items():
        state = ET.SubElement(srdf, "group_state", name=pose, group="arm_0")
        for joint, value in zip(ARM_JOINTS, values):
            ET.SubElement(state, "joint", name=joint, value=str(value))
    pairs = list(itertools.combinations(platform, 2))
    pairs += [(f"{ARM}{a}", p) for a in ("base_link", "link_1") for p in platform]
    pairs += [(f"{ARM}{a}", f"{ARM}{b}") for a, b in ARM_PAIRS]
    for a, b in pairs:
        ET.SubElement(srdf, "disable_collisions", link1=a, link2=b, reason="Never")
    return ET.tostring(srdf, encoding="unicode")


def launch_setup(context):
    setup_path = LaunchConfiguration("setup_path").perform(context)
    namespace = LaunchConfiguration("namespace").perform(context)
    urdf = xacro.process_file(os.path.join(setup_path, "robot.urdf.xacro")).toxml()
    robot_name = ET.fromstring(urdf).get("name")
    return [Node(
        package="moveit_ros_move_group",
        executable="move_group",
        namespace=namespace,
        output="log",
        parameters=[
            "/opt/kit/config/moveit.yaml",
            {"robot_description": urdf,
             "robot_description_semantic": semantic_description(urdf, robot_name),
             "use_sim_time": True},
        ],
        remappings=[("/tf", "tf"), ("/tf_static", "tf_static"),
                    ("joint_states", "platform/joint_states")],
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("setup_path", default_value="/root/clearpath"),
        DeclareLaunchArgument("namespace", default_value="a200_0000"),
        OpaqueFunction(function=launch_setup),
    ])
