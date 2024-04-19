import logging
import sys
from .base import Environment, Env, Step


class Pipeline:
    """
    The Pipeline allows to run steps in the defined environment
    """

    def __init__(self, env: Env):
        """
        initializes environment for pipeline and configures logger
        :param env: an environment
        """
        self._environment = Environment(env)
        logger_config = {
            "encoding": "utf-8",
            "level": logging.getLevelName(
                self._environment.config.get("logger.log_level")
            ),
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
        if self._environment.config.get("logger.log_to_file", bool, True):
            logger_config["filename"] = self._environment.config.get("logger.filename")
        else:
            logger_config["stream"] = sys.stdout

        logging.basicConfig(**logger_config)

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
