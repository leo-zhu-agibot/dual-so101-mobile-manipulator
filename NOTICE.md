# Third-party attribution

This repository is an independent integration project. It does not claim authorship of the
upstream robot model, simulators, planners, navigation stack, or learning frameworks.

- **SO101-Nexus** — SO-101 MuJoCo environments and robot assets, Apache-2.0,
  <https://github.com/johnsutor/so101-nexus>. Joint naming and calibrated limit values in the
  primitive Xacro model are interoperable with this upstream project. No upstream meshes are
  redistributed here.
- **LeRobot** — robot-learning interfaces and dataset conventions, Apache-2.0,
  <https://github.com/huggingface/lerobot>.
- **ROS 2, ros2_control, MoveIt 2, and Nav2** — consumed through their public interfaces under
  their respective upstream licenses.
- **NVIDIA Isaac Sim** — optional proprietary simulator runtime. This repository contains only
  integration scripts and configuration, not Isaac Sim binaries or assets.

The original orchestration, contracts, QC tooling, baseline policy code, tests, and documentation
in this repository are released under the MIT License.

