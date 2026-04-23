from pipeline import Pipeline
from pipeline.base import Environment, Env, Step, StepDefinition


class TestStep(Step):
    """
    The TestStep implements Step and does a simple counting
    """

    __test__ = False
    _count = 0

    def run(self, environment: Environment):
        self._count += 1

    @property
    def count(self):
        return self._count


def test_run():
    """
    The TestPipeline runs a TestStep 3 times in a row anc tests, if the execution is done correctly
    """
    step = StepDefinition(
        "test",
        TestStep(),
    )
    pipeline = Pipeline(Environment(Env.test), {})
    pipeline.run(step, step, step)
    assert 3 == step.step.count
