import time

from database import BaseSQLStep
from ..base import Environment


class CreateViewsFromSQL(BaseSQLStep):
    def __init__(self, sql_folder):
        super().__init__(sql_folder)

    def run(self, environment: Environment):
        self.logger.info("Starting to create views from SQL files...")
        start_time = time.time()

        try:
            self._execute_sql_files(environment)
        except Exception as e:
            self.logger.error(f"Error while creating views: {e}")
            raise

        end_time = time.time()
        execution_time = end_time - start_time
        self.logger.info(
            f"Execution time for creating views: {execution_time:.2f} seconds"
        )

    def _execute_sql_files(self, environment: Environment):
        with environment.get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Alle SQL-Dateien im Ordner durchgehen
                for sql_file in self._get_sql_files():
                    self._execute_sql_file(sql_file, cursor, environment)

                connection.commit()

    def _execute_sql_file(self, sql_file, cursor, environment: Environment):
        self.logger.debug(f"Executing SQL file: {sql_file}")

        sql_script = self.render_sql_file(environment, sql_file)

        # SQL-Script anhand von "GO" in Batches aufteilen (Groß-/Kleinschreibung beachten, Zeilenweise!)
        batches = []
        current_batch = []

        for line in sql_script.splitlines():
            if line.strip().upper() == "GO":
                if current_batch:
                    batches.append("\n".join(current_batch))
                    current_batch = []
            else:
                current_batch.append(line)

        # Letzter Batch (falls vorhanden)
        if current_batch:
            batches.append("\n".join(current_batch))

        # Alle Batches einzeln ausführen
        try:
            for batch in batches:
                if batch.strip():  # Nur ausführen, wenn nicht leer
                    cursor.execute(batch)
            self.logger.info(f"{sql_file} executed successfully.")
        except Exception as e:
            self.logger.error(f"Failed to execute {sql_file}: {e}")
            raise
