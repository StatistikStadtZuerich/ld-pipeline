import os

from .ld_view_model import View
from ...base import Environment


class LdViewSerializer:
    def __init__(self, environment: Environment):
        self._environment = environment

    def _templater(self, template: str):
        return self._environment.get_template_engine(template, None)

    def serialize(self, view: View):
        out = os.path.join(
            self._environment.config.get("template_output_path"), "ldviews", f"view.{view.id}.ttl"
        )
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wt") as ttl_file:
            # serialize base
            with self._templater("ldviews/metadata.ttl.jinja") as engine:
                ttl_file.write(engine.render({"view": view}) + "\n")

            with self._templater("ldviews/filters.ttl.jinja") as engine:
                ttl_file.write(engine.render({"id": view.id, "filters": view.filters}) + "\n")

            with self._templater("ldviews/sources.ttl.jinja") as engine:
                ttl_file.write(engine.render({"id": view.id, "sources": view.get_sources()}) + "\n")

            with self._templater("ldviews/dimensions.ttl.jinja") as engine:
                ttl_file.write(engine.render({"id": view.id, "dimensions": view.dimensions}) + "\n")

            projected_dimensions = list(
                filter(lambda d: d.column is not None, view.dimensions)
            )
            projected_dimensions.sort(key=lambda x: x.column.position)

            attributes = [dimension.column for dimension in projected_dimensions]
            projected_bnodes = [
                dimension.to_bnode(view.id) for dimension in projected_dimensions
            ]

            with self._templater("ldviews/projection.ttl.jinja") as engine:
                ttl_file.write(engine.render(
                    {
                        "id": view.id,
                        "attributes": attributes,
                        "projected_bnodes": projected_bnodes,
                    }
                ) + "\n")
