from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import xacro
import yaml


ROOT = Path(__file__).parents[1]
DESCRIPTION = ROOT / "robot_ws/src/dual_so101_description"


def _urdf() -> ET.Element:
    document = xacro.process_file(
        str(DESCRIPTION / "urdf/dual_so101_mobile.urdf.xacro"),
        mappings={"use_mock_hardware": "true"},
    )
    return ET.fromstring(document.toxml())


def test_xacro_expands_unique_mobile_manipulator() -> None:
    root = _urdf()
    links = {element.attrib["name"] for element in root.findall("link")}
    joints = [element.attrib["name"] for element in root.findall("joint")]
    assert len(links) == 27
    assert len(joints) == len(set(joints)) == 26
    assert {
        "left_tcp_link",
        "right_tcp_link",
        "head_rgbd_color_optical_frame",
        "head_rgbd_depth_optical_frame",
        "lidar_link",
        "imu_link",
    } <= links


def test_ros2_control_and_controller_config_agree() -> None:
    root = _urdf()
    control = root.find("ros2_control")
    assert control is not None
    hardware_joints = {joint.attrib["name"] for joint in control.findall("joint")}
    controllers = yaml.safe_load((DESCRIPTION / "config/controllers.yaml").read_text())
    configured = {
        *controllers["left_arm_controller"]["ros__parameters"]["joints"],
        *controllers["right_arm_controller"]["ros__parameters"]["joints"],
        *controllers["mobile_base_controller"]["ros__parameters"]["left_wheel_names"],
        *controllers["mobile_base_controller"]["ros__parameters"]["right_wheel_names"],
    }
    assert configured == hardware_joints


def test_perception_topics_flow_into_navigation_and_recording() -> None:
    nav2 = yaml.safe_load(
        (ROOT / "robot_ws/src/dual_so101_bringup/config/nav2_params.yaml").read_text()
    )
    contract = yaml.safe_load((ROOT / "data_pipeline/config/bag_contract.yaml").read_text())
    recorded = {item["name"] for item in contract["topics"]}
    voxel = nav2["local_costmap"]["local_costmap"]["ros__parameters"]["voxel_layer"]
    assert voxel["scan"]["topic"] in recorded
    assert "/head_rgbd/depth/image_rect_raw" in recorded
    assert "/imu/data" in recorded

