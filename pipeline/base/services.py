from logging import getLogger
from ..interfaces.services import TemplateEngine, DbConnection
from .environment import Config
from typing import Dict
from jinja2 import Environment, FileSystemLoader


class MSSQLDbConnection(DbConnection):
    """TODO defined the interface methods for DB connections"""

    def __init__(self, config: Config):
        super().__init__()
        self._config = config

    def query(self, data):
        """
        TODO just a simple stub
        """
        return data

    def open(self):
        pass

    def close(self):
        pass


class JinjaTemplateEngine(TemplateEngine):
    """TODO defined the interface methods for TemplateEngine"""

    def __init__(self, config: Config, template_filename: str, output_filepath: str):
        self._config = config
        self._env = Environment(loader=FileSystemLoader(config.get("template_path")))
        self._template = self._env.get_template(template_filename)
        self._output_filepath = output_filepath
        self._output_file = None
        self.logger = getLogger(__name__)

    def template(self, data: Dict):
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
