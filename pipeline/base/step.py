from abc import abstractmethod

from .base import Base
from .environment import Environment


class Step(Base):
    """
    The base class for pipeline steps
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def run(self, environment: Environment):
        """
        This methode is called by the pipeline
        :param environment: the current environment, managed by the pipeline
        """
        pass


class StepDefinition:
    def __init__(self, name: str, step: Step, description: str = ""):
        self._name = name
        self._step = step
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def step(self):
        return self._step

    @property
    def description(self):
        return self._description
