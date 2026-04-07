import pathlib
import re
import time
from typing import List

from database import BaseSQLStep
from pipeline.base import Environment


class InitPipeTables(BaseSQLStep):
    def __init__(self, sql_dirs: List[str]):
        super().__init__(sql_dirs)

    def run(self, environment: Environment, tables=None):
        start_time = time.time()
        self.logger.info(f"Initializing pipe tables for {environment.name.upper()} ...")

        if tables is None:
            tables = self._get_sql_files()
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
                        sql = self.render_sql_file(environment, table)
                        if sql is None:
                            self.logger.error(
                                f"Invalid SQL file: {table}, skipping ..."
                            )
                            continue

                        statements = [
                            s.strip()
                            for s in re.split(r"(?im)^\s*GO\s*$", sql)
                            if s.strip()
                        ]

                        self.logger.info(f"Executing {table.name}...")

                        for stmt in statements:
                            cursor.execute(stmt)

                        self.logger.info("Done")

                connection.commit()
            except Exception:
                connection.rollback()
                raise
