import gzip
import os
import shutil

from .templating import Templating
from ..base import Environment


class BuildTermsetHierarchy(Templating):
    def pre_process(self, row):
        rows = []
        for x in range(1, 4):
            x_value = row.get(f"f{x}")
            if not x_value:
                break
            for y in range(0, x):
                value = row.get(f"f{y}")
                if not value:
                    break
                for relation in value.split(";"):
                    rows.append(
                        {
                            "child_code": row[f"r{x}"],
                            "relation_filter": relation.strip(),
                            "parent_code": row[f"r{y}"],
                        }
                    )
        return rows

    def run(self, environment: Environment):
        self.logger.info("Generating termset hierarchies ...")
        super().run(environment)
        folderpath = environment.config.get("template_output_path")
        file_path = os.path.join(folderpath, self._output_filename)
        filename_dest = f"{self._output_filename}.gz"
        filepath_dest = os.path.join(folderpath, filename_dest)
        with gzip.open(filepath_dest, "wb") as gz_file:
            self.logger.info("Zipping %s ...", self._output_filename)
            with open(file_path, "rb") as ttl_file:
                shutil.copyfileobj(ttl_file, gz_file)
            os.remove(file_path)
        self.logger.info("Created %s", filename_dest)
