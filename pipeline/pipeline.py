import logging
import sys
from .base import Environment, Env, Step
from .steps import Copy


class StepFactory:

    def __init__(self):
        self._classes = {
            'copy': Copy
        }

    def get_instance_for(self, name) -> Step:
        if name in self._classes:
            return self._classes[name]()
        else:
            raise RuntimeError(f'no step for name "{name}"')

    def list_names(self):
        return [key for key in self._classes.keys()]


class Pipeline:

    __step_factory = StepFactory()

    def __init__(self, env: Env):
        self._environment = Environment(env)
        logger_config = {
            'encoding': 'utf-8',
            'level': logging.getLevelName(self._environment.get_config_value('logger.log_level'))
        }
        if self._environment.get_config_value('logger.log_to_file', bool, True):
            logger_config['filename'] = self._environment.get_config_value('logger.filename')
        else:
            logger_config['stream'] = sys.stdout

        logging.basicConfig(**logger_config)

    def run(self, *steps: Step):
        for step in steps:
            step.run(self._environment)

    def step(self, name: str):
        Pipeline.__step_factory.get_instance_for(name).run(self._environment)

    @staticmethod
    def step_names():
        return Pipeline.__step_factory.list_names()
