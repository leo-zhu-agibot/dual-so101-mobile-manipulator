from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch


def generate_launch_description():
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    config = (
        MoveItConfigsBuilder("dual_so101_mobile", package_name="dual_so101_moveit_config")
        .robot_description(
            file_path="../dual_so101_description/urdf/dual_so101_mobile.urdf.xacro",
            mappings={"use_mock_hardware": use_mock_hardware},
        )
        .robot_description_semantic(file_path="config/dual_so101.srdf")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl"], default_planning_pipeline="ompl")
        .to_moveit_configs()
    )
    move_group = generate_move_group_launch(config)
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_mock_hardware", default_value="true"),
            *move_group.entities,
        ]
    )
