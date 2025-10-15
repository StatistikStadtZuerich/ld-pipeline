import os
import pathlib
import time
from os import PathLike
from typing import List

from pipeline.base import Step, Environment


class InitPipeTables(Step):
    def __init__(self, sql_dirs: List[str]):
        super().__init__()
        self._sql_dirs = sql_dirs

    @staticmethod
    def _list_dir(path: str) -> List[PathLike]:
        return [
            pathlib.Path(os.path.join(path, f))
            for f in os.listdir(path)
            if f.endswith(".sql")
        ]

    def run(self, environment: Environment, tables=None):
        start_time = time.time()
        self.logger.info(f"Initializing pipe tables for {environment.name.upper()} ...")

        if tables is None:
            _x = []
            for _sql_dir in self._sql_dirs:
                _x.extend(self._list_dir(_sql_dir))
            tables = _x
        else:
            self.logger.info(f"Using provided table list: {tables}")
        self.logger.debug(environment)
        self._create_pipe_tables(environment, tables)

        end_time = time.time()
        execution_time = end_time - start_time
        self.logger.info(
            f"Execution time for initializing pipe tables: {execution_time:.2f} seconds"
        )

    def _create_pipe_tables(self, environment: Environment, tables: List[pathlib.Path]):
        with environment.get_db_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    for table in tables:
                        sql = table.read_text(encoding="utf-8")

                        self.logger.info(
                            f"Executing {table.name} for pipe_{table.name.removesuffix('.sql')} ..."
                        )
                        cursor.execute(sql)
                        self.logger.info("Done")

                connection.commit()
            except Exception:
                connection.rollback()
                raise
