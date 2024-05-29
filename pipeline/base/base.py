import logging
from abc import ABC


class Base(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
