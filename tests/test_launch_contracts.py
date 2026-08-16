from pathlib import Path

ROOT = Path(__file__).parents[1]
STACK = ROOT / "robot_ws/src/dual_so101_bringup/launch/stack.launch.py"
CONTROL = ROOT / "robot_ws/src/dual_so101_bringup/launch/control.launch.py"
MOVEIT = ROOT / "robot_ws/src/dual_so101_moveit_config/launch/move_group.launch.py"


def test_use_mock_hardware_is_propagated_to_control_and_moveit():
    stack = STACK.read_text()
    control = CONTROL.read_text()
    moveit = MOVEIT.read_text()

    assert 'LaunchConfiguration("use_mock_hardware")' in stack
    assert '"use_mock_hardware": use_mock_hardware' in stack
    assert 'DeclareLaunchArgument("use_mock_hardware"' in control
    assert 'LaunchConfiguration("use_mock_hardware")' in moveit
    assert 'mappings={"use_mock_hardware": use_mock_hardware}' in moveit
