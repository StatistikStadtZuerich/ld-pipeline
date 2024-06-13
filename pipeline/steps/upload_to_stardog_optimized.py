import os
import stardog
import glob
import shutil
from datetime import datetime

from ..base import Step, Environment, Utils

class UploadToStardogOptimized(Step):
    def __init__(self):
        super().__init__()
        self._utils = Utils()

    def run(self, environment: Environment):
        cert_path = environment.config.get("stardog_cert_path")
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        stardog_database = environment.config.get("stardog_database")
        connection_details = {
            "endpoint": environment.config.get("stardog_endpoint"),
            "username": environment.config.get("stardog_username"),
            "password": environment.config.get("stardog_password"),
        }
        output_folder = environment.config.get("template_output_path")
        output_folder_tmp = output_folder + '/tmp'
        output_folder_done = output_folder + '/done'
        os.makedirs(output_folder_tmp, exist_ok=True)
        os.makedirs(output_folder_done, exist_ok=True)
        url = f"{environment.config.get("stardog_endpoint")}/{environment.config.get("stardog_database")}?graph={environment.config.get("stardog_graph_uri")}"
        
        files = glob.glob(os.path.join(output_folder, "*.gz"))
        try:
            with stardog.Admin(**connection_details) as admin:
                with stardog.Connection(stardog_database, **connection_details) as connection:
                    self._utils.print_formatted(f"Connection to {url} established...")
                    connection.begin()
                    for filepath in files:
                        filename = os.path.basename(filepath)
                        filepath_tmp = f"{output_folder_tmp}/{filename}"
                        shutil.move(filepath, filepath_tmp)
                        self._utils.print_formatted(f"Adding {filename}")
                        connection.add(
                            stardog.content.File(filepath_tmp, content_type="text/turtle"),
                            environment.config.get("stardog_graph_uri"),
                        )
                    self._utils.print_formatted("Commit transaction ...")
                    connection.commit()
                    for filepath in files:
                        filename = os.path.basename(filepath)
                        filepath_tmp = f"{output_folder_tmp}/{filename}"
                        filepath_done = f"{output_folder_done}/{filename}"
                        shutil.move(filepath_tmp, filepath_done)
                    self._utils.print_formatted("Done")
        except Exception as e:
            self._utils.print_formatted(f"Ein Fehler ist aufgetreten: {e}", error=True)
