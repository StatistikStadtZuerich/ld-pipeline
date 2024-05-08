from typing import Dict
from ..base import Step, Environment


class Templating(Step):
    def __init__(self, template_filename: str, output_filename: str, sql_filepath: str):
        super().__init__()
        self._template_filename = template_filename
        self._output_filename = output_filename
        self._sql_filepath = sql_filepath

    def run(self, environment: Environment):
        output_filepath = environment.config.get("output_path") + self._output_filename

        with environment.get_template_engine(
            self._template_filename, output_filepath
        ) as template_engine:
            with environment.get_db_connection() as connection:
                with open(self._sql_filepath) as sql_file:
                    sql = sql_file.read()
                    with connection.query(sql) as cursor:
                        for row in cursor:
                            template_engine.template(row)

    def _preprocess(self, row: Dict) -> Dict:
        return row
