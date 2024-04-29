import os
import shutil
import unittest
from unittest.mock import Mock
from pipeline.steps import Templating
from pipeline.base import Environment, Env
from tests.unit.utils import TestUtils


class TestTemplating(unittest.TestCase):
    def test_ttl_templating(self):
        tmp_dir = TestUtils.abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        mocked_config = {
            "output_path": TestUtils.abs_path("tmp/"),
            "template_path": TestUtils.abs_path("data/"),
        }

        def side_effect(arg):
            return mocked_config[arg]

        env.config.get = Mock(side_effect=side_effect)

        try:
            csv_filepath = TestUtils.abs_path("data/sample.csv")
            template_filename = "template.ttl.jinja"
            output_filename = "test_output.ttl"

            template = Templating(template_filename, output_filename, csv_filepath)
            template.run(env)

            content = open(
                TestUtils.abs_path("tmp/" + output_filename),
                "r",
            ).read()
            expected_content = open(
                TestUtils.abs_path("data/expected_content.ttl"), "r"
            ).read()
            self.assertEqual(content, expected_content)

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
