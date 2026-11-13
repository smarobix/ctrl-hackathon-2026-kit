#!/usr/bin/env python3
"""Writes a Doosan M1013 xacro macro that can be mounted on another robot.

Doosan's description names the arm's links base_link, link_1 ... link_6, which clashes with
the Husky's own base_link, and brings its own Gazebo ros2_control plugin, which clashes with
Clearpath's. This script takes the links and joints from Doosan's macro unchanged (masses,
inertias, meshes, limits), prefixes their names, hangs the arm on a parent link and adds a
ros2_control block for the Gazebo plugin the Husky already loads.

usage: make_m1013_macro.py <dsr_description2 share directory> <output .xacro>
"""
import sys
import xml.etree.ElementTree as ET

XACRO = "http://www.ros.org/wiki/xacro"
ET.register_namespace("xacro", XACRO)

# Joint positions the arm starts in: upper arm up, forearm forward, tool pointing down.
START = [0.0, 0.0, 1.5708, 0.0, 1.5708, 0.0]
PREFIX = "${prefix}"

share, out = sys.argv[1], sys.argv[2]
macro = ET.parse(f"{share}/xacro/macro.m1013.white.xacro").getroot().find(f"{{{XACRO}}}macro")
links = [e for e in macro if e.tag == "link"]
joints = [e for e in macro if e.tag == "joint"]
if len(links) != 7 or len(joints) != 6:
    sys.exit(f"unexpected Doosan description: {len(links)} links, {len(joints)} joints")

for link in links:
    link.set("name", PREFIX + link.get("name"))
for joint in joints:
    joint.set("name", PREFIX + joint.get("name"))
    for end in ("parent", "child"):
        joint.find(end).set("link", PREFIX + joint.find(end).get("link"))

robot = ET.Element("robot")
out_macro = ET.SubElement(robot, f"{{{XACRO}}}macro", name="doosan_m1013",
                          params="prefix parent_link *origin")
mount = ET.SubElement(out_macro, "joint", name=PREFIX + "mount_joint", type="fixed")
ET.SubElement(mount, f"{{{XACRO}}}insert_block", name="origin")
ET.SubElement(mount, "parent", link="${parent_link}")
ET.SubElement(mount, "child", link=PREFIX + "base_link")
out_macro.extend(links + joints)

control = ET.SubElement(out_macro, "ros2_control", name=PREFIX + "m1013", type="system")
ET.SubElement(ET.SubElement(control, "hardware"), "plugin").text = "ign_ros2_control/IgnitionSystem"
for joint, start in zip(joints, START):
    limit = joint.find("limit")
    entry = ET.SubElement(control, "joint", name=joint.get("name"))
    command = ET.SubElement(entry, "command_interface", name="position")
    ET.SubElement(command, "param", name="min").text = limit.get("lower")
    ET.SubElement(command, "param", name="max").text = limit.get("upper")
    position = ET.SubElement(entry, "state_interface", name="position")
    ET.SubElement(position, "param", name="initial_value").text = str(start)
    ET.SubElement(entry, "state_interface", name="velocity")

ET.indent(robot)
with open(out, "w") as f:
    f.write('<?xml version="1.0"?>\n<!-- Generated from Doosan\'s dsr_description2 by make_m1013_macro.py. -->\n')
    f.write(ET.tostring(robot, encoding="unicode"))
    f.write("\n")
print(f"wrote {out}: {len(links)} links, {len(joints)} joints")
