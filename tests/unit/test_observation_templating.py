import os
import shutil
from unittest.mock import Mock, MagicMock

from pipeline.base import Environment, Env, StepDefinition
from pipeline.steps import create_templating
from tests.unit.utils import TestUtils


def test_observation_templating():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env = Environment(Env.test)
    env.config.get = Mock(
        side_effect=lambda name, _return_type=str, fallback=None: {
            "template_output_path": TestUtils.abs_path("tmp"),
            "template_path": TestUtils.abs_path("../../pipeline/templates"),
        }.get(name, fallback)
    )
    env.get_db_connection = MagicMock()
    env.get_db_connection().__enter__().query().__enter__.return_value = [
        {
            "uri": "BEW001-ABCDEF01-XXX-XXX-XXX-XXX-R30000-Z2022A",
            "cube_ids": "BEW001OD1003",
            "measure": "BEW001",
            "value": "12345.5",
            "time_code": "Z2022A",
            "time": "2022-12-31",
            "room_code": "R30000",
            "prop1_code_short": "GES",
            "prop1_code": "XYDEF0",
            "prop2_code_short": "XXX",
            "prop2_code": "XXX",
            "prop3_code_short": "XXX",
            "prop3_code": "XXX",
            "prop4_code_short": "XXX",
            "prop4_code": "XXX",
            "prop5_code_short": "XXX",
            "prop5_code": "XXX",
            "number_groups": 1,
            "status": "DEFINITIV",
            "modified": "2023-01-15",
        }
    ]

    sql_filepath = TestUtils.abs_path("data/sample_observation.sql")
    output_filename = "test_observation_output.ttl"

    try:
        step_def = StepDefinition(
            "observationTemplating",
            create_templating(
                env,
                "observation.ttl.jinja",
                output_filename,
                "view_observation",
                sql_filepath,
            ),
        )
        step_def.step.run(env)

        actual = open(
            os.path.join(TestUtils.abs_path("tmp"), output_filename), encoding="utf-8"
        ).read()
        expected = open(
            TestUtils.abs_path("data/expected_content_observation.ttl"), encoding="utf-8"
        ).read()
        TestUtils.assert_text_equals(expected, actual)
    finally:
        shutil.rmtree(tmp_dir)
