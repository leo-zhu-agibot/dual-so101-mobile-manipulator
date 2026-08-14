"""Build and execute reproducible rosbag2 episode recording commands."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


def topics_from_contract(contract_path: Path) -> tuple[str, ...]:
    raw = yaml.safe_load(contract_path.read_text())
    topics = tuple(str(item["name"]) for item in raw["topics"])
    if len(topics) != len(set(topics)):
        raise ValueError("recording contract contains duplicate topics")
    return topics


def build_record_command(
    output: Path,
    contract_path: Path,
    *,
    storage: str = "sqlite3",
) -> list[str]:
    return [
        "ros2",
        "bag",
        "record",
        "--storage",
        storage,
        "--output",
        str(output),
        *topics_from_contract(contract_path),
    ]


def record_episode(output: Path, contract_path: Path, *, storage: str = "sqlite3") -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = build_record_command(output, contract_path, storage=storage)
    return subprocess.run(command, check=False).returncode

