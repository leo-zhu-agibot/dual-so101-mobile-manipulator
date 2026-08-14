"""Load the generated USD, add a ground plane, and run Isaac Sim physics."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("usd", type=Path)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--steps", type=int, default=0, help="0 runs until the app closes")
    args = parser.parse_args()
    if not args.usd.is_file():
        raise FileNotFoundError(args.usd)

    from isaacsim import SimulationApp

    app = SimulationApp({"headless": args.headless})
    try:
        import omni.usd
        from isaacsim.core.api import World

        omni.usd.get_context().open_stage(str(args.usd.resolve()))
        world = World(stage_units_in_meters=1.0, physics_dt=1.0 / 100.0, rendering_dt=1.0 / 30.0)
        world.scene.add_default_ground_plane()
        world.reset()
        completed = 0
        while app.is_running() and (args.steps == 0 or completed < args.steps):
            world.step(render=not args.headless)
            completed += 1
        print(f"simulation_steps={completed}")
    finally:
        app.close()


if __name__ == "__main__":
    main()

