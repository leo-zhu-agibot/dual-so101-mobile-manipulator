from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    use_nav2 = LaunchConfiguration("use_nav2")
    use_moveit = LaunchConfiguration("use_moveit")
    use_sim_time = LaunchConfiguration("use_sim_time")
    control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("dual_so101_bringup"), "launch", "control.launch.py"])
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )
    perception = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("dual_so101_bringup"), "launch", "perception.launch.py"])
        )
    )
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("nav2_bringup"), "launch", "navigation_launch.py"])
        ),
        launch_arguments={
            "params_file": PathJoinSubstitution(
                [FindPackageShare("dual_so101_bringup"), "config", "nav2_params.yaml"]
            ),
            "use_sim_time": use_sim_time,
        }.items(),
        condition=IfCondition(use_nav2),
    )
    moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("dual_so101_moveit_config"), "launch", "move_group.launch.py"]
            )
        ),
        condition=IfCondition(use_moveit),
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_nav2", default_value="true"),
            DeclareLaunchArgument("use_moveit", default_value="true"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            control,
            perception,
            nav2,
            moveit,
        ]
    )
