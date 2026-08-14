FROM osrf/ros:jazzy-desktop

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends \
    git python3-colcon-common-extensions python3-pip python3-rosdep python3-vcstool \
    ros-jazzy-controller-manager ros-jazzy-diff-drive-controller \
    ros-jazzy-joint-trajectory-controller ros-jazzy-moveit \
    ros-jazzy-nav2-bringup ros-jazzy-ros2-control ros-jazzy-ros2-controllers \
    ros-jazzy-xacro && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
RUN rosdep init 2>/dev/null || true

