import unittest
from pipeline import Pipeline, Env, Step
from pipeline.base import Environment


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


class TestPipeline(unittest.TestCase):
    """
    The TestPipeline runs a TestStep 3 times in a row anc tests, if the execution is done correctly
    """
    def test_run(self):
        step = TestStep()
        pipeline = Pipeline(Env.test)
        pipeline.run(step, step, step)
        self.assertEqual(3, step.count)


if __name__ == '__main__':
    unittest.main()
