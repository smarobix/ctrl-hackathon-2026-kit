# Husky A200 with a Doosan M1013

A Clearpath Husky A200 with a Doosan M1013 on its top plate, in Gazebo, on ROS 2 Humble. The Husky
comes from Clearpath's simulator. The arm comes from Doosan's description package and has a joint
trajectory controller and MoveIt. Runs without a GPU.

## Start

```bash
docker compose up --build -d          # first build: about 10 minutes
```

Open <http://localhost:6080/vnc.html> and click *Connect*. Gazebo starts first. About two minutes
later, RViz opens with MoveIt's *MotionPlanning* panel. Pick a goal state for `arm_0` and press
*Plan & Execute*. Progress: `docker logs -f husky-doosan`; details in `/tmp/*.log` in the container.

Stop with `docker compose down`.

## Use it from ROS 2

Inside the container:

```bash
docker exec -it husky-doosan bash
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

The arm's joints are `arm_0_joint_1` to `arm_0_joint_6`; its flange is `arm_0_link_6`. MoveIt knows
the named poses `home` (arm straight up), `ready` and `reach_front`.

## Files

| File | What |
|---|---|
| `robot.yaml` | Clearpath's configuration: Husky A200, bumpers, top plate, and the arm as a URDF extra |
| `tools/make_m1013_macro.py` | Builds the arm's description from Doosan's at image build time, with prefixed names and a ros2_control block for Gazebo |
| `urdf/m1013_on_husky.urdf.xacro` | Puts the arm on `top_plate_default_mount` |
| `config/arm_controller.yaml` | The arm's joint trajectory controller |
| `config/moveit.yaml`, `launch/moveit.launch.py` | MoveIt for the arm, with Doosan's joint limits |
| `bin/start-sim` | Starts Gazebo, the controllers, MoveIt and RViz |
| `examples/drive_and_reach.py` | A plain ROS 2 example: drive, then send the arm a trajectory |

## Notes

- Clearpath's tools support Kinova, Universal Robots and Franka arms, not Doosan, so the arm is
  added through Clearpath's `extras` and its controller is started by `start-sim`.
- Without a GPU, Gazebo and RViz render with Mesa's software renderer. On a slow laptop, Gazebo can
  take longer than Clearpath's 60-second timeout to start its controllers; `start-sim` then starts
  them itself.
- To move the arm elsewhere, change `parent_link` and `origin` in `urdf/m1013_on_husky.urdf.xacro`.
