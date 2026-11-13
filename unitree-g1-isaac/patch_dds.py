"""Lets DDS_DOMAIN and DDS_IFACE choose the simulation's DDS domain and network interface.

unitree_sim_isaaclab always joins domain 1 on an interface Cyclone DDS picks, which at an event
puts every laptop's simulation on the same shared network. With DDS_IFACE=lo it stays local.
"""
PATH = "/home/code/unitree_sim_isaaclab/dds/dds_master.py"
OLD = "ChannelFactoryInitialize(1)"
NEW = 'ChannelFactoryInitialize(int(os.environ.get("DDS_DOMAIN", "1")), os.environ.get("DDS_IFACE") or None)'

source = open(PATH).read()
assert source.count(OLD) == 1, "dds_master.py changed upstream"
open(PATH, "w").write("import os\n" + source.replace(OLD, NEW))
print("patched", PATH)
