from typing import List
import zipfile
from os import walk
from ..base import Step, Environment


class Zipping(Step):
    def __init__(self, output_filename: str, input_filenames: List[str] = None):
        super().__init__()
        self._input_filenames = input_filenames
        self._output_filename = output_filename

    def run(self, environment: Environment):
        zip_filepath = environment.config.get("zip_output_path") + self._output_filename
        if self._input_filenames is None:
            self._input_filenames = next(
                walk(environment.config.get("template_output_path"))
            )[2]
        with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as myzip:
            self.logger.info("Zipping started...")
            for filename in self._input_filenames:
                myzip.write(
                    environment.config.get("template_output_path") + filename, filename
                )
        self.logger.info(f"Zipping completed. Created {zip_filepath}")
