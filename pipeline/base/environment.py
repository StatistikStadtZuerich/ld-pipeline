from typing import Iterator
from contextlib import contextmanager
from .config import Config, Env
from .services import DbConnection, TemplateEngine
from .base import Base


class Environment(Base):
    def __init__(self, env: Env):
        super().__init__()
        self._config = Config(env)

    @contextmanager
    def get_db_connection(self) -> Iterator[DbConnection]:
        """
        Returns the db connection for the environment
        :return: a database connection
        """
        connection = DbConnection(self._config)
        try:
            self.logger.info("establish connection")
            yield connection
        except Exception as e:
            self.logger.error("caught:", e)
            raise
        else:
            self.logger.info("end connection")
        finally:
            self.logger.info("final cleanup connection")

    @contextmanager
    def get_template_engine(
        self, template_filename: str, output_filename: str
    ) -> Iterator[TemplateEngine]:
        """
        Returns the template engine for the environment, the template file and the defined output
        :param template_filename: the template file that is used by the engine
        :param output_filename: the output file where the
        :return:
        """
        engine = TemplateEngine(self._config, template_filename, output_filename)
        try:
            engine.open()
            yield engine
        except Exception:
            raise
        finally:
            engine.close()

    def get_config_value(self, name: str, return_type=str, fallback=None):
        return self._config.get(name, return_type, fallback)
