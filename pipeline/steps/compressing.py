import os

from ..base import Step, Environment


class Compressing(Step):
    def __init__(self):
        super().__init__()

    def run(self, environment: Environment):
        input_path = environment.config.get("template_output_path")
        filenames = next(os.walk(input_path))[2]
        self.logger.info("Compression started...")
        os.makedirs(
            os.path.dirname(environment.config.get("compression_output_path")),
            exist_ok=True,
        )
        for filename in filenames:
            filepath = os.path.join(input_path, filename)
            environment.get_compression_engine().compress(filepath, filename)
        self.logger.info("Compression completed")
