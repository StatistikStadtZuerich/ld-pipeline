import logging
from abc import abstractmethod

from .base import Base
from .environment import Environment


class Step(Base):
    """
    The base class for pipeline steps
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def run(self, environment: Environment):
        """
        This methode is called by the pipeline
        :param environment: the current environment, managed by the pipeline
        """
        pass


class StepDefinition:
    def __init__(self, step: Step, description: str = ""):
        self._step = step
        self._description = description

    @property
    def step(self):
        return self._step

    @property
    def description(self):
        return self._description
