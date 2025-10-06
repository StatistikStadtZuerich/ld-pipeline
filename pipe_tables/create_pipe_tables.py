import time
from pathlib import Path
from pipeline.base import Step, Environment, Utils


class InitPipeTables(Step):
    def __init__(self, env):
        super().__init__()
        self._env = env
        self._utils = Utils()
        self._sql_dir = "sql/INT/pipe_tables"

    def run(self, environment: Environment, tables=None):

        start_time = time.time()
        self._utils.print_formatted(f"Initializing pipe tables for {self._env.upper()} ...")

        if tables is None:
            tables = [f.stem for f in self._sql_dir.glob("*.sql")]
        else:
            self._utils.print_formatted(f"Using provided table list: {tables}")  
        print(environment)     
        self._create_pipe_tables(environment, tables)

        end_time = time.time()
        execution_time = end_time - start_time
        self._utils.print_formatted(
            f"Execution time for initializing pipe tables: {execution_time:.2f} seconds"
        )

    def _create_pipe_tables(self, environment, tables):
        with environment.get_db_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    for tablename in tables:
                        sql_file = self._sql_dir / f"{tablename}.sql"
                        if not sql_file.exists():
                            raise FileNotFoundError(f"No SQL file found for {tablename} at {sql_file}")

                        sql = sql_file.read_text(encoding="utf-8")

                        self._utils.print_formatted(
                            f"Executing {sql_file.name} for pipe_{tablename} ..."
                        )
                        cursor.execute(sql)
                        self._utils.print_formatted("Done")

                connection.commit()
            except Exception:
                connection.rollback()
                raise