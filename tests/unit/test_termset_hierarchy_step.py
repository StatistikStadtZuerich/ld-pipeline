import os
import shutil
import unittest
from unittest.mock import Mock, MagicMock

from pipeline.base import Environment, Env
from pipeline.steps import BuildTermsetHierarchy
from tests.unit.utils import TestUtils


class TestTermsetHierarchyStep(unittest.TestCase):
    def test_templating(self):
        tmp_dir = TestUtils.abs_path("tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        env = Environment(Env.test)
        env.config.get = Mock(
            side_effect=lambda arg: {
                "template_output_path": TestUtils.abs_path("tmp"),
                "template_path": TestUtils.abs_path("../../pipeline/templates"),
            }[arg]
        )
        env.get_db_connection = MagicMock()
        env.get_db_connection().__enter__().query().__enter__.return_value = [
            {
                "r0": "R30000",
                "f0": "KantonZH; StadtZH",
                "r1": "R00200",
                "f1": "KreiseZH; WahlkreiseZH",
                "r2": "R00023",
                "f2": "QuartiereZH",
                "r3": "R3Z030",
            },
            {
                "r0": "R30000",
                "f0": "KantonZH; StadtZH",
                "r1": "R10000",
                "f1": "KreiseZH; WahlkreiseZH; StadtZHAlt",
                "r2": "R00011",
                "f2": "QuartiereZH",
                "r3": "R3Z004",
            },
        ]

        sql_filepath = TestUtils.abs_path("data/sample.sql")
        template_filename = "raum_hierarchy.ttl.jinja"
        output_filename = "test_output.ttl"

        try:
            BuildTermsetHierarchy(
                template_filename, output_filename, sql_filepath, {"env": "test"}
            ).run(env)

            env.get_db_connection().__enter__().query.assert_called_with(
                open(sql_filepath).read()
            )

            content = open(
                os.path.join(TestUtils.abs_path("tmp"), output_filename)
            ).read()
            expected_content = open(
                TestUtils.abs_path("data/expected_content_hierarchies.ttl")
            ).read()
            self.assertEqual(content, expected_content)

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
