from .base import Environment, Step, Base


class Pipeline(Base):
    """
    The Pipeline allows to run steps in the defined environment
    """

    def __init__(self, environment: Environment):
        """
        initializes environment for pipeline and configures logger
        :param env: an environment
        """
        super().__init__()
        self._environment = environment
        self.logger.info("Initialized pipeline for '%s'", self._environment.name)

    def run(self, *steps: Step):
        """
        run all given steps
        :param *steps all given are executed on the given order
        """
        for step in steps:
            step.run(self._environment)

    def step(self, step: Step):
        """
        run single step
        :param step: the step to run
        """
        step.run(self._environment)
