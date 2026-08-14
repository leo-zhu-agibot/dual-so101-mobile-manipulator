# Technical walkthrough for interviews

## Why split navigation and manipulation?

Nav2 solves the lower-dimensional global/local base problem and MoveIt solves collision-aware arm
kinematics. The orchestrator treats navigation completion as a precondition for acquiring a fresh
object pose and planning a grasp. This avoids executing an arm trajectory against stale geometry.

## How is control safety represented?

URDF joint limits define the hard model boundary, MoveIt velocity/acceleration limits define the
planner boundary, and ros2_control trajectory controllers define the execution boundary. The
separate SO101-DeployLab repository adds latency, noise, dropout, clipping, and slew-rate stress
tests to the policy action path.

## What does rosbag QC actually inspect?

The QC tool reads `metadata.yaml` and rosbag2 SQLite timestamp tables directly. It verifies required
topic presence, ROS message type, average rate, and the largest inter-message gap. This catches a
camera process that silently slowed down even when the overall message count looks plausible.

## What is implemented versus environment-dependent?

Implemented and tested here: Xacro expansion, dual-arm/base/sensor frame graph, ros2_control and
planner contracts, Nav2 sensor wiring, rosbag QC, annotation rules, traceable manifests, BC smoke
training, task state transitions, container definition, and CI. Isaac Sim execution, real sensor
drivers, and physical SO-101 calibration require an NVIDIA/ROS2 machine and hardware; their
interfaces are versioned, but they are not falsely reported as exercised on this Mac workspace.

