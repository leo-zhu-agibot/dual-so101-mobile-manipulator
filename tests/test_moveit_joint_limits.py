from pathlib import Path
import re

import yaml

ROOT = Path(__file__).parents[1]
URDF = ROOT / "robot_ws/src/dual_so101_description/urdf/so101_arm.xacro"
LIMITS = ROOT / "robot_ws/src/dual_so101_moveit_config/config/joint_limits.yaml"


def _urdf_velocity_limits() -> dict[str, float]:
    text = URDF.read_text()
    return {
        name: float(velocity)
        for name, velocity in re.findall(
            r'<joint name="([^"]+)" type="revolute">.*?<limit[^>]*velocity="([0-9.]+)"',
            text,
            re.DOTALL,
        )
    }


def test_moveit_velocity_limits_do_not_exceed_urdf() -> None:
    urdf_limits = _urdf_velocity_limits()
    moveit_limits = yaml.safe_load(LIMITS.read_text())["joint_limits"]

    for joint, config in moveit_limits.items():
        assert joint in urdf_limits, f"MoveIt joint {joint!r} is missing from the URDF model"
        assert config["max_velocity"] <= urdf_limits[joint], (
            f"MoveIt velocity for {joint} exceeds the URDF limit: "
            f"{config['max_velocity']} > {urdf_limits[joint]}"
        )
