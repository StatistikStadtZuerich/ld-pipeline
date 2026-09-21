import os
from typing import Any

from pipeline.base import Environment, Step, Utils
from pipeline.steps.ldview import LdViewBuilder, LdViewSerializer
from pipeline.steps.templating import OutputType


class ViewsStep(Step):
    def __init__(self, options: dict[str, Any] | None = None):
        super().__init__()
        self._utils = Utils()
        self._options = options or {}

    def run(self, environment: Environment):
        view_ids = self._options.get("view_ids")
        output_path = environment.config.get("template_output_path")
        if view_ids:
            # Fast-View: nie in den öffentlichen Ordner schreiben, den das
            # create_fuseki_index.sh für den öffentlichen Index einliest.
            output_path = os.path.join(output_path, OutputType.PREVIEW.value)
        else:
            output_path = os.path.join(output_path, OutputType.SHARED.value)
        serializer = LdViewSerializer(environment, output_path)

        self.logger.info("Start building ld-views")

        for view in LdViewBuilder(environment).build_all(view_ids=view_ids):
            self.logger.info(f"Start building ld-view {view.id}")
            serializer.serialize(view)
            self.logger.info(f"Written ld-view {view.id}")
