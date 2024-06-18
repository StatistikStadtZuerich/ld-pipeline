import os

from ..base import Step, Environment


class Compressing(Step):
    def __init__(self, directory: str = None, filepaths: list[str] = None):
        super().__init__()
        self._files = []
        if directory is None and filepaths is None:
            raise ValueError("You must provide a directory or filepaths")
        elif directory is not None and filepaths is not None:
            raise ValueError("Please provide only one of directory or filepaths")
        elif directory is not None:
            self._files = [
                (os.path.join(dirpath, filename), filename)
                for (dirpath, dirnames, filenames) in os.walk(directory)
                for filename in filenames
            ]
        elif filepaths is not None:
            self._files = [
                (filepath, os.path.basename(filepath)) for filepath in filepaths
            ]

    def run(self, environment: Environment):
        self.logger.info("Compression started...")
        os.makedirs(
            os.path.dirname(environment.config.get("compression_output_path")),
            exist_ok=True,
        )
        for filepath, filename in self._files:
            environment.get_compression_engine().compress(filepath, filename)
        self.logger.info("Compression completed")
