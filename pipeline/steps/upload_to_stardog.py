import os
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
        url = f"{environment.config.get("stardog_endpoint")}/{environment.config.get("stardog_database")}?graph={environment.config.get("stardog_graph_uri")}"
        self.logger.info(f"Uploading to {url} started...")
        with stardog.Connection(**connection_details) as connection:
            self.logger.info(f"Connection to {url} established...")
            connection.begin()
            for filename in filenames:
                filepath = os.path.join(directory, filename)
                connection.add(
                    stardog.content.File(filepath),
                    environment.config.get("stardog_graph_uri"),
                )
                self.logger.info(f"Added {filepath} to {url}")
            connection.commit()
        self.logger.info(f"Connection to {url} closed")
        self.logger.info(f"Uploading to {url} completed")
