from typing import Dict

from .base import Environment, Base, StepDefinition


class Pipeline(Base):
    """
    The Pipeline allows to run steps in the defined environment
    """

    def __init__(
        self, environment: Environment, steps: Dict[str, StepDefinition] = None
    ):
        """
        initializes environment for pipeline and configures logger
        :param env: an environment
        """
        super().__init__()
        self._environment = environment
        self._steps = steps or {}
        self.logger.info("Initialized pipeline for '%s'", self._environment.name)

    def execute(self, step: str) -> None:
        _step = self._steps.get(step)
        if _step is None:
            raise NotImplementedError("Step '%s' not found" % step)
        self.run(_step)

    def run(self, *steps: StepDefinition):
        """
        run all given steps
        :param *steps all given are executed on the given order
        """
        for step in steps:
            self.step(step)

    def step(self, step: StepDefinition):
        """
        run single step
        :param step: the step to run
        """
        self.logger.info(
            "Running step '%s' (%s)", step.name, step.step.__class__.__name__
        )
        step.step.run(self._environment)
        self.logger.info("Completed step '%s'", step.name)
