from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    use_mock = LaunchConfiguration("use_mock_hardware")
    description_file = PathJoinSubstitution(
        [FindPackageShare("dual_so101_description"), "urdf", "dual_so101_mobile.urdf.xacro"]
    )
    controller_file = PathJoinSubstitution(
        [FindPackageShare("dual_so101_description"), "config", "controllers.yaml"]
    )
    robot_description = {
        "robot_description": Command(
            [FindExecutable(name="xacro"), " ", description_file, " use_mock_hardware:=", use_mock]
        )
    }

    nodes = [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[robot_description, {"use_sim_time": True}],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[robot_description, controller_file],
            output="screen",
        ),
    ]
    for controller in (
        "joint_state_broadcaster",
        "mobile_base_controller",
        "left_arm_controller",
        "right_arm_controller",
    ):
        nodes.append(
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[controller, "--controller-manager", "/controller_manager"],
            )
        )
    return LaunchDescription([DeclareLaunchArgument("use_mock_hardware", default_value="true"), *nodes])

