"""Episode annotation validation for manipulation demonstrations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


OUTCOMES = {"success", "failure", "aborted"}


@dataclass(frozen=True, slots=True)
class EpisodeAnnotation:
    episode_id: str
    task: str
    outcome: str
    start_seconds: float
    end_seconds: float
    failure_mode: str | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EpisodeAnnotation":
        annotation = cls(
            episode_id=str(raw["episode_id"]),
            task=str(raw["task"]),
            outcome=str(raw["outcome"]),
            start_seconds=float(raw["start_seconds"]),
            end_seconds=float(raw["end_seconds"]),
            failure_mode=raw.get("failure_mode"),
            notes=str(raw.get("notes", "")),
        )
        annotation.validate()
        return annotation

    @classmethod
    def read(cls, path: Path) -> "EpisodeAnnotation":
        return cls.from_dict(json.loads(path.read_text()))

    def validate(self) -> None:
        if not self.episode_id or not self.task:
            raise ValueError("episode_id and task are required")
        if self.outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {sorted(OUTCOMES)}")
        if self.start_seconds < 0 or self.end_seconds <= self.start_seconds:
            raise ValueError("annotation interval must be positive and ordered")
        if self.outcome == "failure" and not self.failure_mode:
            raise ValueError("failure annotations require failure_mode")

