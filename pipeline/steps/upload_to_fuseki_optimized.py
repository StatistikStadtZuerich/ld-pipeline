import os
import requests
import glob
import shutil

from ..base import Step, Environment, Utils


class UploadToFusekiOptimized(Step):
    def __init__(self):
        super().__init__()
        self._utils = Utils()

    def run(self, environment: Environment):
        output_folder = environment.config.get("template_output_path")
        output_folder_tmp = output_folder + "/tmp"
        output_folder_done = output_folder + "/done"
        os.makedirs(output_folder_tmp, exist_ok=True)
        os.makedirs(output_folder_done, exist_ok=True)
        url = f"{environment.config.get("fuseki_endpoint")}/{environment.config.get("fuseki_dataset")}/data?{environment.config.get("fuseki_graph")}"

        files = glob.glob(os.path.join(output_folder, "*.gz"))
        for filepath in files:
            filename = os.path.basename(filepath)
            filepath_tmp = f"{output_folder_tmp}/{filename}"
            filepath_done = f"{output_folder_done}/{filename}"
            shutil.move(filepath, filepath_tmp)
            self._utils.print_formatted(f"Uploading {filename}")
            with open(filepath_tmp, "rb") as file_data:
                response = requests.post(
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
                    proxies={"http": None, "https": None},
                )

                if response.status_code == 200:
                    shutil.move(filepath_tmp, filepath_done)
                    self._utils.print_formatted("OK")
                else:
                    self._utils.print_formatted(
                        f"{response.status_code}: {response.text}",
                        error=True
                    )
