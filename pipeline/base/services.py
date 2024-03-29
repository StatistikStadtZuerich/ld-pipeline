from .base import Base
from .environment import Config


class DbConnection(Base):
    """TODO defined the interface methods for DB connections"""

    def __init__(self, config: Config):
        super().__init__()
        self._config = config

    def query(self, data):
        """
        TODO just a simple stub
        """
        return data


class TemplateEngine(Base):
    """TODO defined the interface methods for TemplateEngine"""

    def __init__(self, config: Config, template_filepath: str, output_filepath: str):
        super().__init__()
        self._config = config
