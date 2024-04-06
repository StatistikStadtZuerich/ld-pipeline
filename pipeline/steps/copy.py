from ..base import Step, Environment


class Copy(Step):
    """
    A simple step that logs a line, noting else
    """
    def run(self, environment: Environment):
        """
        TODO just a simple stub
        """
        self.logger.info("Start a copy step")

        with (environment.get_db_connection()) as db:
            self.logger.info(db.query("Query something"))

        self.logger.info("End a copy step")
