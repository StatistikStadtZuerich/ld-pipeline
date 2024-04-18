from ..base.base import Base
from ..base.environment import Config
from typing import Dict
from abc import abstractmethod


class Closeable(Base):
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass


class DbConnection(Closeable):
    """TODO defined the interface methods for DB connections"""

    def __init__(self, config: Config):
        pass

    @abstractmethod
    def query(self, data):
        """
        TODO just a simple stub
        """
        pass


class TemplateEngine(Closeable):
    """TODO defined the interface methods for TemplateEngine"""

    def __init__(self, config: Config, template_filename: str, output_filename: str):
        pass

    @abstractmethod
    def template(self, data: Dict):
        pass
