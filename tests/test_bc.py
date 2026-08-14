from pathlib import Path

import numpy as np

from mobile_manipulation_data.bc import RidgeBCPolicy


def test_ridge_bc_fits_and_round_trips(tmp_path: Path) -> None:
    rng = np.random.default_rng(17)
    observations = rng.normal(size=(256, 5))
    matrix = rng.normal(scale=0.15, size=(5, 3))
    bias = np.array([0.1, -0.2, 0.05])
    actions = observations @ matrix + bias
    policy = RidgeBCPolicy.fit(
        observations,
        actions,
        ridge=1e-8,
        action_low=np.full(3, -10.0),
        action_high=np.full(3, 10.0),
    )
    evaluation = policy.evaluate(observations, actions)
    assert evaluation.mean_squared_error < 1e-10

    path = tmp_path / "policy.npz"
    policy.save(path)
    restored = RidgeBCPolicy.load(path)
    np.testing.assert_allclose(policy.predict(observations[:8]), restored.predict(observations[:8]))


def test_ridge_bc_reports_action_bound_violations() -> None:
    observations = np.array([[0.0], [1.0], [2.0], [3.0]])
    actions = np.array([[0.0], [0.5], [1.0], [1.5]])
    policy = RidgeBCPolicy.fit(
        observations,
        actions,
        ridge=1e-8,
        action_low=np.array([-0.75]),
        action_high=np.array([0.75]),
    )
    assert policy.evaluate(observations, actions).bound_violation_rate == 0.5
