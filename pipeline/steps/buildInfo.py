import os
import tempfile
from datetime import datetime, timezone

from ..base import Environment
from .copy import Copy


class BuildInfo(Copy):
    def __init__(self, options={}):
        """
        Adds build information to output
        """
        super().__init__(source=None, target="info.ttl", options=options)

    def run(self, environment: Environment):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        content = f'<https://ld.stadt-zuerich.ch/.well-known/void> <http://purl.org/dc/terms/created> "{now}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n'

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as tmp:
            tmp.write(content)
            self._source = tmp.name

        try:
            super().run(environment)
        finally:
            os.unlink(self._source)
