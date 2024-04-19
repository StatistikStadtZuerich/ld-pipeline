from ..base import Base
from typing import Dict, TYPE_CHECKING
from abc import abstractmethod

if TYPE_CHECKING:
    from ..base import Environment


class ContextManager(Base):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, *exc_details):
        pass


class DbConnection(ContextManager):
    def __init__(self, environment: "Environment"):
        pass

    @abstractmethod
    def query(self, data):
        pass


class TemplateEngine(ContextManager):
    def __init__(
        self, environment: "Environment", template_filename: str, output_filepath: str
    ):
        pass

    @abstractmethod
    def template(self, data: Dict):
        pass
