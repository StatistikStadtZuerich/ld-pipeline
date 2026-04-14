import difflib
import pathlib
import re
import pytest

from database import InitPipeTables
from pipeline.base import Environment, Env
from pipeline.steps import CreateViewsFromSQL
from tests.unit.utils import TestUtils


class TestSqlScriptTemplating:
    _prod = Environment(Env.prod)
    _int = Environment(Env.int)

    def test_pipe_hdb(self):
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
        self.assert_sql_equal(
            _int_sql, _int_rendered, "INT SQL does not match expected SQL"
        )

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
        self.assert_sql_equal(
            _prod_sql, _prod_rendered, "PROD SQL does not match expected SQL"
        )

    def test_pipe_hdb_datenobjekte(self):
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
        self.assert_sql_equal(
            _int_sql, _int_rendered, "INT SQL does not match expected SQL"
        )

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
        self.assert_sql_equal(
            _prod_sql, _prod_rendered, "PROD SQL does not match expected SQL"
        )

    @staticmethod
    def _get_templates(template_dir: str) -> list[pathlib.Path]:
        _step = CreateViewsFromSQL(
            [TestUtils.abs_path(f"../../sql/shared/{template_dir}")]
        )
        return [f for f in _step._get_sql_files() if f.suffix == ".jinja"]

    @pytest.mark.parametrize(
        "template", _get_templates("view_definition"), ids=lambda t: t.name
    )
    # @pytest.mark.parametrize("env_name", [Env.int, Env.prod])
    @pytest.mark.parametrize("env_name", [Env.int])
    def test_view_definitions(self, env_name: Env, template: pathlib.Path):
        env = Environment(env_name)
        _step = CreateViewsFromSQL(
            [TestUtils.abs_path("../../sql/shared/view_definition")]
        )

        _expected_path = pathlib.Path(
            TestUtils.abs_path(
                f"../../sql/{env.name}/view_definition/{template.name[:-6]}"
            )
        )
        if not _expected_path.exists():
            _expected_path.write_text(
                f"""-- FIXME: This file was generated as placeholder.\n--   Verify that it's correct and remove this header.\n\n{_step.render_sql_file(env, template)}""",
                encoding="utf-8",
            )
            pytest.skip(
                f"Expected file {_expected_path} does not exist, template generated"
            )

        _expected = _expected_path.read_text(encoding="utf-8")
        _rendered = _step.render_sql_file(env, template)
        self.assert_sql_equal(
            _expected,
            _rendered,
            f"{env.name.upper()} SQL does not match expected SQL for {template.name}",
        )

    @pytest.mark.parametrize(
        "template", _get_templates("pipe_tables"), ids=lambda t: t.name
    )
    @pytest.mark.parametrize("env_name", [Env.int, Env.prod])
    def test_pipe_tables(self, env_name: Env, template: pathlib.Path):
        env = Environment(env_name)
        _step = InitPipeTables([TestUtils.abs_path("../../sql/shared/pipe_tables")])

        _expected_path = pathlib.Path(
            TestUtils.abs_path(
                f"../../sql/{env.name}/pipe_tables/{env.table_name(template.name[:-10])}.sql"
            )
        )
        if not _expected_path.exists():
            _expected_path.write_text(
                f"""-- FIXME: This file was generated as placeholder.\n--   Verify that it's correct and remove this header.\n\n{_step.render_sql_file(env, template)}""",
                encoding="utf-8",
            )
            pytest.skip(
                f"Expected file {_expected_path} does not exist, template generated"
            )

        _expected = _expected_path.read_text(encoding="utf-8")
        _rendered = _step.render_sql_file(env, template)
        self.assert_sql_equal(
            _expected,
            _rendered,
            f"{env.name.upper()} SQL does not match expected SQL for {template.name}",
        )

    @pytest.mark.parametrize("env_name", [Env.int, Env.prod])
    def test_pipe_tables_templating(self, env_name: Env):
        env = Environment(env_name)

        def template_exists(tmpl_name: str) -> bool:
            return pathlib.Path(
                TestUtils.abs_path(
                    f"../../sql/shared/pipe_tables/{tmpl_name}.sql.jinja"
                )
            ).exists()

        sql_files = pathlib.Path(
            TestUtils.abs_path(f"../../sql/{env.name}/pipe_tables")
        ).glob("*.sql")

        for sql_file in sql_files:
            table_name = sql_file.name[:-4]
            if not (
                template_exists(table_name)
                or template_exists(table_name.removesuffix(f"_{env.table_suffix}"))
            ):
                pytest.fail(f"Missing template for {sql_file.name}")

    @pytest.mark.parametrize("env_name", [Env.int, Env.prod])
    def test_view_definition_templating(self, env_name: Env):
        env = Environment(env_name)

        def template_exists(tmpl_name: str) -> bool:
            return pathlib.Path(
                TestUtils.abs_path(
                    f"../../sql/shared/view_definition/{tmpl_name}.sql.jinja"
                )
            ).exists()

        sql_files = pathlib.Path(
            TestUtils.abs_path(f"../../sql/{env.name}/view_definition")
        ).glob("*.sql")

        for sql_file in sql_files:
            table_name = sql_file.name[:-4]
            if not (
                template_exists(table_name)
                or template_exists(table_name.removesuffix(f"_{env.view_suffix}"))
            ):
                pytest.fail(f"Missing template for {sql_file.name}")

    def test_sql_rendering(self):
        expected = "SELECT * FROM [dbo].[view_observation_int]"
        template = "SELECT * FROM [{{ 'view_observation' | view_name }}]"
        rendered = CreateViewsFromSQL.render_sql(
            Environment(Env.int), template
        )
        assert expected == rendered

        view_name = "view_room"
        expected = f"SELECT * FROM [dbo].[{view_name}]"
        template = f"SELECT * FROM [{{{{ '{view_name}' | view_name }}}}]"
        rendered = CreateViewsFromSQL.render_sql(
            Environment(Env.prod), template
        )
        assert expected == rendered

    @staticmethod
    def assert_sql_equal(expected, actual, msg=""):
        def normalize(sql: str) -> str:
            sql = sql + "\n"
            sql = sql.replace("\r\n", "\n")  # Windows line endings
            sql = sql.replace("\r", "\n")  # alte Mac line endings
            sql = sql.strip("\ufeff")  # BOM
            sql = re.sub(
                r"\n[ \t]+\n", "\n\n", sql
            )  # Leerzeilen mit Whitespace → echte Leerzeile
            sql = re.sub(r"\n{3,}", "\n\n", sql)  # 3+ Leerzeilen → max. eine
            return sql.strip()

        _expected = normalize(expected)
        _actual = normalize(actual)

        if _expected == _actual:
            return

        diffs = difflib.unified_diff(
            _expected.splitlines(keepends=True),
            _actual.splitlines(keepends=True),
            fromfile="expected",
            tofile="actual",
            n=2,  # Zeilen Kontext
        )
        diff = "".join(diffs)
        pytest.fail(f"{msg}\n{diff}")
