# Unitree G1 in NVIDIA Isaac Sim 5.1 with Isaac Lab 2.3.2, from Unitree's unitree_sim_isaaclab.
#
# Follows Unitree's own Dockerfile at the pinned commit, with what it took to make it run:
# Isaac Lab pinned to v2.3.2, Isaac Lab's core package installed by hand, the X and GL libraries
# Isaac Sim needs, pyarrow for NumPy 1, and the DDS domain and interface set from the environment.
#
# Needs an NVIDIA RTX GPU, driver 580 series (Isaac Sim 5.1 crashed with 595) and the NVIDIA
# Container Toolkit. Building installs and starts Isaac Sim, which requires accepting NVIDIA's
# Isaac Sim license: docker build --build-arg ACCEPT_EULA=YES ...

# ------------------------------------------------------------------ builder
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS builder
ARG ACCEPT_EULA
RUN [ "$ACCEPT_EULA" = YES ] || { echo "Building Isaac Sim requires accepting NVIDIA's Isaac Sim license: --build-arg ACCEPT_EULA=YES"; exit 1; }
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC CONDA_DIR=/opt/conda OMNI_KIT_ACCEPT_EULA=YES
ENV PATH=$CONDA_DIR/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc-12 g++-12 cmake build-essential unzip git git-lfs libglu1-mesa-dev vulkan-tools wget ca-certificates \
 && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 100 \
 && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-12 100 \
 && rm -rf /var/lib/apt/lists/*
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
 && bash /tmp/miniconda.sh -b -p $CONDA_DIR && rm /tmp/miniconda.sh \
 && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
 && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r \
 && conda create -n unitree_sim_env python=3.11 -y && conda clean -afy
SHELL ["conda", "run", "-n", "unitree_sim_env", "/bin/bash", "-c"]

RUN conda install -y -c conda-forge "libgcc-ng>=12" "libstdcxx-ng>=12" && conda clean -afy
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126
RUN pip install --no-cache-dir "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com

WORKDIR /home/code
# Unitree's Dockerfile clones Isaac Lab's main branch, which no longer has isaaclab.sh.
RUN git clone -b v2.3.2 --depth 1 https://github.com/isaac-sim/IsaacLab.git && cd IsaacLab && ./isaaclab.sh --install
# isaaclab.sh leaves Isaac Lab's core package out: flatdict 4.0.1 does not build with a setuptools
# that has no pkg_resources. Build it with an older setuptools, install the core package, then
# restore the versions Isaac Sim 5.1 pins.
RUN pip install --no-cache-dir "setuptools<81" \
 && pip install --no-cache-dir --no-build-isolation flatdict==4.0.1 \
 && pip install --no-cache-dir -e /home/code/IsaacLab/source/isaaclab \
 && pip install --no-cache-dir packaging==23.0 cryptography==44.0.0 "starlette>=0.40.0,<0.46.0" \
 && python -c "import isaaclab"

RUN git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x /cyclonedds \
 && cmake -S /cyclonedds -B /cyclonedds/build -DCMAKE_INSTALL_PREFIX=/cyclonedds/install \
 && cmake --build /cyclonedds/build --target install -j"$(nproc)" && rm -rf /cyclonedds/build
ENV CYCLONEDDS_HOME=/cyclonedds/install

ARG UNITREE_SDK2_PYTHON_COMMIT=814556d15970dd2ecf1c9984e845ca02ab07e206
RUN git clone https://github.com/unitreerobotics/unitree_sdk2_python \
 && git -C unitree_sdk2_python checkout -q ${UNITREE_SDK2_PYTHON_COMMIT} \
 && pip install --no-cache-dir -e unitree_sdk2_python

ARG UNITREE_SIM_ISAACLAB_COMMIT=e30c25b1dffdf92ada1d6c8c1fe9a47bdde0fecc
RUN git clone https://github.com/unitreerobotics/unitree_sim_isaaclab.git \
 && cd unitree_sim_isaaclab && git checkout -q ${UNITREE_SIM_ISAACLAB_COMMIT} \
 && git submodule update --init --depth 1 \
 && pip install --no-cache-dir -e teleimager && pip install --no-cache-dir -r requirements.txt
# rerun, from the requirements, pulls a pyarrow built for NumPy 2; Isaac Sim 5.1 pins NumPy 1.26.
RUN pip install --no-cache-dir "pyarrow==17.0.0" && python -c "import numpy, pyarrow, rerun"

# The simulation always joins DDS domain 1 on an interface Cyclone picks; see patch_dds.py.
COPY patch_dds.py /tmp/patch_dds.py
RUN python /tmp/patch_dds.py

# ------------------------------------------------------------------ runtime
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH CYCLONEDDS_HOME=/cyclonedds/install OMNI_KIT_ALLOW_ROOT=1 OMNI_KIT_DISABLE_STARTUP=1
# Unitree's runtime stage ships almost no X or GL libraries; MaterialX and the USD material
# libraries need libXt and friends.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libglu1-mesa git git-lfs zenity unzip ca-certificates \
      libxt6 libsm6 libice6 libx11-6 libxext6 libxrender1 libxrandr2 libxinerama1 libxcursor1 libxi6 \
      libxkbcommon0 libgl1 libegl1 libglib2.0-0 libgomp1 libvulkan1 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/conda /opt/conda
COPY --from=builder /cyclonedds/install /cyclonedds/install
COPY --from=builder /home/code /home/code
COPY run-g1 fetch-assets /usr/local/bin/
RUN chmod 0755 /usr/local/bin/run-g1 /usr/local/bin/fetch-assets
WORKDIR /home/code/unitree_sim_isaaclab
CMD ["run-g1"]
