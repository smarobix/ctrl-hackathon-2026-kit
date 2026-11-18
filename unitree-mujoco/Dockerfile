# Unitree B2 and G1 in MuJoCo (Unitree's unitree_mujoco), on Unitree's own DDS interface,
# plus ROS 2 with Unitree's message packages (unitree_ros2) to talk to them. No GPU needed.
#
# The robot side runs like the robot does: unitree_sdk2_python on Cyclone DDS 0.10.2, no ROS.
# The ROS 2 side uses rmw_cyclonedds_cpp and reads the same topics, as on the real robot.
ARG ROS_DISTRO=humble
FROM ros:${ROS_DISTRO}-ros-base
ARG ROS_DISTRO
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
# rmw_fastrtps_dynamic_cpp lets tools such as the SMAROBIX Insights probe read ros2_control on
# Humble.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-${ROS_DISTRO}-rmw-cyclonedds-cpp ros-${ROS_DISTRO}-rosidl-generator-dds-idl \
      ros-${ROS_DISTRO}-rmw-fastrtps-dynamic-cpp \
      python3-venv python3-dev python3-pip python3-colcon-common-extensions build-essential cmake git \
      xvfb x11vnc fluxbox novnc websockify xterm libglfw3 libgl1 libegl1 libgl1-mesa-dri mesa-utils libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Robot side: the Cyclone DDS version unitree_sdk2 is built on, apart from ROS 2's own.
RUN git clone --depth 1 --branch 0.10.2 https://github.com/eclipse-cyclonedds/cyclonedds /tmp/cyclonedds \
 && cmake -S /tmp/cyclonedds -B /tmp/cyclonedds/build -DCMAKE_INSTALL_PREFIX=/opt/cyclonedds-0.10.2 \
      -DCMAKE_BUILD_TYPE=Release -DENABLE_SHM=OFF -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF \
 && cmake --build /tmp/cyclonedds/build --target install -j"$(nproc)" \
 && rm -rf /tmp/cyclonedds

ARG UNITREE_SDK2_PYTHON_COMMIT=814556d15970dd2ecf1c9984e845ca02ab07e206
ARG UNITREE_MUJOCO_COMMIT=1eb6642e3f3fdfb7fb13a9794fd6a2dd93ea0e7d
RUN python3 -m venv /opt/unitree-venv \
 && /opt/unitree-venv/bin/pip install --no-cache-dir -U pip wheel setuptools \
 && CYCLONEDDS_HOME=/opt/cyclonedds-0.10.2 /opt/unitree-venv/bin/pip install --no-cache-dir \
      --no-binary cyclonedds cyclonedds==0.10.2 \
 && /opt/unitree-venv/bin/pip install --no-cache-dir numpy==2.2.6 mujoco==3.17.0 \
 && git clone https://github.com/unitreerobotics/unitree_sdk2_python /opt/unitree_sdk2_python \
 && git -C /opt/unitree_sdk2_python checkout -q ${UNITREE_SDK2_PYTHON_COMMIT} \
 && CYCLONEDDS_HOME=/opt/cyclonedds-0.10.2 /opt/unitree-venv/bin/pip install --no-cache-dir -e /opt/unitree_sdk2_python \
 && git clone https://github.com/unitreerobotics/unitree_mujoco /opt/unitree_mujoco \
 && git -C /opt/unitree_mujoco checkout -q ${UNITREE_MUJOCO_COMMIT}

# ROS 2 side: Unitree's message packages, so ROS 2 nodes can use the robot's topics.
ARG UNITREE_ROS2_COMMIT=668d1ec5a05d1c38d3306bdca7d59f2ba3581a88
RUN git clone https://github.com/unitreerobotics/unitree_ros2 /tmp/unitree_ros2 \
 && git -C /tmp/unitree_ros2 checkout -q ${UNITREE_ROS2_COMMIT} \
 && mkdir -p /opt/unitree_ws/src \
 && cp -r /tmp/unitree_ros2/cyclonedds_ws/src/unitree/unitree_api /tmp/unitree_ros2/cyclonedds_ws/src/unitree/unitree_go \
          /tmp/unitree_ros2/cyclonedds_ws/src/unitree/unitree_hg /opt/unitree_ws/src/ \
 && rm -rf /tmp/unitree_ros2 \
 && source /opt/ros/${ROS_DISTRO}/setup.bash && cd /opt/unitree_ws \
 && colcon build --event-handlers console_cohesion- && rm -rf build log

COPY . /opt/kit/
RUN install -m 0755 /opt/kit/bin/* /usr/local/bin/ \
 && echo "source /opt/ros/${ROS_DISTRO}/setup.bash; source /opt/unitree_ws/install/setup.bash" >> /root/.bashrc

# ROS 2 nodes in this image use Cyclone DDS, as unitree_ros2 asks for.
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
WORKDIR /root
CMD ["run-sim"]
