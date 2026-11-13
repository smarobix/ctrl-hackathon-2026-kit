"""Work-around for Cyclone DDS 0.10.2 built against a recent glibc (seen on Ubuntu 24.04).

Cyclone 0.10.2 then aborts in its configuration printer when the SDK's
<Tracing><Verbosity>config</Verbosity> block is present. The block only controls a trace file,
so it is removed; what goes over the network is unchanged.
"""
import re

import unitree_sdk2py.core.channel as _channel

_channel.ChannelConfigHasInterface = re.sub(
    r"<Tracing>.*?</Tracing>", "", _channel.ChannelConfigHasInterface, flags=re.S)
