import os
import pathlib
from datetime import datetime
import uuid
import gzip
import shutil
import time
from typing import Dict, Any
from itertools import groupby as itertools_groupby

from database import BaseSQLStep
from ..base import Step, Environment, Utils


class TemplatingOptimized(Step):
    def __init__(
        self,
        template_filename: str,
        output_filename: str,
        sql_view_name: str,
        sql_filepath: str | None = None,
        options: Dict[str, Any] | None = None,
    ):
        super().__init__()
        self._template_filename = template_filename
        self._output_filename = output_filename
        self._sql_view_name = sql_view_name
        self._sql_filepath = sql_filepath
        self._options = options or {}
        self._utils = Utils()

    def _load_sql_query(self, enviroment: Environment):
        if self._sql_filepath is None:
            return BaseSQLStep.render_sql(
                enviroment,
                f"SELECT * FROM [{{{{ '{self._sql_view_name}' | view_name }}}}]",
            )
        else:
            return BaseSQLStep.render_sql_file(
                enviroment,
                pathlib.Path(self._sql_filepath),
            )

    def _write_batch(
        self, batch, output_folder, output_folder_tmp, env, output_table, timestamp
    ):
        """Writes a batch of triples to a gzipped file."""
        uniqid = str(uuid.uuid4())
        filename = f"{env}_{output_table}_{timestamp}_{uniqid}.ttl.gz"
        dest_file = f"{output_folder}/{filename}"
        dest_file_tmp = f"{output_folder_tmp}/{filename}"
        self.logger.info(f"Writing batch data to {os.path.basename(dest_file_tmp)} ...")
        with gzip.open(dest_file_tmp, "at") as f_out:
            f_out.write("\n".join(batch) + "\n")
        shutil.move(dest_file_tmp, dest_file)
        self.logger.info("File is created.")

    def process_triples(self, tablename, cursor, template, output_folder, output_table):
        db_batch_size = 100000
        write_batch_size = 500000
        max_iteration = None
        max_delay = 120

        env = self._options["env"]

        if "db_batch_size" in self._options:
            db_batch_size = self._options["db_batch_size"]
        if "write_batch_size" in self._options:
            write_batch_size = self._options["write_batch_size"]
        if "max_iteration" in self._options:
            max_iteration = self._options["max_iteration"]

        output_folder_tmp = output_folder + "/tmp"
        os.makedirs(output_folder_tmp, exist_ok=True)

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        batch = []

        query = f"SELECT * FROM #{tablename} ORDER BY _sort_order"
        offset = 0
        counter = 0
        counter_rows = 0
        running = True
        number_rows_total = 0
        delay = 0
        iteration_durations = []
        while running:
            counter += 1
            if max_iteration is not None and counter > max_iteration:
                running = False
                break
            start_time = time.time()
            batch_query = (
                f"{query} OFFSET {offset} ROWS FETCH NEXT {db_batch_size} ROWS ONLY"
            )
            self.logger.info("Downloading data ...")
            cursor.execute(batch_query)
            rows = cursor.fetchall()
            if not rows:
                self.logger.info("No rows left.")
                running = False
                break
            number_rows = len(rows)
            number_rows_total += number_rows
            self.logger.info(
                f"{number_rows} rows downloaded in the {counter}. iteration."
            )

            self.logger.info("Generating triples ...")
            for row in rows:
                counter_rows += 1
                triples = template.render(row)
                batch.append(triples)
            self.logger.info("done")

            end_time = time.time()
            iteration_time = end_time - start_time
            iteration_durations.append(iteration_time)

            if len(batch) >= write_batch_size:
                self._write_batch(
                    batch,
                    output_folder,
                    output_folder_tmp,
                    env,
                    output_table,
                    timestamp,
                )
                batch.clear()
            offset += db_batch_size

            if len(iteration_durations) > 10:
                iteration_durations.pop(0)
            adaptive_threshold = sum(iteration_durations) / len(iteration_durations)
            self.logger.info(f"{counter}. iteration took {iteration_time:.2f} seconds.")
            if iteration_time > adaptive_threshold:
                delay_increase = (iteration_time - adaptive_threshold) * 0.5
                delay = min(max_delay, delay + delay_increase)
            else:
                delay_decrease = (adaptive_threshold - iteration_time) * 0.5
                delay = max(0, delay - delay_decrease)
            if delay > 0:
                self.logger.info(
                    f"Delaying next iteration by {delay:.2f} seconds to reduce load."
                )
                time.sleep(delay)
            self.logger.info(f"{counter}. iteration is finished.")

        if batch:
            self._write_batch(
                batch, output_folder, output_folder_tmp, env, output_table, timestamp
            )

    def run(self, environment: Environment):
        output_filepath = os.path.join(
            environment.config.get("template_output_path"), self._output_filename
        )
        output_table = self._output_filename
        env = self._options["env"]
        only_vb_cubes = environment.config.get("only_vb_cubes")

        output_folder = os.path.dirname(output_filepath)

        with environment.get_db_connection() as connection:
            tablename = self._sql_view_name
            query = self._load_sql_query(environment)

            with connection.cursor() as cursor:
                like_conditions = ""

                if only_vb_cubes == "true" and tablename == f"view_observation_{env}":
                    cursor.execute(
                        f"SELECT DISTINCT t.cube_id FROM view_vb_source_{env} t"
                    )
                    rows = cursor.fetchall()
                    if len(rows) > 0:
                        like_conditions = " OR ".join(
                            [f"cube_ids LIKE '%{row['cube_id']}%'" for row in rows]
                        )
                        like_conditions = f"( {like_conditions} )"
                        self.logger.info(
                            "Considering only cubes from the view builder."
                        )

                if len(like_conditions) == 0:
                    query_tmp_table = (
                        f"SELECT *, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS _sort_order INTO #{tablename} "
                        f" FROM ({query}) AS original_query"
                    )
                else:
                    query_tmp_table = (
                        f"SELECT *, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS _sort_order INTO #{tablename}"
                        f" FROM ({query} WHERE ({like_conditions})) AS original_query"
                    )

                self.logger.info(f"Creating temporary table #{tablename} ...")
                cursor.execute(query_tmp_table)
                self.logger.info("Creating an index on the _sort_order column ...")
                cursor.execute(
                    f"CREATE INDEX idx_sort_order ON #{tablename} (_sort_order)"
                )
                self.logger.info("done")

                    with environment.get_template_engine(
                        self._template_filename, output_filepath
                    ) as template_engine:
                        template = template_engine.get_template()
                        self.process_triples(
                            tablename, cursor, template, output_folder, output_table
                        )


class GroupedTemplatingOptimized(TemplatingOptimized):
    """
    Wie TemplatingOptimized, aber gruppiert Rows nach einem Key (z.B. termset_code)
    bevor sie ans Template übergeben werden.

    Benötigt options["group_by"]: der Spaltenname nach dem gruppiert wird.
    Die SQL Query muss nach diesem Spaltenname sortiert sein (ORDER BY termset_code).
    """

    def process_triples(self, tablename, cursor, template, output_folder, output_table):
        db_batch_size = 100000
        write_batch_size = 500000
        env = self._options["env"]
        group_by = self._options["group_by"]  # z.B. "termset_code"

        if "db_batch_size" in self._options:
            db_batch_size = self._options["db_batch_size"]
        if "write_batch_size" in self._options:
            write_batch_size = self._options["write_batch_size"]

        output_folder_tmp = output_folder + "/tmp"
        os.makedirs(output_folder_tmp, exist_ok=True)

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        batch = []

        # Wichtig: ORDER BY group_by damit Gruppen nicht über Batches aufgeteilt werden
        query = f"SELECT * FROM #{tablename} ORDER BY {group_by}, _sort_order"
        offset = 0
        running = True
        leftover_rows = []  # letzte Gruppe des vorherigen Batches

        while running:
            cursor.execute(
                f"{query} OFFSET {offset} ROWS FETCH NEXT {db_batch_size} ROWS ONLY"
            )
            rows = cursor.fetchall()

            if not rows:
                self.logger.info("No rows left.")
                running = False
                # letzte Gruppe noch rendern
                if leftover_rows:
                    triples = template.render({"rows": leftover_rows})
                    batch.append(triples)
                break

            # Rows vom letzten Batch vorne anhängen
            rows = leftover_rows + list(rows)
            leftover_rows = []

            # Letzte Gruppe zurückhalten — könnte im nächsten Batch weitergehen
            last_group_key = rows[-1][group_by]
            safe_rows = [r for r in rows if r[group_by] != last_group_key]
            leftover_rows = [r for r in rows if r[group_by] == last_group_key]

            # Gruppieren und pro Gruppe rendern
            for _, group in itertools_groupby(safe_rows, key=lambda r: r[group_by]):
                triples = template.render({"rows": list(group)})
                batch.append(triples)

            offset += db_batch_size

            if len(batch) >= write_batch_size:
                self._write_batch(
                    batch,
                    output_folder,
                    output_folder_tmp,
                    env,
                    output_table,
                    timestamp,
                )
                batch.clear()

        if batch:
            self._write_batch(
                batch, output_folder, output_folder_tmp, env, output_table, timestamp
            )
