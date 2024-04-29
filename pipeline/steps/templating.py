from typing import Dict
from ..base import Step, Environment
import csv


class Templating(Step):
    def __init__(self, template_filename: str, output_filename: str, csv_filepath: str):
        super().__init__()
        self._template_filename = template_filename
        self._output_filename = output_filename
        self._csv_filepath = csv_filepath

    def run(self, environment: Environment):
        output_filepath = environment.config.get("output_path") + self._output_filename

        with environment.get_template_engine(
            self._template_filename, output_filepath
        ) as templating_engine:
            with open(self._csv_filepath, newline="") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    templating_engine.template(self._preprocess(row))

    def _preprocess(self, row: Dict) -> Dict:
        return row
