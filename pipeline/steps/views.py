from pipeline.base import Step, Environment
from pipeline.steps.ldview import LdViewBuilder, LdViewSerializer


class ViewsStep(Step):
    def __init__(self):
        super().__init__()

    def run(self, environment: Environment):
        serializer = LdViewSerializer(environment)

        self.logger.info("Start building ld-views")

        for view in LdViewBuilder(environment).build_all():
            self.logger.info(f"Start building ld-view {view.id}")
            serializer.serialize(view)
            self.logger.info(f"Written ld-view {view.id}")
