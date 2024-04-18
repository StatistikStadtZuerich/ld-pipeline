import os
import shutil
import unittest
from unittest.mock import MagicMock
from pipeline.steps import Templating
from pipeline.base import Environment, Env
from tests.unit.test import UnitTest


class TestTemplating(unittest.TestCase):
    def test_ttl_templating(self):
        tmp_dir = UnitTest.abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        env.get_config_value = MagicMock(return_value=UnitTest.abs_path("tmp/"))

        try:
            csv_filepath = UnitTest.abs_path("data/sample.csv")
            template_filename = "ttl_template.jinja"
            output_filename = "test_output.ttl"

            template = Templating(template_filename, output_filename, csv_filepath)
            template.run(env)

            content = open(
                UnitTest.abs_path("tmp/" + output_filename),
                "r",
            ).read()
            expected_content = open(
                UnitTest.abs_path("data/expected_content.ttl"), "r"
            ).read()
            self.assertEqual(content, expected_content)

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
