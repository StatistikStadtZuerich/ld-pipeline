import os
import shutil
import unittest
from unittest.mock import MagicMock
from pipeline import Templating, Env
from pipeline.base import Environment


class TestTemplating(unittest.TestCase):
    @staticmethod
    def __abs_path(rel_path):
        return os.path.join(os.path.dirname(__file__), rel_path)

    def test_ttl_templating(self):
        tmp_dir = self.__abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        env.get_config_value = MagicMock(return_value=self.__abs_path("tmp/"))

        try:
            csv_filepath = self.__abs_path("data/sample.csv")
            template_filename = "ttl_template.jinja"
            output_filename = "test_output.ttl"

            template = Templating(template_filename, output_filename, csv_filepath)
            template.run(env)

            content = open(
                self.__abs_path("tmp/" + output_filename),
                "r",
            ).read()
            expected_content = open(
                self.__abs_path("data/expected_content.ttl"), "r"
            ).read()
            self.assertEqual(content, expected_content)

        finally:
            shutil.rmtree(tmp_dir)
