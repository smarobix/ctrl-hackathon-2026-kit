"""Makes the simulated B2 stand up and stay up, with Unitree's own B2 stand example.

Unitree's example (unitree_sdk2_python, example/b2/low_level/b2_stand_example.py) is run as it
is, with four changes made to its source when it loads: it starts without waiting for Enter, it
uses this kit's DDS domain and interface, it does not ask the robot's motion switcher to release
the walking controller (the simulation has neither), and it holds the standing pose instead of
going on to lie down. It commands the robot over rt/lowcmd, so it is a third DDS process next to
the simulation.

usage: stand_b2.py <dds domain> <network interface>
"""
import os
import sys

import robot_env  # noqa: F401  Cyclone 0.10.2 work-around, see robot_env.py
import unitree_sdk2py.core.channel as channel

EXAMPLE = "/opt/unitree_sdk2_python/example/b2/low_level/b2_stand_example.py"
DOMAIN, IFACE = int(sys.argv[1]), sys.argv[2]

_initialize = channel.ChannelFactoryInitialize
channel.ChannelFactoryInitialize = lambda *_: _initialize(DOMAIN, IFACE)

source = open(EXAMPLE).read()
for old, new in [
        ('input("Press Enter to continue...")', ""),
        # The motion switcher reports that no walking controller is active.
        ("status, result = self.msc.CheckMode()", "status, result = 0, {'name': ''}"),
        # The third phase holds the standing pose; it now lasts forever.
        ("self.duration_3 = 1000", "self.duration_3 = float('inf')"),
        # The example reads the robot's state on its first command, so it waits for one.
        ("    custom.Start()", "    while custom.low_state is None:\n        time.sleep(0.01)\n    custom.Start()")]:
    if old not in source:
        sys.exit(f"b2_stand_example.py changed upstream, cannot find: {old}")
    source = source.replace(old, new)
sys.path.insert(0, os.path.dirname(EXAMPLE))  # for the example's unitree_legged_const
sys.argv = [EXAMPLE]
exec(compile(source, EXAMPLE, "exec"), {"__name__": "__main__", "__file__": EXAMPLE})
