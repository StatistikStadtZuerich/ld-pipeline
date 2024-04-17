from ..interfaces.services import TemplateEngine, DbConnection
from .environment import Config
from typing import Dict
from jinja2 import Environment, FileSystemLoader


class DbConnection(DbConnection):
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


class TemplateEngine(TemplateEngine):
    """TODO defined the interface methods for TemplateEngine"""

    def __init__(self, config: Config, template_filename: str, output_filename: str):
        self._config = config
        self._env = Environment(loader=FileSystemLoader(config.get("template_path")))
        self._template = self._env.get_template(template_filename)
        self._output_path = config.get("output_path") + output_filename

    def template(self, data: Dict):
        content = self._template.render(data)
        if not self._output_file.closed:
            characters_wrote = self._output_file.write(content + "\n")
            print(
                "Successfully wrote "
                + str(characters_wrote)
                + " characters in "
                + self._output_path
            )
        else:
            print(
                "File ist closed. Please open the file first and call the template function again."
            )

    def open(self):
        self._output_file = open(file=self._output_path, mode="a", encoding="utf-8")

    def close(self):
        self._output_file.close()
