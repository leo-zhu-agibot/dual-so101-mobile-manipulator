from pathlib import Path
import xml.etree.ElementTree as ET

import xacro
import yaml

ROOT = Path(__file__).parents[1]
ROBOT = ROOT / "robot_ws/src/dual_so101_description/urdf/dual_so101_mobile.urdf.xacro"
LIMITS = ROOT / "robot_ws/src/dual_so101_moveit_config/config/joint_limits.yaml"


def _expanded_urdf() -> ET.Element:
    document = xacro.process_file(
        str(ROBOT),
        mappings={"use_mock_hardware": "true"},
    )
    return ET.fromstring(document.toxml())


def _urdf_velocity_limits() -> dict[str, float]:
    root = _expanded_urdf()
    return {
        joint.attrib["name"]: float(joint.find("limit").attrib["velocity"])
        for joint in root.findall("joint")
        if joint.find("limit") is not None and "velocity" in joint.find("limit").attrib
    }


def test_moveit_velocity_limits_do_not_exceed_urdf() -> None:
    urdf_limits = _urdf_velocity_limits()
    moveit_limits = yaml.safe_load(LIMITS.read_text())["joint_limits"]

    assert urdf_limits
    for joint, config in moveit_limits.items():
        assert joint in urdf_limits, f"MoveIt joint {joint!r} is missing from the expanded URDF"
        assert "max_velocity" in config, f"MoveIt joint {joint!r} has no max_velocity"
        assert config["max_velocity"] <= urdf_limits[joint], (
            f"MoveIt velocity for {joint} exceeds the URDF limit: "
            f"{config['max_velocity']} > {urdf_limits[joint]}"
        )
