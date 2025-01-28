from typing import Dict, Self, Any
from abc import abstractmethod

from ..base import Base


class ContextManager(Base):
    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(self, *exc_details) -> None:
        pass


class DbConnection(ContextManager):
    @abstractmethod
    def query(self, data: Dict):
        pass


class TemplateEngine(ContextManager):
    @abstractmethod
    def template(self, data: Any) -> None:
        """This method renders the template with the specified data.

        Args:
            data (Dict): The data argument provides the data to be used in the template in the form of a dictonary.
        """
        pass


class CompressionEngine(Base):
    @abstractmethod
    def compress(self, filepath: str) -> None:
        """Compress the given file to the output path.

        Args:
            filepath (str): The file to be compressed
        """
        pass
