https://www.overleaf.com/read/bhsymfqmrfgp#2e006f
com/8996316972spgzgdqczfbz#11fb2c
###############################################
# 1. ON THE ONLINE SYSTEM (with internet)
###############################################

# Update system
sudo apt update && sudo apt upgrade -y

# Download but don't remove .deb packages
sudo apt install --download-only -y \
    build-essential cmake git pkg-config \
    libopencv-dev libceres-dev \
    libeigen3-dev libgflags-dev libgoogle-glog-dev libyaml-cpp-dev \
    libgl1-mesa-dev libegl1-mesa-dev libepoxy-dev \
    python3-dev python3-catkin-tools python3-catkin-pkg python3-osrf-pycommon \
    nvidia-cuda-toolkit libcublas-11-0 libcublas-dev-11-0 \
    cuda-toolkit-11-8 \
    ros-noetic-desktop-full ros-noetic-catkin

# Collect all .deb files
mkdir -p ~/supervins_offline_pkgs
cp -v /var/cache/apt/archives/*.deb ~/supervins_offline_pkgs/

# Download source codes
mkdir -p ~/supervins_offline_src
cd ~/supervins_offline_src
git clone https://github.com/stevenlovegrove/Pangolin.git
git clone https://github.com/luohongk/SuperVINS.git

# Download ONNX Runtime
mkdir -p ~/supervins_offline_thirdparty
cd ~/supervins_offline_thirdparty
wget https://github.com/microsoft/onnxruntime/releases/download/v1.16.3/onnxruntime-linux-x64-gpu-1.16.3.tgz

# Download CUDA keyring
mkdir -p ~/supervins_offline_keys
cd ~/supervins_offline_keys
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.1-1_all.deb

# Copy Dataset / ROS bag
mkdir -p ~/supervins_offline_data
cp /path/to/MH_01_easy.bag ~/supervins_offline_data/

# Make one bundle
mkdir -p ~/supervins_bundle
cp -r ~/supervins_offline_pkgs ~/supervins_bundle/
cp -r ~/supervins_offline_src ~/supervins_bundle/
cp -r ~/supervins_offline_thirdparty ~/supervins_bundle/
cp -r ~/supervins_offline_keys ~/supervins_bundle/
cp -r ~/supervins_offline_data ~/supervins_bundle/

tar -czvf supervins_offline_bundle.tar.gz ~/supervins_bundle

echo "✅ Copy supervins_offline_bundle.tar.gz to the offline machine"


###############################################
# 2. ON THE OFFLINE SYSTEM (no internet)
###############################################

# Extract the bundle
tar -xzvf supervins_offline_bundle.tar.gz -C ~/
cd ~/supervins_bundle

# Install .deb packages
cd ~/supervins_bundle/supervins_offline_pkgs
sudo dpkg -i *.deb
sudo apt-get install -f -y

# Install CUDA keyring
cd ~/supervins_bundle/supervins_offline_keys
sudo dpkg -i cuda-keyring_1.1-1_all.deb

# Setup ONNX Runtime
cd ~/supervins_bundle/supervins_offline_thirdparty
tar -xvzf onnxruntime-linux-x64-gpu-1.16.3.tgz
mkdir -p ~/catkin_ws/Thirdparty
mv onnxruntime-linux-x64-gpu-1.16.3 ~/catkin_ws/Thirdparty/onnxruntime

# Build Pangolin
cd ~/supervins_bundle/supervins_offline_src/Pangolin
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install

# Setup Catkin Workspace
mkdir -p ~/catkin_ws/src
cp -r ~/supervins_bundle/supervins_offline_src/SuperVINS ~/catkin_ws/src/
cd ~/catkin_ws
catkin_make --force-cmake

# Run SuperVINS
source ~/catkin_ws/devel/setup.bash
roscore &
rosbag play ~/supervins_bundle/supervins_offline_data/MH_01_easy.bag --clock &
roslaunch supervins supervins_rviz.launch &
rosrun supervins supervins_node ~/catkin_ws/src/SuperVINS/config/euroc/euroc_mono_imu_config.yaml








//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' \
  --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
sudo apt-get update


mkdir -p ~/ros_offline/debs

cd ~/ros_offline/debs
sudo apt-get install --download-only \
  ros-noetic-ros-base \
  ros-noetic-cv-bridge \
  ros-noetic-tf \
  ros-noetic-message-filters -y

cp /var/cache/apt/archives/*.deb ~/ros_offline/debs/

apt-cache depends ros-noetic-ros-base \
  ros-noetic-cv-bridge \
  ros-noetic-tf \
  ros-noetic-message-filters \
  > ~/ros_offline/ros_dependencies.txt

<<<<<<cd ~/ros_offline/debs
sudo dpkg -i *.deb
sudo apt-get -f install   # fixes any missing order of deps
>>>>>>>


mkdir -p ~/opencv_offline/src
cd ~/opencv_offline/src
wget https://github.com/opencv/opencv/archive/4.2.0.tar.gz -O opencv-4.2.0.tar.gz
wget https://github.com/opencv/opencv_contrib/archive/4.2.0.tar.gz -O opencv_contrib-4.2.0.tar.gz

sudo apt-get install --download-only \
  build-essential cmake git pkg-config \
  libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev \
  libv4l-dev libxvidcore-dev libx264-dev \
  libjpeg-dev libpng-dev libtiff-dev \
  gfortran libatlas-base-dev \
  python3-dev python3-numpy -y

<<<<<<cd ~/opencv_offline/debs
sudo dpkg -i *.deb
sudo apt-get -f install

cd ~/opencv_offline/src
tar -xvzf opencv-4.2.0.tar.gz
tar -xvzf opencv_contrib-4.2.0.tar.gz

cd opencv-4.2.0
mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=Release \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-4.2.0/modules \
      -D BUILD_opencv_python3=ON \
      ..
make -j$(nproc)
sudo make install
>>>>>


mkdir -p ~/ceres_offline/src
cd ~/ceres_offline/src

wget http://ceres-solver.org/ceres-solver-2.1.0.tar.gz

mkdir -p ~/ceres_offline/debs
cd ~/ceres_offline/debs

sudo apt-get install --download-only \
  cmake build-essential \
  libeigen3-dev \
  libsuitesparse-dev \
  liblapack-dev libblas-dev \
  libgoogle-glog-dev libgflags-dev \
  -y

<<<<cd ~/ceres_offline/debs
sudo dpkg -i *.deb
sudo apt-get -f install

cd ~/ceres_offline/src
tar -xvzf ceres-solver-2.1.0.tar.gz
cd ceres-solver-2.1.0
mkdir build && cd build

cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
make -j$(nproc)
sudo make install

>>>>>

mkdir -p ~/onnxruntime_offline
cd ~/onnxruntime_offline

wget https://github.com/microsoft/onnxruntime/releases/download/v1.16.3/onnxruntime-linux-x64-gpu-1.16.3.tgz
tar -xvzf onnxruntime-linux-x64-gpu-1.16.3.tgz

mkdir -p ~/onnxruntime_offline/debs
cd ~/onnxruntime_offline/debs

sudo apt-get install --download-only \
  libprotobuf-dev protobuf-compiler \
  libomp-dev libgomp1 \
  zlib1g-dev libzstd-dev \
  -y

mkdir -p ~/onnxruntime_offline/pip
pip download onnxruntime-gpu==1.16.3 numpy protobuf -d ~/onnxruntime_offline/pip/

<<<cd ~/onnxruntime_offline/debs
sudo dpkg -i *.deb
sudo apt-get -f install

cd ~/onnxruntime_offline
tar -xvzf onnxruntime-linux-x64-gpu-1.16.3.tgz -C /opt/

pip install --no-index --find-links=~/onnxruntime_offline/pip onnxruntime-gpu==1.16.3

export LD_LIBRARY_PATH=/opt/onnxruntime-linux-x64-gpu-1.16.3/lib:$LD_LIBRARY_PATH

>>>>>


cd ~/third_party/
tar -xvzf some-library.tar.gz
cd some-library
mkdir build && cd build

cmake .. \
  -D CMAKE_BUILD_TYPE=Release \
  -D CMAKE_INSTALL_PREFIX=/home/aman/local_libs

make -j$(nproc)
make install




