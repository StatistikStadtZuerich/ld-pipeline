from abc import ABC
from typing import List

from pipeline.base import Environment
from pipeline.steps.ldview import View


class LdViewBuilder(ABC):

    def __init__(self, environment: Environment):
        self._environment = environment

    def build_all(self) -> List[View]:
        return []

    def build_single(self, view_id: str) -> View | None:
        return None
