import os
import requests

from ..base import Step, Environment


class UploadToFuseki(Step):
    def __init__(self):
        super().__init__()

    def run(self, environment: Environment):
        directory = environment.config.get("compression_output_path")
        filenames = next(os.walk(directory))[2]
        url = f"{environment.config.get('fuseki_endpoint')}/{environment.config.get('fuseki_dataset')}/data?{environment.config.get('fuseki_graph')}"
        self.logger.info(f"Uploading to {url} started...")
        for filename in filenames:
            filepath = os.path.join(directory, filename)
            with open(filepath, "rb") as file_data:
                response = requests.put(
                    url=url,
                    data=file_data.read(),
                    auth=(
                        environment.config.get("fuseki_username"),
                        environment.config.get("fuseki_password"),
                    ),
                    headers={
                        "Content-Type": "text/turtle",
                        "Content-Encoding": "gzip",
                    },
                )
                if response.status_code == 200:
                    self.logger.info(f"Added {filepath} to {url}")
                else:
                    self.logger.error(f"{response.status_code}: {response.text}")
        self.logger.info(f"Uploading to {url} completed")
