from __future__ import annotations

import sqlite3
from pathlib import Path

import yaml

from mobile_manipulation_data.bag_qc import inspect_bag


def _bag(tmp_path: Path, include_imu: bool = True) -> tuple[Path, Path]:
    bag = tmp_path / "episode_0001"
    bag.mkdir()
    database = bag / "episode_0001.db3"
    topics = [
        (1, "/joint_states", "sensor_msgs/msg/JointState"),
        (2, "/imu/data", "sensor_msgs/msg/Imu"),
    ]
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE topics(id INTEGER PRIMARY KEY, name TEXT, type TEXT)")
        connection.execute("CREATE TABLE messages(id INTEGER PRIMARY KEY, topic_id INTEGER, timestamp INTEGER, data BLOB)")
        connection.executemany("INSERT INTO topics VALUES (?, ?, ?)", topics)
        message_id = 1
        for topic_id, rate in ((1, 50), (2, 100)):
            if topic_id == 2 and not include_imu:
                continue
            for index in range(rate * 2):
                connection.execute(
                    "INSERT INTO messages VALUES (?, ?, ?, ?)",
                    (message_id, topic_id, index * int(1e9 / rate), b"payload"),
                )
                message_id += 1
    counts = [
        {
            "topic_metadata": {"name": name, "type": message_type},
            "message_count": (100 if topic_id == 1 else 200),
        }
        for topic_id, name, message_type in topics
        if include_imu or topic_id != 2
    ]
    metadata = {
        "rosbag2_bagfile_information": {
            "duration": {"nanoseconds": 2_000_000_000},
            "relative_file_paths": [database.name],
            "topics_with_message_count": counts,
        }
    }
    (bag / "metadata.yaml").write_text(yaml.safe_dump(metadata))
    contract = tmp_path / "contract.yaml"
    contract.write_text(
        yaml.safe_dump(
            {
                "topics": [
                    {"name": "/joint_states", "type": "sensor_msgs/msg/JointState", "min_rate_hz": 40, "max_gap_ms": 30},
                    {"name": "/imu/data", "type": "sensor_msgs/msg/Imu", "min_rate_hz": 80, "max_gap_ms": 20},
                ]
            }
        )
    )
    return bag, contract


def test_qc_passes_complete_bag(tmp_path: Path) -> None:
    bag, contract = _bag(tmp_path)
    report = inspect_bag(bag, contract)
    assert report.passed
    assert {topic.name for topic in report.topics} == {"/joint_states", "/imu/data"}
    assert not report.issues


def test_qc_rejects_missing_required_topic(tmp_path: Path) -> None:
    bag, contract = _bag(tmp_path, include_imu=False)
    report = inspect_bag(bag, contract)
    assert not report.passed
    assert any(issue.code == "missing_topic" and issue.topic == "/imu/data" for issue in report.issues)

