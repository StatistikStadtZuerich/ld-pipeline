import logging
import sys
from .base import Environment, Env, Step
from .steps import Copy


class StepFactory:
    """
    The StepFactory enables to list all registered Steps and a step instance by name
    """

    def __init__(self):
        """
        Steps must be registered, so they can executed as single steps from the command line
        """
        self._classes = {
            'copy': Copy
        }

    def get_step_for(self, name) -> Step:
        """
        get the step class for a given name
        :param name: the name that identifies the step class in the registration
        """
        if name in self._classes:
            return self._classes[name]()
        else:
            raise RuntimeError(f'no step for name "{name}"')

    def list_names(self):
        """
        returns all registered step names
        """
        return [key for key in self._classes.keys()]


class Pipeline:
    """
    The Pipeline allows to run steps in the defined environment
    """

    __step_factory = StepFactory()

    def __init__(self, env: Env):
        """
        initializes environment for pipeline and configures logger
        :param env: an environment
        """
        self._environment = Environment(env)
        logger_config = {
            'encoding': 'utf-8',
            'level': logging.getLevelName(self._environment.get_config_value('logger.log_level')),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
        if self._environment.get_config_value('logger.log_to_file', bool, True):
            logger_config['filename'] = self._environment.get_config_value('logger.filename')
        else:
            logger_config['stream'] = sys.stdout

        logging.basicConfig(**logger_config)

    def run(self, *steps: Step):
        """
        run all given steps
        :param *steps all given are executed on the given order
        """
        for step in steps:
            step.run(self._environment)

    def step(self, name: str):
        """
        run single step given by name
        :param name: the name of the step that is executed
        """
        Pipeline.__step_factory.get_step_for(name).run(self._environment)

    @staticmethod
    def step_names():
        """
        list all registered step names
        """
        return Pipeline.__step_factory.list_names()
