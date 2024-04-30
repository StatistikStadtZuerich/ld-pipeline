from ..base import Base
from typing import Dict
from abc import abstractmethod


class ContextManager(Base):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, *exc_details):
        pass


class DbConnection(ContextManager):
    @abstractmethod
    def query(self, data):
        pass


class TemplateEngine(ContextManager):
    @abstractmethod
    def template(self, data: Dict):
        pass
