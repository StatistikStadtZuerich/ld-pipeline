from .config import Config, Env
from .services import MSSQLDbConnection, JinjaTemplateEngine, GzipEngine
from .base import Base


class Environment(Base):
    def __init__(self, env: Env):
        super().__init__()
        self._config = Config(env)

    @property
    def config(self):
        return self._config

    def get_db_connection(self) -> MSSQLDbConnection:
        """
        Returns the db connection for the environment
        :return: a database connection
        """
        return MSSQLDbConnection(self)

    def get_template_engine(
        self, template_filename: str, output_filepath: str
    ) -> JinjaTemplateEngine:
        """
        Returns the template engine for the environment, the template file and the defined output
        :param template_filename: the template file that is used by the engine
        :param output_filepath: the output file where the templated data will be written in
        :return: a jinja template engine
        """
        return JinjaTemplateEngine(self, template_filename, output_filepath)

    def get_compression_engine(self) -> GzipEngine:
        return GzipEngine(self)
