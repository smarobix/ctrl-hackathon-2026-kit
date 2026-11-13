"""Runs a Unitree robot from unitree_mujoco and serves its low-level interface on Unitree's DDS.

The simulated robot publishes rt/lowstate (and, for the Go2, rt/sportmodestate) and follows
rt/lowcmd, through unitree_mujoco's own bridge, the way the real robot's low-level interface does.
Humanoids hang from an elastic band so they do not fall before a controller takes over
(viewer keys: 7 and 8 lower and raise the band, 9 releases it).

usage: sim.py <robot> <dds domain> <network interface> <viewer: 1 or 0>
"""
import os
import sys
import time
import types

import mujoco

ROBOT, DOMAIN, IFACE, VIEWER = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4] == "1"
CLONE = "/opt/unitree_mujoco"
HUMANOIDS = ("g1", "h1", "h1_2", "h2")

# unitree_mujoco's bridge reads its settings from a module named config and imports pygame for
# a gamepad. Both are provided here: settings from the arguments, no gamepad.
config = types.ModuleType("config")
# The bridge picks the message family from config.ROBOT: "g1" means unitree_hg, which the
# other humanoids use as well, so they are announced as g1 while keeping their own scene.
config.ROBOT = "g1" if ROBOT in HUMANOIDS else ROBOT
config.ROBOT_SCENE = os.path.join(CLONE, "unitree_robots", ROBOT, "scene.xml")
config.DOMAIN_ID = DOMAIN
config.INTERFACE = IFACE
config.USE_JOYSTICK = 0
config.PRINT_SCENE_INFORMATION = False
config.ENABLE_ELASTIC_BAND = ROBOT in HUMANOIDS
config.SIMULATE_DT = 0.005
config.VIEWER_DT = 0.02
sys.modules["config"] = config
sys.modules["pygame"] = types.ModuleType("pygame")
sys.path.insert(0, os.path.join(CLONE, "simulate_python"))

import robot_env  # noqa: E402,F401  Cyclone 0.10.2 work-around, see robot_env.py
from unitree_sdk2py.core.channel import ChannelFactoryInitialize  # noqa: E402
from unitree_sdk2py_bridge import ElasticBand, UnitreeSdk2Bridge  # noqa: E402

model = mujoco.MjModel.from_xml_path(config.ROBOT_SCENE)
data = mujoco.MjData(model)
model.opt.timestep = config.SIMULATE_DT

ChannelFactoryInitialize(DOMAIN, IFACE)
bridge = UnitreeSdk2Bridge(model, data)
print(f"robot up: {ROBOT}, DDS domain {DOMAIN}, interface {IFACE}, {model.nu} actuators", flush=True)

band = ElasticBand() if config.ENABLE_ELASTIC_BAND else None
band_body = model.body("torso_link").id if band else None


def step():
    if band and band.enable:
        data.xfrc_applied[band_body, :3] = band.Advance(data.qpos[:3], data.qvel[:3])
    mujoco.mj_step(model, data)


if VIEWER:
    import mujoco.viewer

    viewer = mujoco.viewer.launch_passive(model, data, key_callback=band.MujuocoKeyCallback if band else None)
    steps = 0
    while viewer.is_running():
        start = time.perf_counter()
        step()
        steps += 1
        if steps % int(config.VIEWER_DT / config.SIMULATE_DT) == 0:
            viewer.sync()
        rest = model.opt.timestep - (time.perf_counter() - start)
        if rest > 0:
            time.sleep(rest)
else:
    while True:
        start = time.perf_counter()
        step()
        rest = model.opt.timestep - (time.perf_counter() - start)
        if rest > 0:
            time.sleep(rest)
