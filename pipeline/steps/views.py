from pipeline.base import Environment, Step, Utils
from pipeline.steps.ldview import LdViewBuilder, LdViewSerializer


class ViewsStep(Step):
    def __init__(self):
        super().__init__()
        self._utils = Utils()

    def run(self, environment: Environment):
        serializer = LdViewSerializer(
            environment, environment.config.get("template_output_path")
        )

        self.logger.info("Start building ld-views")

        for view in LdViewBuilder(environment).build_all():
            self.logger.info(f"Start building ld-view {view.id}")
            serializer.serialize(view)
            self.logger.info(f"Written ld-view {view.id}")
