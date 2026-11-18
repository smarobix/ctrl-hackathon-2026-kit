# Husky A200 with an ABB GoFa CRB 15000-12/1.27 on its top plate, in Gazebo, on ROS 2 Humble.
#
# Clearpath's simulator brings the Husky. The arm comes from ROS-Industrial's description
# (abb_crb15000_support), turned into a macro that can sit on the Husky by
# tools/make_gofa_macro.py, and is driven by a ros2_control joint trajectory controller.
# MoveIt plans for it.
FROM ros:humble-ros-base
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
# rmw_fastrtps_dynamic_cpp lets tools such as the SMAROBIX Insights probe read ros2_control on
# Humble.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-humble-clearpath-simulator ros-humble-clearpath-viz ros-humble-clearpath-config \
      ros-humble-moveit ros-humble-ros2controlcli ros-humble-rmw-cyclonedds-cpp git \
      ros-humble-rmw-fastrtps-dynamic-cpp \
      xvfb x11vnc fluxbox novnc websockify xterm mesa-utils libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# The GoFa's description and meshes, and ABB's colours, at a fixed commit of ros-industrial/abb
# (Apache-2.0). Only files are used, so nothing is built.
ARG ABB_COMMIT=45f4769d826cf3ac62a65495f2db67b78b0c81df
RUN git clone --filter=blob:none --no-checkout https://github.com/ros-industrial/abb /tmp/abb \
 && git -C /tmp/abb sparse-checkout set abb_crb15000_support abb_resources \
 && git -C /tmp/abb checkout -q ${ABB_COMMIT} \
 && mkdir -p /opt/abb \
 && cp -r /tmp/abb/abb_crb15000_support /tmp/abb/abb_resources /opt/abb/ \
 && rm -rf /tmp/abb

COPY . /opt/kit/
RUN python3 /opt/kit/tools/make_gofa_macro.py /opt/abb /opt/kit/urdf/abb_gofa_12_127.xacro \
 && install -m 0755 /opt/kit/bin/* /usr/local/bin/ \
 && echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc

# The simulation stays on this machine: ROS 2 and Gazebo talk over loopback only, so it cannot
# reach a real Husky (same namespace, same DDS domain) or another laptop's simulation.
ENV ROS_LOCALHOST_ONLY=1 IGN_IP=127.0.0.1
WORKDIR /root
CMD ["start-sim"]
