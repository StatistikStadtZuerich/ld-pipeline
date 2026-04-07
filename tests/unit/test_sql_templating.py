import pathlib
import unittest

from database import InitPipeTables
from pipeline.base import Environment, Env
from pipeline.steps import CreateViewsFromSQL
from tests.unit.utils import TestUtils


class MyTestCase(unittest.TestCase):
    _prod = Environment(Env.prod)
    _int = Environment(Env.int)

    def test_pipe_HDB(self):
        ## Test INT rendering
        _step = InitPipeTables([])
        _int_sql = _step.render_sql_file(
            self._int,
            pathlib.Path(
                TestUtils.abs_path("../../sql/int/pipe_tables/pipe_HDB_TEST.sql")
            ),
        )
        _int_rendered = _step.render_sql_file(
            self._int,
            pathlib.Path(
                TestUtils.abs_path("../../sql/shared/pipe_tables/pipe_HDB.sql.jinja")
            ),
        )
        self.assertEqual(_int_sql, _int_rendered, "INT SQL does not match expected SQL")

        _prod_sql = _step.render_sql_file(
            self._prod,
            pathlib.Path(
                TestUtils.abs_path("../../sql/prod/pipe_tables/pipe_HDB_FINAL.sql")
            ),
        )
        _prod_rendered = _step.render_sql_file(
            self._prod,
            pathlib.Path(
                TestUtils.abs_path("../../sql/shared/pipe_tables/pipe_HDB.sql.jinja")
            ),
        )
        self.assertEqual(
            _prod_sql, _prod_rendered, "PROD SQL does not match expected SQL"
        )

    def test_pipe_HDBDatenobjekte(self):
        ## Test INT rendering
        _step = InitPipeTables([])
        _int_sql = _step.render_sql_file(
            self._int,
            pathlib.Path(
                TestUtils.abs_path(
                    "../../sql/int/pipe_tables/pipe_HDBDatenobjekte_TEST.sql"
                )
            ),
        )
        _int_rendered = _step.render_sql_file(
            self._int,
            pathlib.Path(
                TestUtils.abs_path(
                    "../../sql/shared/pipe_tables/pipe_HDBDatenobjekte.sql.jinja"
                )
            ),
        )
        self.assertEqual(_int_sql, _int_rendered, "INT SQL does not match expected SQL")

        _prod_sql = _step.render_sql_file(
            self._prod,
            pathlib.Path(
                TestUtils.abs_path(
                    "../../sql/prod/pipe_tables/pipe_HDBDatenobjekte_FINAL.sql"
                )
            ),
        )
        _prod_rendered = _step.render_sql_file(
            self._prod,
            pathlib.Path(
                TestUtils.abs_path(
                    "../../sql/shared/pipe_tables/pipe_HDBDatenobjekte.sql.jinja"
                )
            ),
        )
        self.assertEqual(
            _prod_sql, _prod_rendered, "PROD SQL does not match expected SQL"
        )

    def test_view_definitions(self):
        _step = CreateViewsFromSQL(
            [TestUtils.abs_path("../../sql/shared/view_definition")]
        )
        _templates = [f for f in _step._get_sql_files() if f.suffix == ".jinja"]
        for _template in _templates:
            for _env in [self._int, self._prod]:
                if _env == self._prod:
                    if _template.name.startswith("view_hierarchy"):
                        continue
                    if _template.name.startswith("view_room_hierarchy"):
                        continue
                    if _template.name.startswith("view_vb_measure"):
                        continue
                    if _template.name.startswith("view_vb_view"):
                        continue
                    if _template.name.startswith("view_group_code"):
                        continue
                    if _template.name.startswith("view_measure"):
                        continue
                    if _template.name.startswith("view_room"):
                        continue
                with self.subTest(env=_env, template=_template.name):
                    _expected = pathlib.Path(
                        TestUtils.abs_path(
                            f"../../sql/{_env.name}/view_definition/{_template.name[:-6]}"
                        )
                    ).read_text(encoding="utf-8")
                    _rendered = _step.render_sql_file(_env, _template)
                    self.assertEqualIgnoreWhitespace(
                        _expected,
                        _rendered,
                        f"{_env.name.upper()} SQL does not match expected SQL for {_template.name}",
                    )

    def assertEqualIgnoreWhitespace(self, first: str, second: str, msg: str = None):
        return self.assertEqual(
            first.split(),
            second.split(),
            msg,
        )


if __name__ == "__main__":
    unittest.main()
