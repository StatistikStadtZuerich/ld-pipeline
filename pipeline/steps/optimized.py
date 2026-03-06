from typing import Dict, Any

from pipeline.base import Environment, Step
from .templating import Templating
from .templating_optimized import TemplatingOptimized
from .upload_to_fuseki import UploadToFuseki
from .upload_to_fuseki_optimized import UploadToFusekiOptimized


def _is_optimized(environment: Environment) -> bool:
    return environment.config.get("optimized", bool, False)


def create_templating(
    environment: Environment,
    template_filename: str,
    output_filename: str,
    sql_filepath: str,
    options: Dict[str, Any],
) -> Step:
    if _is_optimized(environment):
        return TemplatingOptimized(
            template_filename, output_filename, sql_filepath, options
        )
    else:
        return Templating(template_filename, output_filename, sql_filepath, options)


def create_fuseki_uploader(environment: Environment) -> Step:
    if _is_optimized(environment):
        return UploadToFusekiOptimized()
    else:
        return UploadToFuseki()
