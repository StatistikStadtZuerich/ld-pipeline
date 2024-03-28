from .base import Base
from .environment import Environment
from abc import abstractmethod
import logging


class Step(Base):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def run(self, environment: Environment):
        pass
