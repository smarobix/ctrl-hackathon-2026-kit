# Unitree B2 and G1 in MuJoCo

Unitree's own MuJoCo simulator ([unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco)),
serving the robot's low-level interface on Unitree's DDS, the way the real robot does. ROS 2 Humble
with Unitree's message packages ([unitree_ros2](https://github.com/unitreerobotics/unitree_ros2))
reads and writes the same topics. Runs without a GPU.

## Start

```bash
docker compose up --build -d             # B2; first build: about 10 minutes
ROBOT=g1 docker compose up -d robot      # switch to the G1
```

Open <http://localhost:6081/vnc.html> and click *Connect* to see the robot. The B2 stands up after a
few seconds. The G1 hangs from an elastic band: in the viewer, keys 7 and 8 lower and raise it, and
9 lets go.

Stop with `docker compose down`.

## Use it from ROS 2

The `ros` container has ROS 2 Humble, Cyclone DDS and Unitree's messages:

```bash
docker compose exec ros bash
ros2 topic list                                   # /lowstate, /lowcmd, /sportmodestate, ...
python3 /root/examples/watch_lowstate.py b2       # or g1
```

From ROS 2 Humble on your laptop, build Unitree's messages
([unitree_ros2](https://github.com/unitreerobotics/unitree_ros2), `cyclonedds_ws/src/unitree`) and
use the same settings as the `ros` container:

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp ROS_DOMAIN_ID=1
export CYCLONEDDS_URI=file://$PWD/cyclonedds-lo.xml
```

Cyclone prints `selected interface "lo" is not multicast-capable: disabling multicast`. That is
expected; discovery still works on the same machine.

| Topic | B2 type | G1 type | |
|---|---|---|---|
| `/lowstate` | `unitree_go/LowState` | `unitree_hg/LowState` | joints, IMU, 200 Hz |
| `/lowcmd` | `unitree_go/LowCmd` | `unitree_hg/LowCmd` | joint commands (with CRC, see unitree_ros2's examples) |
| `/sportmodestate` | `unitree_go/SportModeState` | | body position and velocity |

The B2's 12 motors are the first 12 entries of `motor_state` and `motor_cmd`: front right, front
left, rear right, rear left leg, each hip, thigh, calf.

## The real robot

On the real robot, the same topics are on DDS domain 0 on the robot's network interface. Drop
`ROS_DOMAIN_ID` and `CYCLONEDDS_URI`, and follow unitree_ros2's setup for the interface. The B2's
walking controller (`SportClient`, `/api/sport/request`) is on the real robot only.

## Files

| File | What |
|---|---|
| `robot/sim.py` | Runs a robot from unitree_mujoco with its DDS bridge, with or without the viewer |
| `robot/stand_b2.py` | Unitree's stand-up example for the B2, holding the standing pose |
| `robot/robot_env.py` | A work-around for Cyclone DDS 0.10.2 with recent glibc |
| `bin/run-sim` | Starts the robot. Settings: `ROBOT`, `DOMAIN`, `IFACE`, `VIEWER`, `STAND` |
| `cyclonedds-lo.xml` | Cyclone settings for ROS 2 nodes on the same machine |
| `examples/watch_lowstate.py` | A plain ROS 2 node reading `/lowstate` |
