"""Quality control for rosbag2 SQLite recordings without ROS deserialization."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class TopicRequirement:
    name: str
    message_type: str
    min_rate_hz: float
    max_gap_ms: float
    required: bool = True


@dataclass(frozen=True, slots=True)
class TopicStats:
    name: str
    message_type: str
    messages: int
    rate_hz: float
    max_gap_ms: float


@dataclass(frozen=True, slots=True)
class QCIssue:
    severity: str
    code: str
    topic: str
    detail: str


@dataclass(frozen=True, slots=True)
class BagQCReport:
    bag_path: str
    duration_seconds: float
    passed: bool
    topics: tuple[TopicStats, ...]
    issues: tuple[QCIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n")


def _requirements(path: Path) -> tuple[TopicRequirement, ...]:
    raw = yaml.safe_load(path.read_text())
    return tuple(
        TopicRequirement(
            name=item["name"],
            message_type=item["type"],
            min_rate_hz=float(item["min_rate_hz"]),
            max_gap_ms=float(item["max_gap_ms"]),
            required=bool(item.get("required", True)),
        )
        for item in raw["topics"]
    )


def _metadata(bag_path: Path) -> dict[str, Any]:
    metadata_path = bag_path / "metadata.yaml"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"missing rosbag2 metadata: {metadata_path}")
    raw = yaml.safe_load(metadata_path.read_text())
    try:
        return raw["rosbag2_bagfile_information"]
    except (KeyError, TypeError) as error:
        raise ValueError("invalid rosbag2 metadata.yaml") from error


def _timestamps_by_topic(bag_path: Path, files: list[str]) -> dict[str, list[int]]:
    timestamps: dict[str, list[int]] = {}
    for relative in files:
        database = bag_path / relative
        if database.suffix != ".db3" or not database.is_file():
            continue
        with sqlite3.connect(database) as connection:
            rows = connection.execute(
                "SELECT topics.name, messages.timestamp "
                "FROM messages JOIN topics ON messages.topic_id = topics.id "
                "ORDER BY topics.name, messages.timestamp"
            )
            for topic, timestamp in rows:
                timestamps.setdefault(str(topic), []).append(int(timestamp))
    return timestamps


def inspect_bag(bag_path: Path, contract_path: Path) -> BagQCReport:
    """Validate topic presence, type, rate, and timestamp gaps for one episode."""

    bag_path = bag_path.resolve()
    metadata = _metadata(bag_path)
    duration_ns = int(metadata.get("duration", {}).get("nanoseconds", 0))
    duration_seconds = duration_ns / 1e9
    if duration_seconds <= 0:
        raise ValueError("bag duration must be positive")

    declared: dict[str, tuple[str, int]] = {}
    for item in metadata.get("topics_with_message_count", []):
        topic = item["topic_metadata"]
        declared[str(topic["name"])] = (str(topic["type"]), int(item["message_count"]))

    timestamp_map = _timestamps_by_topic(bag_path, list(metadata.get("relative_file_paths", [])))
    issues: list[QCIssue] = []
    stats: list[TopicStats] = []
    for requirement in _requirements(contract_path):
        if requirement.name not in declared:
            if requirement.required:
                issues.append(QCIssue("error", "missing_topic", requirement.name, "topic absent"))
            continue
        message_type, metadata_count = declared[requirement.name]
        timestamps = timestamp_map.get(requirement.name, [])
        count = len(timestamps) if timestamps else metadata_count
        rate = count / duration_seconds
        gaps = [right - left for left, right in zip(timestamps, timestamps[1:])]
        max_gap_ms = max(gaps, default=0) / 1e6
        stats.append(TopicStats(requirement.name, message_type, count, rate, max_gap_ms))
        if message_type != requirement.message_type:
            issues.append(
                QCIssue("error", "type_mismatch", requirement.name, f"{message_type} != {requirement.message_type}")
            )
        if rate < requirement.min_rate_hz:
            issues.append(
                QCIssue("error", "low_rate", requirement.name, f"{rate:.2f} Hz < {requirement.min_rate_hz:.2f} Hz")
            )
        if timestamps and max_gap_ms > requirement.max_gap_ms:
            issues.append(
                QCIssue("error", "timestamp_gap", requirement.name, f"{max_gap_ms:.1f} ms > {requirement.max_gap_ms:.1f} ms")
            )
    return BagQCReport(
        bag_path=str(bag_path),
        duration_seconds=duration_seconds,
        passed=not any(issue.severity == "error" for issue in issues),
        topics=tuple(stats),
        issues=tuple(issues),
    )

