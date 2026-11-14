# Husky A200 with an ABB GoFa CRB 15000-12/1.27

A Clearpath Husky A200 with an ABB GoFa CRB 15000-12/1.27 (12 kg, 1.27 m reach) on its top plate,
in Gazebo, on ROS 2 Humble. The Husky comes from Clearpath's simulator. The arm comes from
ROS-Industrial's description package ([abb_crb15000_support](https://github.com/ros-industrial/abb/tree/noetic-devel/abb_crb15000_support))
and has a joint trajectory controller and MoveIt. Runs without a GPU.

## Start

```bash
docker compose up --build -d          # first build: about 10 minutes
```

Open <http://localhost:6080/vnc.html> and click *Connect*. Gazebo starts first. About two minutes
later, RViz opens with MoveIt's *MotionPlanning* panel. Pick a goal state for `arm_0` and press
*Plan & Execute*. Progress: `docker logs -f husky-gofa`; details in `/tmp/*.log` in the container.

Stop with `docker compose down`.

## Use it from ROS 2

Inside the container:

```bash
docker exec -it husky-gofa bash
python3 /root/examples/drive_and_reach.py     # drives 0.8 m, then moves the arm
```

From ROS 2 Humble on your laptop, set `ROS_LOCALHOST_ONLY=1` first (the simulation keeps its
traffic on loopback):

```bash
export ROS_LOCALHOST_ONLY=1
ros2 topic list | grep a200_0000
```

| What | Name | Type |
|---|---|---|
| Drive | `/a200_0000/cmd_vel` | `geometry_msgs/Twist` |
| Odometry | `/a200_0000/platform/odom/filtered` | `nav_msgs/Odometry` |
| Joint states (wheels and arm) | `/a200_0000/platform/joint_states` | `sensor_msgs/JointState` |
| Arm trajectories | `/a200_0000/arm_0_joint_trajectory_controller/follow_joint_trajectory` | `control_msgs/FollowJointTrajectory` |
| MoveIt | `/a200_0000/move_action`, planning group `arm_0` | `moveit_msgs/MoveGroup` |

The arm's joints are `arm_0_joint_1` to `arm_0_joint_6`; its flange is `arm_0_flange` and its tool
frame `arm_0_tool0`. With all joints at zero, the upper arm points up and the forearm forward.
MoveIt knows the named poses `home` (all zero), `ready` (tool pointing down in front of the arm)
and `reach_front`.

## Files

| File | What |
|---|---|
| `robot.yaml` | Clearpath's configuration: Husky A200, bumpers, top plate, and the arm as a URDF extra |
| `tools/make_gofa_macro.py` | Builds the arm's description from ROS-Industrial's at image build time, adding what Gazebo needs |
| `urdf/gofa_on_husky.urdf.xacro` | Puts the arm on `top_plate_default_mount` |
| `config/arm_controller.yaml` | The arm's joint trajectory controller |
| `config/moveit.yaml`, `launch/moveit.launch.py` | MoveIt for the arm, with the joint limits from ROS-Industrial's package |
| `bin/start-sim` | Starts Gazebo, the controllers, MoveIt and RViz |
| `examples/drive_and_reach.py` | A plain ROS 2 example: drive, then send the arm a trajectory |

## Notes

- ROS-Industrial's package has the arm's shape, kinematics and joint limits, but no masses and no
  torque limits. `make_gofa_macro.py` adds estimates: ABB's 48 kg for the arm, shared over the
  links, and torque limits that hold the arm stretched out with 12 kg. They are good enough to
  try code, not to judge payloads or the Husky's stability.
- ROS-Industrial's package is made for ROS 1. Only its description files and meshes are used here.
- Clearpath's tools support Kinova, Universal Robots and Franka arms, not ABB, so the arm is added
  through Clearpath's `extras` and its controller is started by `start-sim`.
- Without a GPU, Gazebo and RViz render with Mesa's software renderer. On a slow laptop, Gazebo can
  take longer than Clearpath's 60-second timeout to start its controllers; `start-sim` then starts
  them itself.
- Where the arm sits on the real Husky, and which gripper it carries, is not known yet. To move the
  arm, change `parent_link` and `origin` in `urdf/gofa_on_husky.urdf.xacro`.
