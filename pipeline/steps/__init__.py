from .copy import Copy
from .templating_optimized import TemplatingOptimized as Templating
from .compressing import Compressing
from .upload_to_stardog_optimized import UploadToStardogOptimized as UploadToStardog
from .upload_to_fuseki_optimized import UploadToFusekiOptimized as UploadToFuseki

__all__ = [
    "Copy",
    "Templating",
    "Compressing",
    "UploadToStardog",
    "UploadToFuseki",
]
