import configparser
import os
from .copy import Copy
from .compressing import Compressing
from .build_termset_hierarchy import BuildTermsetHierarchy
from .copy_hdb_to_pipe_tables import CopyHDBToPipeTables
from .write_publication_stati_to_hdb import WritePublicationStatiToHDB

config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.ini")
config = configparser.ConfigParser()
config.read(os.path.join(config_path))

if config.getboolean("DEFAULT", "optimized"):
    from .templating_optimized import TemplatingOptimized as Templating
    from .upload_to_stardog_optimized import UploadToStardogOptimized as UploadToStardog
    from .upload_to_fuseki_optimized import UploadToFusekiOptimized as UploadToFuseki
else:
    from .templating import Templating
    from .upload_to_stardog import UploadToStardog
    from .upload_to_fuseki import UploadToFuseki

__all__ = [
    "Copy",
    "Templating",
    "Compressing",
    "UploadToStardog",
    "UploadToFuseki",
    "BuildTermsetHierarchy",
    "CopyHDBToPipeTables",
    "WritePublicationStatiToHDB"
]
