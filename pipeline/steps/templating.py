import os
import pathlib
from typing import Dict, Any

from database import BaseSQLStep
from ..base import Step, Environment


class Templating(Step):
    def __init__(
        self,
        template_filename: str,
        output_filename: str,
        sql_view_name: str,
        sql_filepath: str | None = None,
        options: Dict[str, Any] | None = None,
    ):
        super().__init__()
        self._template_filename = template_filename
        self._output_filename = output_filename
        self._sql_filepath = sql_filepath
        self._sql_view_name = sql_view_name
        self._options = options or {}

    def _load_sql_query(self, enviroment: Environment):
        if self._sql_filepath is None:
            return BaseSQLStep.render_sql(
                enviroment,
                f"SELECT * FROM '{{ '{self._sql_view_name}' | view_name }}'",
            )
        else:
            return BaseSQLStep.render_sql_file(
                enviroment,
                pathlib.Path(self._sql_filepath),
            )

    def pre_process(self, row):
        return [row]

    def run(self, environment: Environment):
        output_filepath = os.path.join(
            environment.config.get("template_output_path"), self._output_filename
        )

        query = self._load_sql_query(environment)

        with environment.get_db_connection() as connection:
            with connection.query(query) as cursor:
                with environment.get_template_engine(
                    self._template_filename, output_filepath
                ) as template_engine:
                    self.logger.info(f"Started templating to {output_filepath}...")
                    for row in cursor:
                        for r in self.pre_process(row):
                            template_engine.template(r)
                    self.logger.info(
                        f"Successfully completed templating to {output_filepath}"
                    )
