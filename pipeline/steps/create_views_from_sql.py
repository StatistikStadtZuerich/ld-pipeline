import os
import time

from ..base import Step, Environment, Utils

class CreateViewsFromSQL(Step):
    def __init__(self, env):
        super().__init__()
        self._env = env
        self._utils = Utils()

        # Pfad zum Ordner mit den View-SQL-Dateien (zwei Ebenen höher + sql/view_definition)
        current_dir = os.getcwd()
        self._sql_folder = os.path.abspath(os.path.join(current_dir, 'sql','int', 'view_definition'))

    def run(self, environment: Environment):
        self._utils.print_formatted('Starting to create views from SQL files...')
        start_time = time.time()

        try:
            self._execute_sql_files(environment)
        except Exception as e:
            self._utils.print_formatted(f"Error while creating views: {e}")
            raise

        end_time = time.time()
        execution_time = end_time - start_time
        self._utils.print_formatted(f"Execution time for creating views: {execution_time:.2f} seconds")

    def _execute_sql_files(self, environment: Environment):
        with environment.get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Alle SQL-Dateien im Ordner durchgehen
                for filename in sorted(os.listdir(self._sql_folder)):
                    if filename.lower().endswith('.sql'):
                        file_path = os.path.join(self._sql_folder, filename)
                        self._utils.print_formatted(f"Executing SQL file: {filename}")

                        with open(file_path, 'r', encoding='utf-8') as file:
                            sql_script = file.read()

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
                                self._utils.print_formatted(f"{filename} executed successfully.")
                            except Exception as e:
                                self._utils.print_formatted(f"Failed to execute {filename}: {e}")
                                raise


                connection.commit()
