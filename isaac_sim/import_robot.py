"""Import the expanded robot URDF into Isaac Sim 4.5+ and save a USD stage.

Run this script with Isaac Sim's python.sh, not the system Python.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("urdf", type=Path, help="Expanded URDF produced by xacro")
    parser.add_argument("--usd", type=Path, default=Path("artifacts/dual_so101_mobile.usd"))
    parser.add_argument("--headless", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.urdf.is_file():
        raise FileNotFoundError(args.urdf)

    from isaacsim import SimulationApp

    app = SimulationApp({"headless": args.headless})
    try:
        import omni.kit.commands
        import omni.usd
        from isaacsim.core.utils.extensions import enable_extension

        enable_extension("isaacsim.asset.importer.urdf")
        enable_extension("isaacsim.ros2.bridge")
        status, import_config = omni.kit.commands.execute("URDFCreateImportConfig")
        if not status:
            raise RuntimeError("Isaac Sim could not create a URDF import configuration")
        import_config.merge_fixed_joints = False
        import_config.fix_base = False
        import_config.make_default_prim = True
        import_config.self_collision = True
        import_config.default_drive_type = 1
        import_config.default_drive_strength = 120.0
        import_config.default_position_drive_damping = 18.0
        status, prim_path = omni.kit.commands.execute(
            "URDFParseAndImportFile",
            urdf_path=str(args.urdf.resolve()),
            import_config=import_config,
            dest_path="",
        )
        if not status:
            raise RuntimeError("URDF import failed")
        args.usd.parent.mkdir(parents=True, exist_ok=True)
        omni.usd.get_context().save_as_stage(str(args.usd.resolve()), None)
        print(f"Imported {prim_path} -> {args.usd}")
    finally:
        app.close()


if __name__ == "__main__":
    main()

