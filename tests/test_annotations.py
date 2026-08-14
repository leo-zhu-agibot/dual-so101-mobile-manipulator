import pytest

from mobile_manipulation_data.annotations import EpisodeAnnotation


def test_failure_requires_failure_mode() -> None:
    with pytest.raises(ValueError, match="failure_mode"):
        EpisodeAnnotation.from_dict(
            {
                "episode_id": "ep-01",
                "task": "dual-arm handover",
                "outcome": "failure",
                "start_seconds": 0,
                "end_seconds": 4.5,
            }
        )


def test_success_annotation_is_valid() -> None:
    annotation = EpisodeAnnotation.from_dict(
        {
            "episode_id": "ep-02",
            "task": "pick-and-place",
            "outcome": "success",
            "start_seconds": 0.2,
            "end_seconds": 8.0,
        }
    )
    assert annotation.outcome == "success"

