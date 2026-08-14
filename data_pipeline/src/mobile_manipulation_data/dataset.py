"""Create traceable episode manifests for downstream LeRobot conversion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from mobile_manipulation_data.annotations import EpisodeAnnotation
from mobile_manipulation_data.bag_qc import BagQCReport


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_episode_manifest(
    bag_path: Path,
    annotation: EpisodeAnnotation,
    report: BagQCReport,
) -> dict[str, Any]:
    if not report.passed:
        raise ValueError("QC must pass before dataset release")
    files = sorted(path for path in bag_path.iterdir() if path.is_file())
    return {
        "schema_version": 1,
        "episode_id": annotation.episode_id,
        "task": annotation.task,
        "outcome": annotation.outcome,
        "trim": {"start_seconds": annotation.start_seconds, "end_seconds": annotation.end_seconds},
        "source": {
            "format": "rosbag2",
            "path": str(bag_path),
            "files": [{"name": path.name, "sha256": _sha256(path)} for path in files],
        },
        "qc": report.to_dict(),
        "target": {"format": "lerobot", "robot_type": "dual_so101_mobile", "fps": 30},
    }


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records))

