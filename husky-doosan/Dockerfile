# Husky A200 with a Doosan M1013 on its top plate, in Gazebo, on ROS 2 Humble.
#
# Clearpath's simulator brings the Husky. The arm comes from Doosan's own description
# (dsr_description2), turned into a macro that can sit on the Husky by tools/make_m1013_macro.py,
# and is driven by a ros2_control joint trajectory controller. MoveIt plans for it.
FROM ros:humble-ros-base
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-humble-clearpath-simulator ros-humble-clearpath-viz ros-humble-clearpath-config \
      ros-humble-moveit ros-humble-ros2controlcli ros-humble-rmw-cyclonedds-cpp \
      python3-colcon-common-extensions git \
      xvfb x11vnc fluxbox novnc websockify xterm mesa-utils libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# Doosan's description package only, at a fixed commit of doosan-robot2 (BSD-3-Clause).
ARG DOOSAN_COMMIT=8653b0440dd23d2b0a57fc413b86269c6967a283
RUN git clone --filter=blob:none --no-checkout https://github.com/DoosanRobotics/doosan-robot2 /tmp/doosan \
 && git -C /tmp/doosan sparse-checkout set dsr_description2 \
 && git -C /tmp/doosan checkout -q ${DOOSAN_COMMIT} \
 && mkdir -p /opt/doosan_ws/src \
 && cp -r /tmp/doosan/dsr_description2 /opt/doosan_ws/src/ \
 && git -C /tmp/doosan show ${DOOSAN_COMMIT}:LICENSE > /opt/doosan_ws/src/dsr_description2/LICENSE \
 && rm -rf /tmp/doosan \
 && source /opt/ros/humble/setup.bash && cd /opt/doosan_ws \
 && colcon build --packages-select dsr_description2 --event-handlers console_cohesion- \
 && rm -rf build log

COPY . /opt/kit/
RUN python3 /opt/kit/tools/make_m1013_macro.py /opt/doosan_ws/install/dsr_description2/share/dsr_description2 \
      /opt/kit/urdf/doosan_m1013.xacro \
 && install -m 0755 /opt/kit/bin/* /usr/local/bin/ \
 && echo 'source /opt/ros/humble/setup.bash; source /opt/doosan_ws/install/setup.bash' >> /root/.bashrc

# The simulation stays on this machine: ROS 2 and Gazebo talk over loopback only, so it cannot
# reach a real Husky (same namespace, same DDS domain) or another laptop's simulation.
ENV ROS_LOCALHOST_ONLY=1 IGN_IP=127.0.0.1
WORKDIR /root
CMD ["start-sim"]
