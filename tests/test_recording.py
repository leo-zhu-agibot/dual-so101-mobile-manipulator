from pathlib import Path

from mobile_manipulation_data.recording import build_record_command


def test_record_command_uses_contract_topics(tmp_path: Path) -> None:
    contract = tmp_path / "contract.yaml"
    contract.write_text(
        "topics:\n"
        "  - {name: /joint_states}\n"
        "  - {name: /head_rgbd/color/image_raw}\n"
    )
    command = build_record_command(Path("bags/episode-01"), contract, storage="mcap")
    assert command[:7] == ["ros2", "bag", "record", "--storage", "mcap", "--output", "bags/episode-01"]
    assert command[-2:] == ["/joint_states", "/head_rgbd/color/image_raw"]

