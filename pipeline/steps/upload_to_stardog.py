import os
import stardog

from ..base import Step, Environment


class UploadToStardog(Step):
    def __init__(self, graph: str, directory: str = None, filepaths: list[str] = None):
        super().__init__()
        self._graph = graph
        self._filepaths = []
        if directory is None and filepaths is None:
            raise ValueError("You must provide a directory or filepaths")
        elif directory is not None and filepaths is not None:
            raise ValueError("Please provide only one of directory or filepaths")
        elif directory is not None:
            self._filepaths = [
                os.path.join(dirpath, filename)
                for (dirpath, dirnames, filenames) in os.walk(directory)
                for filename in filenames
            ]
        elif filepaths is not None:
            self._filepaths = filepaths

    def run(self, environment: Environment):
        connection_details = {
            "database": environment.config.get("stardog_database"),
            "endpoint": environment.config.get("stardog_endpoint"),
            "username": environment.config.get("stardog_username"),
            "password": environment.config.get("stardog_password"),
        }
        url = f"{environment.config.get('stardog_endpoint')}/{environment.config.get('stardog_database')}?graph={self._graph}"
        self.logger.info(f"Uploading to {url} started...")
        with stardog.Connection(**connection_details) as connection:
            self.logger.info(f"Connection to {url} established...")
            connection.begin()
            for filepath in self._filepaths:
                connection.add(
                    stardog.content.File(filepath),
                    self._graph,
                )
                self.logger.info(f"Added {filepath} to {url}")
            connection.commit()
        self.logger.info(f"Connection to {url} closed")
        self.logger.info(f"Uploading to {url} completed")
