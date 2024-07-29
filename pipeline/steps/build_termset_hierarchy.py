import os
import uuid
import gzip
import shutil
from datetime import datetime

from .templating import Templating
from ..base import Environment, Utils


class BuildTermsetHierarchy(Templating):
    def pre_process(self, row):
        rows = []
        for x in range(1, 4):
            for y in range(0, x):
                for relation in row[f"f{y}"].split(";"):
                    rows.append(
                        {
                            "child_code": row[f"r{x}"],
                            "relation_filter": relation.strip(),
                            "parent_code": row[f"r{y}"],
                        }
                    )
        return rows

    def run(self, environment: Environment):
        utils = Utils()
        utils.print_formatted("Generating termset hierarchies ...")
        super().run(environment)
        file_path = os.path.join(
            environment.config.get("template_output_path"), self._output_filename
        )
        uniqid = str(uuid.uuid4())
        now = datetime.now()
        env = self._options["env"]
        timestamp = now.strftime("%Y%m%d%H%M%S")
        filename_dest = f"{env}_termset_hierarchy_{timestamp}_{uniqid}.ttl.gz"
        folderpath = environment.config.get("template_output_path")
        filepath_dest = os.path.join(folderpath, filename_dest)
        with gzip.open(filepath_dest, "wb") as gz_file:
            utils.print_formatted(f"Zipping {self._output_filename} ...")
            with open(file_path, "rb") as ttl_file:
                shutil.copyfileobj(ttl_file, gz_file)
        utils.print_formatted(f"Created {filename_dest}")
