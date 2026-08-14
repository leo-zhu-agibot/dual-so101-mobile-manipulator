"""Small deterministic behavior-cloning baseline for pipeline smoke tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True, slots=True)
class BCEvaluation:
    samples: int
    mean_squared_error: float
    max_absolute_error: float
    bound_violation_rate: float


class RidgeBCPolicy:
    """Linear action regressor with L2 regularization and explicit bounds."""

    def __init__(self, weights: np.ndarray, action_low: np.ndarray, action_high: np.ndarray):
        self.weights = np.asarray(weights, dtype=np.float64)
        self.action_low = np.asarray(action_low, dtype=np.float64)
        self.action_high = np.asarray(action_high, dtype=np.float64)

    @classmethod
    def fit(
        cls,
        observations: np.ndarray,
        actions: np.ndarray,
        *,
        ridge: float = 1e-4,
        action_low: np.ndarray | None = None,
        action_high: np.ndarray | None = None,
    ) -> "RidgeBCPolicy":
        observations = np.asarray(observations, dtype=np.float64)
        actions = np.asarray(actions, dtype=np.float64)
        if observations.ndim != 2 or actions.ndim != 2 or len(observations) != len(actions):
            raise ValueError("observations/actions must be aligned 2-D arrays")
        features = np.column_stack([observations, np.ones(len(observations))])
        gram = features.T @ features
        regularizer = ridge * np.eye(gram.shape[0])
        regularizer[-1, -1] = 0.0
        weights = np.linalg.solve(gram + regularizer, features.T @ actions)
        low = np.full(actions.shape[1], -1.0) if action_low is None else np.asarray(action_low)
        high = np.full(actions.shape[1], 1.0) if action_high is None else np.asarray(action_high)
        if np.any(high <= low):
            raise ValueError("action_high must exceed action_low")
        return cls(weights, low, high)

    def predict(self, observations: np.ndarray, *, clip: bool = True) -> np.ndarray:
        observations = np.asarray(observations, dtype=np.float64)
        features = np.column_stack([observations, np.ones(len(observations))])
        actions = features @ self.weights
        return np.clip(actions, self.action_low, self.action_high) if clip else actions

    def evaluate(self, observations: np.ndarray, actions: np.ndarray) -> BCEvaluation:
        raw = self.predict(observations, clip=False)
        clipped = np.clip(raw, self.action_low, self.action_high)
        error = clipped - np.asarray(actions)
        violation = np.any((raw < self.action_low) | (raw > self.action_high), axis=1)
        return BCEvaluation(
            samples=len(error),
            mean_squared_error=float(np.mean(error**2)),
            max_absolute_error=float(np.max(np.abs(error))),
            bound_violation_rate=float(np.mean(violation)),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, weights=self.weights, action_low=self.action_low, action_high=self.action_high)

    @classmethod
    def load(cls, path: Path) -> "RidgeBCPolicy":
        with np.load(path) as payload:
            return cls(payload["weights"], payload["action_low"], payload["action_high"])

