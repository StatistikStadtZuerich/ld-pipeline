import unittest
from pipeline import Pipeline, Env, Step
from pipeline.base import Environment


class TestStep(Step):
    __test__ = False
    _count = 0

    def run(self, environment: Environment):
        self._count += 1

    @property
    def count(self):
        return self._count


class TestPipeline(unittest.TestCase):
    def test_run(self):
        step = TestStep()
        pipeline = Pipeline(Env.test)
        pipeline.run(step, step, step)
        self.assertEqual(3, step.count)


if __name__ == '__main__':
    unittest.main()
