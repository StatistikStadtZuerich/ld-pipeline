import gzip
import os
import shutil

from ..base import Step, Environment


class Copy(Step):
    """
    The Copy step reads the source file and writes its contents to the destination file,
    creating it if it doesn’t exist, and overwriting it if it does.
    """

    def __init__(self, source, target, options=None):
        """
        Copy file from source to target
        :param source absolute filepath (or relative to runner file)
        :param target absolute filepath (or relative to runner file)
        """
        super().__init__()
        self._source = source
        self._target = target
        self._options = options or {}

    def run(self, environment: Environment):
        out_dir = environment.config.get("output_path")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, self._target)
        self.logger.info(f"Copy {self._source} to {out_file}")
        shutil.copyfile(self._source, out_file)

        filename_dest = self._target + ".gz"
        filepath_dest = os.path.join(out_dir, filename_dest)
        with gzip.open(filepath_dest, "wb") as gz_file:
            self.logger.info(f"Zipping {self._target} ...")
            with open(out_file, "rb") as ttl_file:
                shutil.copyfileobj(ttl_file, gz_file)
            os.remove(out_file)
        self.logger.info(f"Created {filename_dest}")
