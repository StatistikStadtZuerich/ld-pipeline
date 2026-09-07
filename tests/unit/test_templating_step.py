import os
import shutil
from unittest.mock import MagicMock, Mock

from pipeline.base import Env, Environment
from pipeline.steps import Templating
from pipeline.steps.templating import OutputType
from tests.unit.utils import TestUtils


def test_templating():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

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
        Templating(
            template_filename, output_filename, "view_property", OutputType.PUBLIC, sql_filepath=sql_filepath
        ).run(env)

        env.get_db_connection().__enter__().query.assert_called_with(
            TestUtils.read_file(sql_filepath)
        )

        content = TestUtils.gzip_read(
            os.path.join(TestUtils.abs_path("tmp"), OutputType.PUBLIC, output_filename + ".gz")
        )
        expected_content = TestUtils.read_file(
            TestUtils.abs_path("data/expected_content.ttl")
        )
        assert expected_content == content

    finally:
        shutil.rmtree(tmp_dir)
