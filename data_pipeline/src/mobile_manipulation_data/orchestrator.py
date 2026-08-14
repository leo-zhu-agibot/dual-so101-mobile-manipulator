"""Dependency-injected perception-planning-execution task state machine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class Stage(str, Enum):
    NAVIGATE = "navigate"
    PERCEIVE = "perceive"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"


class Navigator(Protocol):
    def navigate(self, goal: Any) -> bool: ...


class Perception(Protocol):
    def locate(self, label: str) -> Any | None: ...

    def verify_grasp(self, label: str) -> bool: ...


class Manipulator(Protocol):
    def plan_pick(self, target: Any) -> Any | None: ...

    def execute(self, plan: Any) -> bool: ...


@dataclass(frozen=True, slots=True)
class TaskTrace:
    stage: Stage
    success: bool
    detail: str


@dataclass(frozen=True, slots=True)
class TaskResult:
    success: bool
    traces: tuple[TaskTrace, ...]
    failure_stage: Stage | None = None


class PickTaskOrchestrator:
    """Run navigation -> perception -> MoveIt plan -> execution -> verification."""

    def __init__(self, navigator: Navigator, perception: Perception, manipulator: Manipulator):
        self.navigator = navigator
        self.perception = perception
        self.manipulator = manipulator

    def run(self, navigation_goal: Any, object_label: str) -> TaskResult:
        traces: list[TaskTrace] = []
        if not self.navigator.navigate(navigation_goal):
            traces.append(TaskTrace(Stage.NAVIGATE, False, "Nav2 goal failed"))
            return TaskResult(False, tuple(traces), Stage.NAVIGATE)
        traces.append(TaskTrace(Stage.NAVIGATE, True, "base reached manipulation pose"))

        target = self.perception.locate(object_label)
        if target is None:
            traces.append(TaskTrace(Stage.PERCEIVE, False, f"{object_label} not found"))
            return TaskResult(False, tuple(traces), Stage.PERCEIVE)
        traces.append(TaskTrace(Stage.PERCEIVE, True, "target transformed into base frame"))

        plan = self.manipulator.plan_pick(target)
        if plan is None:
            traces.append(TaskTrace(Stage.PLAN, False, "MoveIt returned no collision-free plan"))
            return TaskResult(False, tuple(traces), Stage.PLAN)
        traces.append(TaskTrace(Stage.PLAN, True, "time-parameterized trajectory available"))

        if not self.manipulator.execute(plan):
            traces.append(TaskTrace(Stage.EXECUTE, False, "trajectory controller rejected execution"))
            return TaskResult(False, tuple(traces), Stage.EXECUTE)
        traces.append(TaskTrace(Stage.EXECUTE, True, "trajectory execution completed"))

        verified = self.perception.verify_grasp(object_label)
        traces.append(TaskTrace(Stage.VERIFY, verified, "post-grasp observation evaluated"))
        return TaskResult(verified, tuple(traces), None if verified else Stage.VERIFY)

