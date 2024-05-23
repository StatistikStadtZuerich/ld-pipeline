import os
from ..interfaces.services import TemplateEngine, DbConnection, CompressionEngine
from typing import TYPE_CHECKING
from jinja2 import Environment as JinjaEnv, FileSystemLoader
import mysql.connector
import gzip
import re
from urllib.parse import quote
from rdflib import Literal

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

        def remove_umlauts(text: str) -> str:
            translate_table = str.maketrans(
                {
                    "Ä": "A",
                    "Ö": "O",
                    "Ü": "U",
                    "ä": "a",
                    "ö": "o",
                    "ü": "u",
                }
            )
            return text.translate(translate_table)

        def uri_encode_filter(value: str) -> str:
            value = remove_umlauts(value)
            value = re.sub(r"[^A-Za-z0-9-]", "", value)
            return quote(value)

        def literal_encode_filter(value: str) -> str:
            value = value.replace("\r", " ").replace("\n", " ").strip()
            value = re.sub(r"\s+", " ", value)
            return Literal(value).n3()

        self._output_filepath = output_filepath
        self._output_file = None
        self._env = JinjaEnv(
            loader=FileSystemLoader(environment.config.get("template_path"))
        )
        self._env.filters["uri_encode"] = uri_encode_filter
        self._env.filters["literal_encode"] = literal_encode_filter
        self._template = self._env.get_template(template_filename)

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
        os.makedirs(os.path.dirname(self._output_filepath), exist_ok=True)
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


class GzipEngine(CompressionEngine):
    def __init__(self, environment: "Environment"):
        super().__init__()
        self._output_path = environment.config.get("compression_output_path")

    def compress(self, filepath: str, filename: str):
        with open(filepath, "rb") as f_in, gzip.open(
            f"{self._output_path}{filename}.gz", "wb"
        ) as f_out:
            f_out.writelines(f_in)
        self.logger.info(f"Successfully compressed {self._output_path}{filename}.gz")
