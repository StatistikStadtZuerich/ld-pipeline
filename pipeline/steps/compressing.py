import os
from alive_progress import alive_bar

from ..base import Step, Environment


class Compressing(Step):
    def __init__(self):
        super().__init__()

    def run(self, environment: Environment):
        input_path = environment.config.get("template_output_path")
        filenames = next(os.walk(input_path))[2]
        self.logger.info("Started compression...")
        os.makedirs(
            os.path.dirname(environment.config.get("compression_output_path")),
            exist_ok=True,
        )
        for filename in filenames:
            filepath = os.path.join(input_path, filename)
            with alive_bar(
                spinner="dots",
                bar=None,
                stats=None,
                elapsed="({elapsed})",
                monitor=None,
                title=f"Compressing {filepath}",
                receipt=False,
                enrich_print=False,
            ):
                environment.get_compression_engine().compress(filepath, filename)
        self.logger.info("Compression completed")
