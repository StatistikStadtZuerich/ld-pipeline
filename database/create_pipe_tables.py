import pathlib
import re
import time

from database import BaseSQLStep
from pipeline.base import Environment
from pipeline.base.utils import format_duration


class InitPipeTables(BaseSQLStep):
    def __init__(self, sql_dirs: list[str]):
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
            f"Execution time for initializing pipe tables: {format_duration(execution_time)}"
        )

    def _create_pipe_tables(self, environment: Environment, tables: list[pathlib.Path]):
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

                        for i, stmt in enumerate(statements, start=1):
                            try:
                                cursor.execute(stmt)
                            except Exception:
                                self.logger.error(
                                    f"Statement {i}/{len(statements)} failed in {table.name}:\n{stmt}"
                                )
                                raise

                        self.logger.info("Done")

                connection.commit()
            except Exception:
                self.logger.exception(f"Failed while executing {table.name}")
                connection.rollback()
                raise
