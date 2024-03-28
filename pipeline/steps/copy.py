from ..base import Step, Environment


class Copy(Step):
    def run(self, environment: Environment):
        self.logger.info("This is a copy step")
