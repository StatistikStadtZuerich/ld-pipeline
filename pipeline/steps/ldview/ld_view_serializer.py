import gzip
import os

from ...base import Environment
from .ld_view_model import View


class LdViewSerializer:
    def __init__(self, environment: Environment, output_path: str):
        self._environment = environment
        self._output_path = output_path

    def _templater(self, template: str):
        return self._environment.get_template_engine(template, None)

    def serialize(self, view: View):
        out = os.path.join(
            self._output_path,
            f"ldview_{view.id}.ttl.gz",
        )
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with gzip.open(out, "wt") as ttl_file:
            # serialize base
            with self._templater("ldviews/metadata.ttl.jinja") as engine:
                ttl_file.write(engine.render({"view": view}) + "\n")

            with self._templater("ldviews/filters.ttl.jinja") as engine:
                ttl_file.write(
                    engine.render({"id": view.id, "filters": view.filters}) + "\n"
                )

            with self._templater("ldviews/sources.ttl.jinja") as engine:
                ttl_file.write(
                    engine.render({"id": view.id, "sources": view.get_sources()}) + "\n"
                )

            with self._templater("ldviews/dimensions.ttl.jinja") as engine:
                ttl_file.write(
                    engine.render({"id": view.id, "dimensions": view.dimensions}) + "\n"
                )

            projected_dimensions = list(
                filter(lambda d: d.column is not None, view.dimensions)
            )
            projected_dimensions.sort(key=lambda x: x.column.position)

            attributes = [dimension.column for dimension in projected_dimensions]
            projected_bnodes = [
                dimension.to_bnode(view.id) for dimension in projected_dimensions
            ]

            with self._templater("ldviews/projection.ttl.jinja") as engine:
                ttl_file.write(
                    engine.render(
                        {
                            "id": view.id,
                            "attributes": attributes,
                            "projected_bnodes": projected_bnodes,
                        }
                    )
                    + "\n"
                )
