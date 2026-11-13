# Unitree G1 in NVIDIA Isaac Sim

Unitree's Isaac Lab simulation ([unitree_sim_isaaclab](https://github.com/unitreerobotics/unitree_sim_isaaclab)):
a G1 with 29 joints and grippers at a pick-and-place table, on Isaac Sim 5.1 and Isaac Lab 2.3.2. The
robot speaks Unitree's DDS like the real one, so the ROS 2 side from `../unitree-mujoco` works with it.

The Dockerfile follows Unitree's, with the changes it took to run: Isaac Lab pinned to v2.3.2,
Isaac Lab's core package installed by hand, extra X and GL libraries, pyarrow for NumPy 1, and the
DDS domain and interface taken from the environment.

## Needs

- An NVIDIA RTX GPU with the 580 driver series. Isaac Sim 5.1 crashed on the 595 series.
- The NVIDIA Container Toolkit.
- About 45 GB for the image, and 3 GB to download Unitree's assets (1.3 GB once unpacked).
- Acceptance of NVIDIA's [Isaac Sim licence](https://docs.isaacsim.omniverse.nvidia.com/latest/common/NVIDIA_Omniverse_License_Agreement.html).
  `ACCEPT_EULA=YES` below says you accept it.

## Start

```bash
ACCEPT_EULA=YES docker compose build g1               # 20 to 60 minutes, downloads ~20 GB
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose run --rm fetch-assets   # once: Unitree's scene and robot assets
ACCEPT_EULA=YES docker compose up -d g1
```

Isaac Sim takes a minute or two to start; `docker logs -f unitree-g1-isaac` shows progress. The
picture is streamed over WebRTC. Open NVIDIA's *Isaac Sim WebRTC Streaming Client* and connect to
this machine (port 49100).

Other tasks from unitree_sim_isaaclab: `TASK=<name> ACCEPT_EULA=YES docker compose up -d g1`.

Run either this or the MuJoCo robot from `../unitree-mujoco`, not both: they use the same DDS domain
and topics.

Two things in the log are expected. Unitree's camera server for teleoperation repeats
`WebRTC Thread Error` and `Publisher failed to start` every ten seconds; the robot's DDS interface
works regardless. Isaac Sim's stream listens on all interfaces (port 49100), so others on the
network could connect to the view.

## Use it from ROS 2

The ROS 2 side is the image from `../unitree-mujoco`. Build that one first.

```bash
docker compose up -d ros
docker compose exec ros bash
ros2 topic list                                   # /lowstate, /lowcmd, ...
python3 /root/examples/watch_lowstate.py g1
```

From your laptop's ROS 2, use the settings from `../unitree-mujoco/README.md` (domain 1, `lo`).

## Files

| File | What |
|---|---|
| `Dockerfile` | Isaac Sim, Isaac Lab, Unitree's SDK and simulation, at fixed versions |
| `fetch-assets` | Downloads Unitree's assets at a fixed revision, without the interactive question Unitree's script stops at |
| `patch_dds.py` | Lets `DDS_DOMAIN` and `DDS_IFACE` set the simulation's DDS domain and interface |
| `run-g1` | Starts the simulation. Settings: `TASK`, `ROBOT_TYPE`, `DDS_DOMAIN`, `DDS_IFACE` |
