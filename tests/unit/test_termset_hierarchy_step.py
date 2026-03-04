import os
import shutil
import unittest
from unittest.mock import Mock, MagicMock

from pipeline.base import Environment, Env
from pipeline.steps import BuildTermsetHierarchy
from tests.unit.utils import TestUtils


"""
A query like this generated the hierarchy we need (in this case for EIG)

PREFIX schema: <https://schema.org/>
PREFIX schema: <https://schema.org/>
SELECT DISTINCT ?r0 ?f0 ?r1 ?f1 ?r2 ?f2 ?r3 ?f3 WHERE {
  ?o <https://ld.stadt-zuerich.ch/statistics/property/EIG> ?r0.
  ?r0 schema:isPartOf <https://ld.stadt-zuerich.ch/statistics/code/None>.
  ?r0 schema:inDefinedTermSet/schema:name ?f0.
  FILTER(?f0 != "EIG")
  OPTIONAL {
    ?r1 schema:isPartOf ?r0; schema:inDefinedTermSet/schema:name ?f1.
    FILTER(?f1 != "EIG")
    OPTIONAL {
      ?r2 schema:isPartOf ?r1; schema:inDefinedTermSet/schema:name ?f2.
      FILTER(?f2 != "EIG")
      OPTIONAL {
        ?r3 schema:isPartOf ?r2; schema:inDefinedTermSet/schema:name ?f3.
        FILTER(?f3 != "EIG")
      }
    }
  }
}
"""


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
            self.assertEqual(expected_content, content)

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
