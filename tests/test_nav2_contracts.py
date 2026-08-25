from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
NAV2 = ROOT / "robot_ws/src/dual_so101_bringup/config/nav2_params.yaml"


def test_nav2_odom_and_base_frames_match_robot_contract() -> None:
    config = yaml.safe_load(NAV2.read_text())

    amcl = config["amcl"]["ros__parameters"]
    bt = config["bt_navigator"]["ros__parameters"]
    controller = config["controller_server"]["ros__parameters"]
    local = config["local_costmap"]["local_costmap"]["ros__parameters"]
    global_costmap = config["global_costmap"]["global_costmap"]["ros__parameters"]

    assert amcl["base_frame_id"] == "base_footprint"
    assert amcl["odom_frame_id"] == "odom"
    assert bt["robot_base_frame"] == "base_link"
    assert bt["odom_topic"] == "/mobile_base_controller/odom"
    assert controller["controller_frequency"] > 0

    assert local["global_frame"] == "odom"
    assert local["robot_base_frame"] == "base_link"
    assert global_costmap["global_frame"] == "map"
    assert global_costmap["robot_base_frame"] == "base_link"


def test_nav2_motion_limits_are_consistent_with_mobile_base_contract() -> None:
    config = yaml.safe_load(NAV2.read_text())
    follow_path = config["controller_server"]["ros__parameters"]["FollowPath"]

    assert 0.0 < follow_path["max_vel_x"] <= 0.60
    assert 0.0 < follow_path["max_vel_theta"] <= 1.20
    assert follow_path["acc_lim_x"] > 0.0
    assert follow_path["acc_lim_theta"] > 0.0
