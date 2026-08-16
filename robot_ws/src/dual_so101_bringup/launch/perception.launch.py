from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    enabled = LaunchConfiguration("hardware_sensors")
    return LaunchDescription(
        [
            DeclareLaunchArgument("hardware_sensors", default_value="false"),
            Node(
                package="realsense2_camera",
                executable="realsense2_camera_node",
                namespace="head_rgbd",
                name="camera",
                parameters=[
                    {
                        "enable_depth": True,
                        "enable_color": True,
                        "align_depth.enable": True,
                        "pointcloud.enable": True,
                    }
                ],
                condition=IfCondition(enabled),
            ),
            Node(
                package="sllidar_ros2",
                executable="sllidar_node",
                name="lidar",
                parameters=[{"frame_id": "lidar_link", "scan_mode": "Standard"}],
                condition=IfCondition(enabled),
            ),
            Node(
                package="imu_filter_madgwick",
                executable="imu_filter_madgwick_node",
                parameters=[{"use_mag": False, "world_frame": "enu"}],
                remappings=[("imu/data_raw", "/imu/raw"), ("imu/data", "/imu/data")],
                condition=IfCondition(enabled),
            ),
        ]
    )
