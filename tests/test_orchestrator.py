from mobile_manipulation_data.orchestrator import PickTaskOrchestrator, Stage


class FakeNavigator:
    def navigate(self, _goal):
        return True


class FakePerception:
    def locate(self, _label):
        return {"frame": "base_link", "xyz": [0.4, 0.1, 0.2]}

    def verify_grasp(self, _label):
        return True


class FakeManipulator:
    def __init__(self, plan=True):
        self.can_plan = plan
        self.executed = False

    def plan_pick(self, _target):
        return {"trajectory": [1, 2, 3]} if self.can_plan else None

    def execute(self, _plan):
        self.executed = True
        return True


def test_closed_loop_pick_success() -> None:
    result = PickTaskOrchestrator(FakeNavigator(), FakePerception(), FakeManipulator()).run(
        {"frame": "map", "xy": [1.0, 2.0]}, "red_mug"
    )
    assert result.success
    assert [trace.stage for trace in result.traces] == list(Stage)


def test_planning_failure_stops_before_execution() -> None:
    manipulator = FakeManipulator(plan=False)
    result = PickTaskOrchestrator(FakeNavigator(), FakePerception(), manipulator).run({}, "box")
    assert result.failure_stage is Stage.PLAN
    assert not manipulator.executed

