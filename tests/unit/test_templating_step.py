import os
import shutil
import unittest
from unittest.mock import Mock, MagicMock

from pipeline.base import Environment, Env
from pipeline.steps import Templating
from tests.unit.utils import TestUtils


class TestTemplatingStep(unittest.TestCase):
    def test_templating(self):
        tmp_dir = TestUtils.abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        env.config.get = Mock(
            side_effect=lambda arg: {
                "template_output_path": TestUtils.abs_path("tmp"),
                "template_path": TestUtils.abs_path("data"),
            }[arg]
        )
        env.get_db_connection = MagicMock()
        env.get_db_connection().__enter__().query().__enter__.return_value = [
            {"property_code": "ÜBG", "title": "Arbeitslosengrad   "},
            {"property_code": "ABT", "title": "Abteilung"},
        ]

        sql_filepath = TestUtils.abs_path("data/sample.sql")
        template_filename = "template.ttl.jinja"
        output_filename = "test_output.ttl"

        try:
            Templating(template_filename, output_filename, sql_filepath).run(env)

            env.get_db_connection().__enter__().query.assert_called_with(
                open(sql_filepath).read()
            )

            content = open(
                os.path.join(TestUtils.abs_path("tmp"), output_filename)
            ).read()
            expected_content = open(
                TestUtils.abs_path("data/expected_content.ttl")
            ).read()
            self.assertEqual(content, expected_content)

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
