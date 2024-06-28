import os
import uuid
import gzip
import shutil
from datetime import datetime

from pipeline.base import Step, Environment, Utils
from pipeline.steps.ldview import LdViewBuilder, LdViewSerializer


class ViewsStep(Step):
    def __init__(self, env):
        super().__init__()
        self._utils = Utils()
        self._env = env

    def run(self, environment: Environment):
        serializer = LdViewSerializer(environment)

        self._utils.print_formatted("Start building ld-views")

        for view in LdViewBuilder(environment, self._env).build_all():
            self._utils.print_formatted(f"Start building ld-view {view.id}")
            serializer.serialize(view)
            self._utils.print_formatted(f"Written ld-view {view.id}")

        folderpath = environment.config.get("template_output_path")
        folderpath_ldviews = os.path.join(folderpath, "ldviews")
        uniqid = str(uuid.uuid4())
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        filename_dest = f"{self._env}_ldview_{timestamp}_{uniqid}.nt.gz"
        filepath_dest = os.path.join(folderpath, filename_dest)
        with gzip.open(filepath_dest, "wb") as gz_file:
            for filename in os.listdir(folderpath_ldviews):
                self._utils.print_formatted(f"Zipping {filename} ...")
                if filename.endswith(".ttl"):
                    file_path = os.path.join(folderpath_ldviews, filename)
                    with open(file_path, "rb") as ttl_file:
                        shutil.copyfileobj(ttl_file, gz_file)
                    os.remove(file_path)
        self._utils.print_formatted(f"Created {filename_dest}")
