from ..interfaces.services import TemplateEngine, DbConnection
from typing import TYPE_CHECKING
from jinja2 import Environment as JinjaEnv, FileSystemLoader
import mysql.connector

if TYPE_CHECKING:
    from .environment import Environment


class MSSQLDbConnection(DbConnection):
    def __init__(self, environment: "Environment"):
        super().__init__()
        self._config = environment.config

    def query(self, query: str):
        """
        Executes query and returns cursor.
        """
        self._cursor.execute(query)
        return self._cursor

    def __enter__(self):
        self._connection = mysql.connector.connect(
            host=self._config.get("mysql_host"),
            database=self._config.get("mysql_database"),
            user=self._config.get("mysql_user"),
            password=self._config.get("mysql_password"),
        )
        self._cursor = self._connection.cursor(dictionary=True)
        self.logger.info("Database connection established...")
        return self

    def __exit__(self, *exc_details):
        self._connection.close()
        self.logger.info("Database connection closed.")


class JinjaTemplateEngine(TemplateEngine):
    def __init__(
        self, environment: "Environment", template_filename: str, output_filepath: str
    ):
        super().__init__()
        self._env = JinjaEnv(
            loader=FileSystemLoader(environment.config.get("template_path"))
        )
        self._template = self._env.get_template(template_filename)
        self._output_filepath = output_filepath
        self._output_file = None

    def template(self, data):
        content = self._template.render(data)
        try:
            characters_wrote = self._output_file.write(content + "\n")
            self.logger.info(
                "Successfully wrote "
                + str(characters_wrote)
                + " characters in "
                + self._output_filepath
            )
        except Exception as e:
            self.logger.error("Caught:", e)
            raise

    def __enter__(self):
        self._output_file = open(file=self._output_filepath, mode="a", encoding="utf-8")
        return self

    def __exit__(self, *exc_details):
        if not self._output_file:
            self.logger.warning(
                "File is not yet opened. Please open the output file first."
            )
        elif self._output_file.closed:
            self.logger.debug("File already closed.")
        else:
            self._output_file.close()
