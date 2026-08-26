import gzip
import os
import shutil

from .templating import Templating
from ..base import Environment


class FastRunObservationTemplating(Templating):
    """
    Rendert eine Observation-Menge (veröffentlicht oder embargoed), optional
    gefiltert auf bestimmte Referenznummern, in ein gzip-File. Schreibt in den
    'locked/'-Unterordner von template_output_path.

    Nicht über TemplatingOptimized (Batching) erstellt, damit keine
    _batchNNN.ttl.gz-Dateien entstehen.
    """

    def _output_folder(self, environment: Environment) -> str:
        return os.path.join(super()._output_folder(environment), "locked")

    def run(self, environment: Environment):
        self.logger.info("Generating FastRun observations ...")
        super().run(environment)

        folderpath = self._output_folder(environment)
        file_path = os.path.join(folderpath, self._output_filename)
        if not os.path.exists(file_path):
            self.logger.info(
                "No observations found, skipping zipping of %s",
                self._output_filename,
            )
            return

        filename_dest = f"{self._output_filename}.gz"
        filepath_dest = os.path.join(folderpath, filename_dest)
        with gzip.open(filepath_dest, "wb") as gz_file:
            self.logger.info("Zipping %s ...", self._output_filename)
            with open(file_path, "rb") as ttl_file:
                shutil.copyfileobj(ttl_file, gz_file)
            os.remove(file_path)
        self.logger.info("Created %s", filename_dest)
