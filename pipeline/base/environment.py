import os
import re
from datetime import datetime, UTC

from ..interfaces.services import DbConnection
from .base import Base
from .config import Config, Env
from .mmsql_service import MSSQLDbConnection
from .services import GzipEngine, JinjaTemplateEngine, MySQLDbConnection


class Environment(Base):
    def __init__(
        self, env: Env, config_files: list[os.PathLike] | None = None, run_id: str | None = None
    ):
        super().__init__()
        self._env = env
        self._config = Config(env, config_files)
        self._run_id = run_id or datetime.now(UTC).strftime("%Y-%m-%d-%H-%M-%S")

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def config(self) -> Config:
        return self._config

    @property
    def name(self) -> str:
        return self._env.name

    @property
    def table_suffix(self) -> str:
        if self._env.upper() in ["PROD", "DEV"]:
            return "FINAL"
        else:
            return "TEST"

    @property
    def view_suffix(self) -> str:
        return self.name

    def table_name(self, table_name: str) -> str:
        match re.sub(r"^\d+_", "", table_name).removeprefix("pipe_"):
            case "HDB" | "HDBDatenobjekte":
                return f"{table_name}_{self.table_suffix}"
            case _:
                return table_name

    def pipe_table_name(self, table_name: str) -> str:
        return f"{table_name}_{self.name}"

    def view_name(self, view_name: str) -> str:
        if self._env.upper() in ["PROD", "DEV"]:
            return view_name
        else:
            return f"{view_name}_{self.view_suffix}"

    def get_db_connection(self) -> DbConnection:
        """
        Returns the db connection for the environment
        :return: a database connection
        """
        _db_type = self._config.get("db_type")
        self.logger.info("Initializing db connection for %s", _db_type)
        if _db_type == "mssql":
            return MSSQLDbConnection(self)
        elif _db_type == "mysql":
            return MySQLDbConnection(self)
        else:
            raise NotImplementedError(f"Database '{_db_type}' is not supported")

    def get_template_engine(
        self, template_filename: str, output_filepath: str | None = None
    ) -> JinjaTemplateEngine:
        """
        Returns the template engine for the environment, the template file, and the defined output
        :param template_filename: the template file that is used by the engine
        :param output_filepath: the output file where the templated data will be written in
        :return: a jinja template engine
        """
        return JinjaTemplateEngine(self, template_filename, output_filepath)

    def get_compression_engine(self) -> GzipEngine:
        return GzipEngine(self)
