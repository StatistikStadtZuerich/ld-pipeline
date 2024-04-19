from ..interfaces.services import TemplateEngine, DbConnection
from typing import Dict, TYPE_CHECKING
from jinja2 import Environment as JinjaEnv, FileSystemLoader
import pymssql

if TYPE_CHECKING:
    from .environment import Environment


class MSSQLDbConnection(DbConnection):
    """TODO defined the interface methods for DB connections"""

    def __init__(self, environment: "Environment"):
        self._config = environment.config

    def query(self, query: str):
        """
        executes query and return cursor.
        """
        with self._connection.cursor(as_dict=True) as cursor:
            cursor.execute(query)
            return cursor

    def open(self):
        self._connection = pymssql.connect(
            server=self._config.get("database", "host"),
            user=self._config.get("database", "user"),
            password=self._config.get("database", "password"),
            database=self._config.get("database", "database"),
        )

    def close(self):
        self._connection.close()


class JinjaTemplateEngine(TemplateEngine):
    """TODO defined the interface methods for TemplateEngine"""

    def __init__(
        self, environment: "Environment", template_filename: str, output_filepath: str
    ):
        self._env = JinjaEnv(
            loader=FileSystemLoader(environment.config.get("template_path"))
        )
        self._template = self._env.get_template(template_filename)
        self._output_filepath = output_filepath
        self._output_file = None

    def template(self, data: Dict):
        content = self._template.render(data)
        if not self._output_file.closed:
            characters_wrote = self._output_file.write(content + "\n")
            self.logger.info(
                "Successfully wrote "
                + str(characters_wrote)
                + " characters in "
                + self._output_filepath
            )
        else:
            self.logger.debug(
                "File is closed! Please open the file first and call the template function again."
            )

    def open(self):
        self._output_file = open(file=self._output_filepath, mode="a", encoding="utf-8")

    def close(self):
        if not self._output_file:
            self.logger.debug(
                "File is not yet opened. Please open the output file first."
            )
        elif self._output_file.closed:
            self.logger.debug("File already closed.")
        else:
            self._output_file.close()
