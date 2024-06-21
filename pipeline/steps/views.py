from pipeline.base import Step, Environment, Utils
from pipeline.steps.ldview import LdViewBuilder, LdViewSerializer


class ViewsStep(Step):
    def __init__(self, env):
        super().__init__()
        self._utils = Utils()
        self._env = env

    def run(self, environment: Environment):
        serializer = LdViewSerializer(environment)
        
        self._utils.print_formatted("Start building ld-views")

        for view in LdViewBuilder(environment, self._env).build_all():
            self._utils.print_formatted(f"Start building ld-view {view.id}")
            serializer.serialize(view)
            self._utils.print_formatted(f"Written ld-view {view.id}")
