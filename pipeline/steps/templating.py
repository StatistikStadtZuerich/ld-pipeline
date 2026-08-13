import os
import pathlib
import re
from typing import Any

from database import BaseSQLStep

from ..base import Environment, Step

_REFERENCE_NUMBER_VALUE_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")


class Templating(Step):
    def __init__(
        self,
        template_filename: str,
        output_filename: str,
        sql_view_name: str,
        sql_filepath: str | None = None,
        options: dict[str, Any] | None = None,
        reference_numbers: list[str] | set[str] | None = None,
    ):
        super().__init__()
        self._template_filename = template_filename
        self._output_filename = output_filename
        self._sql_filepath = sql_filepath
        self._sql_view_name = sql_view_name
        self._options = options or {}
        self._reference_numbers = reference_numbers

    def _load_sql_query(self, enviroment: Environment):
        if self._sql_filepath is None:
            query = BaseSQLStep.render_sql(
                enviroment,
                f"SELECT * FROM [{{{{ '{self._sql_view_name}' | view_name }}}}]",
            )
        else:
            query = BaseSQLStep.render_sql_file(
                enviroment,
                pathlib.Path(self._sql_filepath),
            )

        if self._reference_numbers:
            for value in self._reference_numbers:
                if not _REFERENCE_NUMBER_VALUE_PATTERN.match(value):
                    raise ValueError(f"Invalid reference_number filter value: {value!r}")
            values = ", ".join(f"'{value}'" for value in self._reference_numbers)
            query = f"SELECT * FROM ({query}) AS filtered WHERE reference_number IN ({values})"

        return query

    def _output_folder(self, environment: Environment) -> str:
        return environment.config.get("template_output_path")

    def pre_process(self, row):
        return [row]

    def run(self, environment: Environment):
        output_filepath = os.path.join(
            self._output_folder(environment), self._output_filename
        )

        query = self._load_sql_query(environment)

        with (
            environment.get_db_connection() as connection,
            connection.query(query) as cursor,
            environment.get_template_engine(
                self._template_filename, output_filepath
            ) as template_engine,
        ):
            self.logger.info(f"Started templating to {output_filepath}...")
            for row in cursor:
                for r in self.pre_process(row):
                    template_engine.template(r)
            self.logger.info(f"Successfully completed templating to {output_filepath}")
