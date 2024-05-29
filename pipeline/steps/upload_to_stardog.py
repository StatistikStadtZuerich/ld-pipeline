import os
import stardog

from ..base import Step, Environment


class UploadToStardog(Step):
    def __init__(self):
        super().__init__()

    def run(self, environment: Environment):
        connection_details = {
            "database": environment.config.get("stardog_db"),
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
                connection.add(
                    stardog.content.File(os.path.join(directory, filename)),
                    environment.config.get("stardog_graph_uri"),
                )
                i += 1
            connection.commit()
            self.logger.info(
                f"Added {i} file{"s" if i!=1 else ""} to {environment.config.get("stardog_url")}."
            )
