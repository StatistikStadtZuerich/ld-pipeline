import os
from abc import ABC

from ...base import Environment
from .ld_view_model import View


class LdViewSerializer(ABC):
    def __init__(self, environment: Environment):
        self._environment = environment

    def _templater(self, template: str, filename: str):
        out = os.path.join(
            self._environment.config.get("template_output_path"), "ldviews", filename
        )
        return self._environment.get_template_engine(template, out)

    def serialize(self, view: View):
        # serialize base
        with self._templater(
            "ldviews/metadata.ttl.jinja", f"view.{view.id}.ttl"
        ) as engine:
            engine.template({"view": view})

        with self._templater(
            "ldviews/filters.ttl.jinja", f"view.{view.id}.ttl"
        ) as engine:
            engine.template({"id": view.id, "filters": view.filters})

        with self._templater(
            "ldviews/sources.ttl.jinja", f"view.{view.id}.ttl"
        ) as engine:
            engine.template({"id": view.id, "sources": view.get_sources()})

        with self._templater(
            "ldviews/dimensions.ttl.jinja", f"view.{view.id}.ttl"
        ) as engine:
            engine.template({"id": view.id, "dimensions": view.dimensions})

        projected_dimensions = list(
            filter(lambda d: d.column is not None, view.dimensions)
        )
        projected_dimensions.sort(key=lambda x: x.column.position)

        attributes = [dimension.column for dimension in projected_dimensions]
        projected_bnodes = [dimension.to_bnode() for dimension in projected_dimensions]

        with self._templater(
            "ldviews/projection.ttl.jinja", f"view.{view.id}.ttl"
        ) as engine:
            engine.template(
                {
                    "id": view.id,
                    "attributes": attributes,
                    "projected_bnodes": projected_bnodes,
                }
            )
