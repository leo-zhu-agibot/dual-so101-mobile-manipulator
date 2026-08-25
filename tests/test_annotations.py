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


def test_aborted_requires_failure_mode() -> None:
    with pytest.raises(ValueError, match="aborted annotations require failure_mode"):
        EpisodeAnnotation.from_dict(
            {
                "episode_id": "ep-03",
                "task": "navigation",
                "outcome": "aborted",
                "start_seconds": 0,
                "end_seconds": 2.0,
            }
        )


def test_invalid_interval_is_rejected() -> None:
    with pytest.raises(ValueError, match="annotation interval"):
        EpisodeAnnotation.from_dict(
            {
                "episode_id": "ep-04",
                "task": "pick-and-place",
                "outcome": "success",
                "start_seconds": 3.0,
                "end_seconds": 2.0,
            }
        )


def test_whitespace_only_required_strings_are_rejected() -> None:
    with pytest.raises(ValueError, match="episode_id and task are required"):
        EpisodeAnnotation.from_dict(
            {
                "episode_id": "   ",
                "task": "pick-and-place",
                "outcome": "success",
                "start_seconds": 0.0,
                "end_seconds": 1.0,
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
