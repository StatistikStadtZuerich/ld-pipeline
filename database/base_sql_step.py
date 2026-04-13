import pathlib
from abc import ABC
from typing import List, Callable

from pipeline.base import Step, Environment
from jinja2 import Environment as JinjaEnv, FileSystemLoader, Template


class BaseSQLStep(Step, ABC):
    def __init__(
        self,
        sql_dirs: List[str],
    ):
        super().__init__()
        self._sql_dirs = sql_dirs

    def _get_sql_files(self) -> List[pathlib.Path]:
        return sorted(
            [
                filepath
                for path in self._sql_dirs
                for pattern in ("*.sql", "*.sql.jinja")
                for filepath in pathlib.Path(path).glob(pattern)
            ]
        )

    @staticmethod
    def render_sql_file(
        environment: Environment, input_file: pathlib.Path
    ) -> str | None:
        if input_file.suffix == ".sql":
            return input_file.read_text(encoding="utf-8")
        elif input_file.suffix == ".jinja":
            return BaseSQLStep._create_jinja_engine(environment, input_file).render()
        else:
            return None

    @staticmethod
    def _create_jinja_engine(
        environment: Environment, template_file: pathlib.Path
    ) -> Template:
        _jinja = BaseSQLStep._init_jinja_env(environment)
        _jinja.loader = FileSystemLoader(template_file.parent.absolute().as_posix())
        return _jinja.get_template(template_file.name)

    @staticmethod
    def render_sql(environment: Environment, template: str) -> str:
        _jinja = BaseSQLStep._init_jinja_env(environment)
        return _jinja.from_string(template).render()

    @staticmethod
    def _init_jinja_env(environment: Environment) -> JinjaEnv:
        _jinja = JinjaEnv(
            trim_blocks=True,
            lstrip_blocks=True,
        )
        _jinja.filters["pipe_table_name"] = BaseSQLStep._fq_sql(environment.pipe_table_name)
        _jinja.filters["table_name"] = BaseSQLStep._fq_sql(environment.table_name)
        _jinja.filters["view_name"] = BaseSQLStep._fq_sql(environment.view_name)

        return _jinja

    @staticmethod
    def _fq_sql(delegate: Callable[..., str]) -> Callable[..., str]:
        def wrapper(value: str, fqa: bool = True, square_brackets: bool = True) -> str:
            parts = value.split('.')
            if fqa and len(parts) == 1:
                parts.insert(0, 'dbo')
            parts[-1] = delegate(parts[-1])
            if square_brackets:
                return '].['.join(parts)
            else:
                return '.'.join(parts)
        return wrapper