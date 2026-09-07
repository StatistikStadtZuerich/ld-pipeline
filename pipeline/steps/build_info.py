import os
import tempfile
from datetime import datetime, timezone

from .templating import OutputType
from ..base import Environment
from .copy import Copy


class BuildInfo(Copy):
    def __init__(self,
                 output_type: OutputType = OutputType.SHARED,
                 options=None):
        """
        Adds build information to output
        """
        super().__init__(source=None, target="info.ttl", output_type=output_type, options=options)

    def run(self, environment: Environment):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        content = f'<https://ld.stadt-zuerich.ch/.well-known/void> <http://purl.org/dc/terms/created> "{now}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n'

        with tempfile.NamedTemporaryFile(mode="wt", prefix="info", suffix=".ttl", delete=False) as tmp:
            tmp.write(content)
            self._source = tmp.name

        try:
            super().run(environment)
        finally:
            os.unlink(self._source)
