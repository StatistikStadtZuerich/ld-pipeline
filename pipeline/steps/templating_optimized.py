import os
import re
from datetime import datetime
import uuid
import gzip
import shutil
import time

from ..base import Step, Environment, Utils


class TemplatingOptimized(Step):
    def __init__(
        self,
        template_filename: str,
        output_filename: str,
        sql_filepath: str,
        options={},
    ):
        super().__init__()
        self._template_filename = template_filename
        self._output_filename = output_filename
        self._sql_filepath = sql_filepath
        self._options = options
        self._utils = Utils()

    def process_triples(self, tablename, cursor, template, output_folder):
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
            self._utils.print_formatted("Downloading data ...")
            cursor.execute(batch_query)
            rows = cursor.fetchall()
            if not rows:
                self._utils.print_formatted("No rows left.")
                running = False
                break
            number_rows = len(rows)
            number_rows_total += number_rows
            self._utils.print_formatted(
                f"{number_rows} rows downloaded in the {counter}. iteration."
            )

            self._utils.print_formatted("Generating triples ...")
            for row in rows:
                counter_rows += 1
                triples = template.render(row)
                batch.append(triples)
            self._utils.print_formatted("done")
            
            end_time = time.time()
            iteration_time = end_time - start_time
            iteration_durations.append(iteration_time)

            if len(batch) >= write_batch_size:
                uniqid = str(uuid.uuid4())
                filename = f"{env}_{tablename}_{timestamp}_{uniqid}.ttl.gz"
                dest_file = f"{output_folder}/{filename}"
                dest_file_tmp = f"{output_folder_tmp}/{filename}"
                self._utils.print_formatted(
                    f"Writing batch data to {os.path.basename(dest_file_tmp)} ..."
                )
                with gzip.open(dest_file_tmp, "at") as f_out:
                    f_out.write("\n".join(batch) + "\n")
                batch.clear()
                shutil.move(dest_file_tmp, dest_file)
                self._utils.print_formatted("File is created.")
            offset += db_batch_size

            if len(iteration_durations) > 10:
                iteration_durations.pop(0)
            adaptive_threshold = sum(iteration_durations) / len(iteration_durations)
            self._utils.print_formatted(f"{counter}. iteration took {iteration_time:.2f} seconds.")
            if iteration_time > adaptive_threshold:
                delay_increase = (iteration_time - adaptive_threshold) * 0.5
                delay = min(max_delay, delay + delay_increase)
            else:
                delay_decrease = (adaptive_threshold - iteration_time) * 0.5
                delay = max(0, delay - delay_decrease)
            if delay > 0:
                self._utils.print_formatted(f"Delaying next iteration by {delay:.2f} seconds to reduce load.")
                time.sleep(delay)
            self._utils.print_formatted(f"{counter}. iteration is finished.")

        if batch:
            uniqid = str(uuid.uuid4())
            filename = f"{env}_{tablename}_{timestamp}_{uniqid}.ttl.gz"
            dest_file = f"{output_folder}/{filename}"
            dest_file_tmp = f"{output_folder_tmp}/{filename}"
            self._utils.print_formatted(
                f"Writing remaining batch data to {os.path.basename(dest_file_tmp)} ..."
            )
            with gzip.open(dest_file_tmp, "at") as f_out:
                f_out.write("\n".join(batch) + "\n")
            shutil.move(dest_file_tmp, dest_file)
            self._utils.print_formatted("File is created.")

    def run(self, environment: Environment):
        output_filepath = os.path.join(
            environment.config.get("template_output_path"), self._output_filename
        )
        env = self._options["env"]
        only_vb_cubes = environment.config.get("only_vb_cubes")

        output_folder = os.path.dirname(output_filepath)

        with environment.get_db_connection() as connection:
            with open(self._sql_filepath) as sql_file:
                query = sql_file.read()
                match = re.search(r"FROM\s+([^\s^;]+)", query, re.IGNORECASE)
                tablename = None
                if match:
                    tablename = match.group(1)
                if not tablename:
                    self._utils.print_formatted(
                        f"Invalid query in {self._sql_filepath}", error=True
                    )
                    return

                with connection.cursor() as cursor:
                    like_conditions = ""

                    if (
                        only_vb_cubes == "true"
                        and tablename == f"view_observation_{env}"
                    ):
                        cursor.execute(
                            f"SELECT DISTINCT t.cube_id FROM view_vb_source_{env} t"
                        )
                        rows = cursor.fetchall()
                        if len(rows) > 0:
                            like_conditions = " OR ".join(
                                [f"cube_ids LIKE '%{row['cube_id']}%'" for row in rows]
                            )
                            like_conditions = f"( {like_conditions} )"
                            self._utils.print_formatted(
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

                    self._utils.print_formatted(
                        f"Creating temporary table #{tablename} ..."
                    )
                    cursor.execute(query_tmp_table)
                    self._utils.print_formatted(
                        "Creating an index on the _sort_order column ..."
                    )
                    cursor.execute(
                        f"CREATE INDEX idx_sort_order ON #{tablename} (_sort_order)"
                    )
                    self._utils.print_formatted("done")

                    with environment.get_template_engine(
                        self._template_filename, output_filepath
                    ) as template_engine:
                        template = template_engine.get_template()
                        self.process_triples(tablename, cursor, template, output_folder)