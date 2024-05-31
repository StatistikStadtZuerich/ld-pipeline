import os
from alive_progress import alive_bar
import stardog

from ..base import Step, Environment


class UploadToStardog(Step):
    def __init__(self):
        super().__init__()

    def run(self, environment: Environment):
        connection_details = {
            "database": environment.config.get("stardog_database"),
            "endpoint": environment.config.get("stardog_endpoint"),
            "username": environment.config.get("stardog_username"),
            "password": environment.config.get("stardog_password"),
        }
        directory = environment.config.get("compression_output_path")
        filenames = next(os.walk(directory))[2]

        with stardog.Connection(**connection_details) as connection:
            connection.begin()
            i = 0
            for filename in filenames:
                filepath = os.path.join(directory, filename)
                with alive_bar(
                    spinner="dots",
                    bar=None,
                    stats=None,
                    elapsed="({elapsed})",
                    monitor=None,
                    title=f"Adding {filepath} to {environment.config.get("stardog_database")} (Graph: {environment.config.get("stardog_graph_uri")})",
                    receipt=False,
                    enrich_print=False,
                ):
                    connection.add(
                        stardog.content.File(filepath),
                        environment.config.get("stardog_graph_uri"),
                    )
                self.logger.info(
                    f"Added {filename} to {environment.config.get("stardog_database")} (Graph: {environment.config.get("stardog_graph_uri")})"
                )
                i += 1
            connection.commit()
            self.logger.info(
                f"Successfully added {i} file{"s" if i!=1 else ""} to {environment.config.get("stardog_endpoint")}/{environment.config.get("stardog_database")}?graph={environment.config.get("stardog_graph_uri")}"
            )
