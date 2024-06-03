import os
from alive_progress import alive_bar

from ..base import Step, Environment


class Templating(Step):
    def __init__(self, template_filename: str, output_filename: str, sql_filepath: str):
        super().__init__()
        self._template_filename = template_filename
        self._output_filename = output_filename
        self._sql_filepath = sql_filepath

    def run(self, environment: Environment):
        output_filepath = os.path.join(
            environment.config.get("template_output_path"), self._output_filename
        )

        with environment.get_db_connection() as connection:
            with open(self._sql_filepath) as sql_file:
                with connection.query(sql_file.read()) as cursor:
                    with environment.get_template_engine(
                        self._template_filename, output_filepath
                    ) as template_engine:
                        list = cursor.fetchall()
                        with alive_bar(
                            cursor.rowcount,
                            title=f"Templating {output_filepath}",
                            length=50,
                            spinner=None,
                            receipt=False,
                            enrich_print=False,
                        ) as bar:
                            for row in list:
                                template_engine.template(row)
                                bar()
                        self.logger.info(f"Successfully created {output_filepath}")
