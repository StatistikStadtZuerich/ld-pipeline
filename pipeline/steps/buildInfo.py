import os
from datetime import datetime, timezone

from ..base import Step, Environment


class BuildInfo(Step):
    def __init__(self, options={}):
        """
        Adds build information to output
        """
        super().__init__()
        self._options = options

    def run(self, environment: Environment):
        out_dir = environment.config.get("output_path")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "info.n3")

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        with open(out_file, "w") as f:
            f.write(
                f'<https://ld.stadt-zuerich.ch/.well-known/void> <http://purl.org/dc/terms/created> "{now}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n'
            )
