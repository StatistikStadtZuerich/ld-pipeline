from .copy import Copy
from .templating import Templating
from .compressing import Compressing
from .upload_to_stardog import UploadToStardog
from .upload_to_fuseki import UploadToFuseki

__all__ = [
    "Copy",
    "Templating",
    "Compressing",
    "UploadToStardog",
    "UploadToFuseki",
]
