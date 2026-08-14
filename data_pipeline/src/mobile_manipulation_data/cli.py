from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from mobile_manipulation_data.bag_qc import inspect_bag
from mobile_manipulation_data.bc import RidgeBCPolicy
from mobile_manipulation_data.recording import record_episode


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mobile-data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    qc = subparsers.add_parser("qc", help="validate one rosbag2 episode")
    qc.add_argument("bag", type=Path)
    qc.add_argument("--contract", type=Path, default=Path("data_pipeline/config/bag_contract.yaml"))
    qc.add_argument("--json-out", type=Path)

    record = subparsers.add_parser("record", help="record the configured multimodal topic set")
    record.add_argument("output", type=Path)
    record.add_argument("--contract", type=Path, default=Path("data_pipeline/config/bag_contract.yaml"))
    record.add_argument("--storage", choices=["sqlite3", "mcap"], default="sqlite3")

    train = subparsers.add_parser("train-bc", help="train a deterministic linear BC smoke baseline")
    train.add_argument("dataset", type=Path, help="NPZ with observations and actions arrays")
    train.add_argument("--model-out", type=Path, default=Path("models/ridge_bc.npz"))
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "qc":
        report = inspect_bag(args.bag, args.contract)
        if args.json_out:
            report.write_json(args.json_out)
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        raise SystemExit(0 if report.passed else 2)

    if args.command == "record":
        raise SystemExit(record_episode(args.output, args.contract, storage=args.storage))

    with np.load(args.dataset) as dataset:
        policy = RidgeBCPolicy.fit(dataset["observations"], dataset["actions"])
        evaluation = policy.evaluate(dataset["observations"], dataset["actions"])
    policy.save(args.model_out)
    print(json.dumps(asdict(evaluation), indent=2))


if __name__ == "__main__":
    main()
