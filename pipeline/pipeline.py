import time

from .base import Base, Environment, StepDefinition


class Pipeline(Base):
    """
    The Pipeline allows to run steps in the defined environment
    """

    def __init__(
        self, environment: Environment, steps: dict[str, StepDefinition] | None = None
    ):
        """
        initializes environment for pipeline and configures logger
        :param environment: an environment
        """
        super().__init__()
        self._environment = environment
        self._steps = steps or {}
        self.logger.info("Initialized pipeline for '%s'", self._environment.name)

    def execute(self, step: str) -> None:
        _step = self._steps.get(step)
        if _step is None:
            raise NotImplementedError(f"Step '{step}' not found")
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
        started_at = time.perf_counter()
        try:
            step.step.run(self._environment)
            duration = time.perf_counter() - started_at
            self.logger.info("Completed step '%s' in %.2f seconds", step.name, duration)
        except Exception as e:
            duration = time.perf_counter() - started_at
            self.logger.error("Step '%s' failed after %.2f seconds: %s", step.name, duration, e)
            raise