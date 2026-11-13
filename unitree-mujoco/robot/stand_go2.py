"""Makes the simulated Go2 stand up and stay up, with unitree_mujoco's stand_go2.py example.

Unitree's example is run as it is, with three changes made to its source when it loads: it
starts without waiting for Enter, it uses this kit's DDS domain and interface, and it holds the
standing pose instead of lying down again after a few seconds. It commands the robot over
rt/lowcmd, so it is a third DDS process next to the simulation.

usage: stand_go2.py <dds domain> <network interface>
"""
import sys

import robot_env  # noqa: F401  Cyclone 0.10.2 work-around, see robot_env.py
import unitree_sdk2py.core.channel as channel

EXAMPLE = "/opt/unitree_mujoco/example/python/stand_go2.py"
DOMAIN, IFACE = int(sys.argv[1]), sys.argv[2]

_initialize = channel.ChannelFactoryInitialize
channel.ChannelFactoryInitialize = lambda *_: _initialize(DOMAIN, IFACE)

source = open(EXAMPLE).read()
for old, new in [('input("Press enter to start")', ""),
                 ("phase = np.tanh((runing_time - 3.0) / 1.2)", "phase = 0.0  # hold the standing pose")]:
    if old not in source:
        sys.exit(f"stand_go2.py changed upstream, cannot find: {old}")
    source = source.replace(old, new)
sys.argv = [EXAMPLE]
exec(compile(source, EXAMPLE, "exec"), {"__name__": "__main__", "__file__": EXAMPLE})
