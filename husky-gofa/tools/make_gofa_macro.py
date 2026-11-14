#!/usr/bin/env python3
"""Writes an ABB GoFa CRB 15000-12/1.27 xacro macro that can be mounted on another robot.

The arm's links, joints and meshes come from ROS-Industrial's abb_crb15000_support unchanged:
names, kinematics, joint limits and velocities. That description is made for RViz and MoveIt,
so this script adds what Gazebo needs:

- Masses and inertias. ABB gives the arm's weight (48 kg), not the links', so the 48 kg are
  shared out over the links by hand and each link is taken as a solid box the size of its
  collision mesh. Estimates, good enough to drive the arm in simulation.
- Joint effort limits. The package has 0, which Gazebo reads as "cannot move". The values here
  are estimates, large enough to hold the arm stretched out with a 12 kg load.
- A ros2_control block for the Gazebo plugin the Husky already loads, and a fixed joint that
  hangs the arm on a parent link.

Mesh paths become file:// paths and ABB's colour macros are written out, so the package does not
have to be built for ROS 2.

usage: make_gofa_macro.py <folder with abb_crb15000_support and abb_resources> <output .xacro>
"""
import struct
import sys
import xml.etree.ElementTree as ET

XACRO = "http://ros.org/wiki/xacro"
ET.register_namespace("xacro", XACRO)
PACKAGE = "package://abb_crb15000_support/"

# Joint positions the arm starts in: upper arm up, forearm tilted down, tool pointing down.
START = [0.0, 0.0, 0.6, 0.0, 0.9708, 0.0]
# Estimated link masses in kg, adding up to ABB's 48 kg for the CRB 15000-12/1.27.
MASS = {"base_link": 6.0, "link_1": 9.0, "link_2": 13.0, "link_3": 6.0,
        "link_4": 8.0, "link_5": 4.0, "link_6": 2.0}
# Estimated joint torque limits in Nm.
EFFORT = {"joint_1": 300, "joint_2": 500, "joint_3": 250,
          "joint_4": 80, "joint_5": 80, "joint_6": 40}

folder, out = sys.argv[1], sys.argv[2]
support = f"{folder}/abb_crb15000_support"
macro = ET.parse(f"{support}/urdf/crb15000_12_127_macro.xacro").getroot().find(f"{{{XACRO}}}macro")
colours = {p.get("name"): p.get("value")
           for p in ET.parse(f"{folder}/abb_resources/urdf/common_colours.xacro").getroot()
           if p.tag == f"{{{XACRO}}}property"}

links = [e for e in macro if e.tag == "link"]
joints = [e for e in macro if e.tag == "joint"]
arm_joints = [j for j in joints if j.get("type") == "revolute"]
if len(arm_joints) != 6:
    sys.exit(f"unexpected ABB description: {len(arm_joints)} arm joints")


def short(name):
    return name.replace("${prefix}", "")


def mesh_box(path):
    """Bounding box (low and high corners) of a binary STL file."""
    data = open(path, "rb").read()
    count = struct.unpack_from("<I", data, 80)[0]
    low, high = [float("inf")] * 3, [float("-inf")] * 3
    for i in range(count):
        values = struct.unpack_from("<12f", data, 84 + 50 * i)
        for vertex in (values[3:6], values[6:9], values[9:12]):
            low = [min(a, b) for a, b in zip(low, vertex)]
            high = [max(a, b) for a, b in zip(high, vertex)]
    return low, high


for link in links:
    for visual in link.findall("visual"):
        for i, child in enumerate(list(visual)):
            if child.tag.startswith(f"{{{XACRO}}}material_"):
                name = child.tag.split("material_", 1)[1]
                material = ET.Element("material", name=name)
                ET.SubElement(material, "color", rgba=colours[f"colour_{name}"])
                visual.remove(child)
                visual.insert(i, material)
    for mesh in link.iter("mesh"):
        mesh.set("filename", mesh.get("filename").replace(PACKAGE, f"file://{support}/"))
    collision = link.find("collision/geometry/mesh")
    if collision is None:
        continue
    low, high = mesh_box(collision.get("filename").removeprefix("file://"))
    size = [h - l for l, h in zip(low, high)]
    mass = MASS[short(link.get("name"))]
    inertial = ET.Element("inertial")
    ET.SubElement(inertial, "origin", xyz=" ".join(f"{(l + h) / 2:.4f}" for l, h in zip(low, high)),
                  rpy="0 0 0")
    ET.SubElement(inertial, "mass", value=f"{mass}")
    x, y, z = (s * s for s in size)
    ET.SubElement(inertial, "inertia", ixx=f"{mass * (y + z) / 12:.5f}", iyy=f"{mass * (x + z) / 12:.5f}",
                  izz=f"{mass * (x + y) / 12:.5f}", ixy="0", ixz="0", iyz="0")
    link.insert(0, inertial)

for joint in arm_joints:
    joint.find("limit").set("effort", str(EFFORT[short(joint.get("name"))]))

robot = ET.Element("robot")
out_macro = ET.SubElement(robot, f"{{{XACRO}}}macro", name="abb_gofa_12_127",
                          params="prefix parent_link *origin")
mount = ET.SubElement(out_macro, "joint", name="${prefix}mount_joint", type="fixed")
ET.SubElement(mount, f"{{{XACRO}}}insert_block", name="origin")
ET.SubElement(mount, "parent", link="${parent_link}")
ET.SubElement(mount, "child", link="${prefix}base_link")
out_macro.extend(links + joints)

control = ET.SubElement(out_macro, "ros2_control", name="${prefix}gofa", type="system")
ET.SubElement(ET.SubElement(control, "hardware"), "plugin").text = "ign_ros2_control/IgnitionSystem"
for joint, start in zip(arm_joints, START):
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
    f.write('<?xml version="1.0"?>\n<!-- Generated from ROS-Industrial\'s abb_crb15000_support '
            'by make_gofa_macro.py. -->\n')
    f.write(ET.tostring(robot, encoding="unicode"))
    f.write("\n")
print(f"wrote {out}: {len(links)} links, {len(joints)} joints")
