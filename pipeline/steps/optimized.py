from typing import Dict, Any

from pipeline.base import Environment, Step
from .templating import Templating
from .templating_optimized import TemplatingOptimized, GroupedTemplatingOptimized
from .upload_to_fuseki import UploadToFuseki
from .upload_to_fuseki_optimized import UploadToFusekiOptimized


def _is_optimized(environment: Environment) -> bool:
    return environment.config.get("optimized", bool, False)


def create_templating(
    environment: Environment,
    template_filename: str,
    output_filename: str,
    view_or_table_name: str,
    sql_filepath: str | None = None,
    options: Dict[str, Any] | None = None,
) -> Step:
    options = options or {}

    if options.get("grouped", False):
        return GroupedTemplatingOptimized(
            template_filename,
            output_filename,
            view_or_table_name,
            sql_filepath,
            options,
        )
    elif _is_optimized(environment):
        return TemplatingOptimized(
            template_filename,
            output_filename,
            view_or_table_name,
            sql_filepath,
            options,
        )
    else:
        return Templating(
            template_filename,
            output_filename,
            view_or_table_name,
            sql_filepath,
            options,
        )


def create_fuseki_uploader(environment: Environment) -> Step:
    if _is_optimized(environment):
        return UploadToFusekiOptimized()
    else:
        return UploadToFuseki()
