import os
import uuid
import gzip
import shutil
from datetime import datetime

from pipeline.base import Step, Environment, Utils
from pipeline.steps.ldview import LdViewBuilder, LdViewSerializer


class ViewsStep(Step):
    def __init__(self):
        super().__init__()
        self._utils = Utils()

    def run(self, environment: Environment):
        serializer = LdViewSerializer(environment)

        self.logger.info("Start building ld-views")

        for view in LdViewBuilder(environment).build_all():
            self.logger.info(f"Start building ld-view {view.id}")
            serializer.serialize(view)
            self.logger.info(f"Written ld-view {view.id}")

        folderpath = environment.config.get("template_output_path")
        folderpath_ldviews = os.path.join(folderpath, "ldviews")
        uniqid = str(uuid.uuid4())
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        filename_dest = f"{environment.name}_ldview_{timestamp}_{uniqid}.ttl.gz"
        filepath_dest = os.path.join(folderpath, filename_dest)
        with gzip.open(filepath_dest, "wb") as gz_file:
            for filename in os.listdir(folderpath_ldviews):
                self.logger.info(f"Zipping {filename} ...")
                if filename.endswith(".ttl"):
                    file_path = os.path.join(folderpath_ldviews, filename)
                    with open(file_path, "rb") as ttl_file:
                        shutil.copyfileobj(ttl_file, gz_file)
                    os.remove(file_path)
        self.logger.info(f"Created {filename_dest}")
