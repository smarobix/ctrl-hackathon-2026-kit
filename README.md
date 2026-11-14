# CTRL Hackathon 2026: simulation kit

Simulated versions of robots at the [CTRL Construction Robotics Hackathon](https://www.ctrl-rwth.de/events/ctrl-hackathon-2026)
(Aachen, 27 to 29 November 2026), so you can write and try ROS 2 code before your time on the real
robots. Each folder is one simulation in Docker, built from the robot makers' own open-source packages.

| Folder | Robot | Simulator | Needs |
|---|---|---|---|
| [`husky-gofa/`](husky-gofa/) | Clearpath Husky A200 with an ABB GoFa CRB 15000-12/1.27 arm | Gazebo, ROS 2 Humble, ros2_control, MoveIt | Linux, Docker |
| [`unitree-mujoco/`](unitree-mujoco/) | Unitree B2 and Unitree G1 | MuJoCo on Unitree's DDS interface, ROS 2 Humble | Linux, Docker |
| [`unitree-g1-isaac/`](unitree-g1-isaac/) | Unitree G1 with grippers at a pick-and-place table | NVIDIA Isaac Sim 5.1, Isaac Lab | Linux, Docker, NVIDIA RTX GPU |

The first two run on any recent Linux laptop without a GPU. Isaac Sim needs an NVIDIA RTX card.

## Before you start

- **Docker** with the Compose plugin (`docker compose version`). For Isaac Sim, also the
  [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
- **Disk:** about 6 GB for the Husky, 3 GB for the Unitree MuJoCo image, 45 GB for Isaac Sim.
- **Your own ROS 2:** the containers share your machine's network, so ROS 2 Humble installed on your
  laptop can talk to them. Each folder's README says which settings to use.

## How the simulations stay on your laptop

At the event, many laptops share one network with the real robots. The simulations are set up so
that they never mix with each other or with a real robot:

- The Husky runs with `ROS_LOCALHOST_ONLY=1`: ROS 2 and Gazebo talk over loopback only.
- The Unitree simulations use DDS domain 1 on the loopback interface (`lo`), as Unitree's own
  simulators do. Real Unitree robots use domain 0 on the robot's network.

To reach a simulation from ROS 2 on your laptop, use the same settings (see each README). To work
with the real robot, leave them out.

## What is simulated and what is not

These are starting points for trying code, not replicas of the event setup.

- The real Husky carries the GoFa CRB 15000-12/1.27. Where it sits, the gripper and the sensors
  are still being decided. The kit puts the arm in the middle of the top plate, with no gripper.
- The B2 simulation has Unitree's low-level interface (joint states and commands). Unitree's
  walking controller (the sport service behind `SportClient`) is not part of it.
- The G1 in MuJoCo hangs from an elastic band, because there is no balance controller. In Isaac Sim,
  the default is Unitree's pick-and-place task for the G1's arms and grippers.

## Licences

The files in this repository are copyright 2026 SMAROBIX GmbH, under the
[Apache License 2.0](LICENSE). The images download and build third-party software, each under its
own licence:

- Clearpath simulator: BSD-3-Clause.
- ROS-Industrial's abb_crb15000_support and abb_resources: Apache-2.0.
- Unitree's unitree_mujoco, unitree_sdk2_python and unitree_ros2: BSD-3-Clause.
- Unitree's unitree_sim_isaaclab: see its repository. Its assets on Hugging Face: Apache-2.0.
- NVIDIA Isaac Sim and Isaac Lab: NVIDIA's licences. You accept Isaac Sim's licence when you build
  that image.

Prepared by [SMAROBIX](https://smarobix.com) for the hackathon. Questions: open an issue.
