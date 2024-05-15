import stardog
from typing import List
from ..base import Step, Environment


class UploadToStardog(Step):
    def __init__(self, zip_filename: str, input_filenames: List[str] = None):
        super().__init__()
        self._zip_filename = zip_filename

    def run(self, environment: Environment):
        connection_details = {
            "database": environment.config.get("stardog_db"),
            "endpoint": environment.config.get("stardog_endpoint"),
            "username": environment.config.get("stardog_username"),
            "password": environment.config.get("stardog_password"),
        }

        filename = environment.config.get("zip_output_path") + self._zip_filename

        with stardog.Connection(**connection_details) as conn:
            conn.begin()
            conn.add(
                stardog.content.File(filename),
                environment.config.get("stardog_graph_uri"),
            )
            conn.commit()
            # print(conn.select("select * { ?a ?p ?o }"))
